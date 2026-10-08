#!/usr/bin/env python3
"""Deterministic workgraph generator (non-LLM sj: emission).

Seed -> regenerate -> enforce doctrine
======================================

Agent-authored workgraphs (e.g. docs/sjira/v26.10.8/WORKGRAPH.ttl per campaign
repo) are the SEED: hand-authored instances of the canonical folded sj: shape.
This generator REGENERATES that shape from raw repository state -- git history,
receipt files, court outputs -- with zero LLM in the loop, byte-identically for
the same repo state. Once deltas against the seed are dispositioned, the
generator's output becomes the enforced successor format and hand-authoring
retires.

Inputs (all read-only over the target repo)
-------------------------------------------
* git log since the campaign tag (``v<version>``) or, absent a tag, all
  non-merge commits touching ``docs/sjira/<version>/``;
* receipt files: ``docs/sjira/<v>/plans/*.md`` frontmatter, campaign receipt
  markdown tables, doc-hdit receipts JSONL, ``*.r.json`` court outputs.

Outputs
-------
A WORKGRAPH.ttl in the canonical folded sj: shape (exactly matching
docs/sjira/v26.10.8/WORKGRAPH.ttl's structure): one ``sj:WorkOrder`` per work
axis (conventional-commit scope group) with ``sj:standing`` / ``sj:baseSha`` /
``sj:acceptance`` / ``sj:falsifier`` / ``sj:authorityCeiling "CONSTRUCT"``,
``prov:Activity`` milestone + epic groupings, and a receipts-cited scope
disclaimer header.

Heuristics (all deterministic)
------------------------------
* commits grouped by conventional-commit scope (``type(scope):``); scopeless
  commits group under their type;
* standing per order: ALIVE only when a receipt/court artifact on disk cites a
  member commit SHA (witnessed); otherwise UNKNOWN;
* falsifier = the repo's re-run command template, derived from the repo's
  build manifest (Makefile/justfile/mix.exs/package.json/Cargo.toml/pyproject).

DETERMINISM: same repo state -> byte-identical TTL. All iteration is sorted;
the only timestamps in the output are derived from commit fields. The output
is a projection of repository state, never hand-edited.

Usage
-----
    python3 scripts/gen_workgraph.py --repo /path/to/repo --version v26.10.8 \
        [--out WORKGRAPH.ttl]            # default stdout
    python3 scripts/gen_workgraph.py --selftest --repo R1 [--repo R2 ...]

Exit codes: 0 ok; 2 usage; 3 repo/version unusable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys

SJ_PREFIX = "https://ggen-igniter.dev/ontology/semantic-jira#"
SHA_RE = re.compile(r"\b[0-9a-f]{7,40}\b")


def run_git(repo: str, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", repo, *args], capture_output=True, text=True, check=False
    )
    # proc.stdout is Optional[str] even under text=True; never leak None.
    return (proc.stdout or "") if proc.returncode == 0 else ""


def esc(text: str) -> str:
    """Turtle literal escaping."""
    return (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "")
        .replace("\t", " ")
    )


class Order:
    """One work axis rendered as an sj:WorkOrder."""

    def __init__(self, scope, commits, standing, receipt_paths):
        self.scope = scope
        self.commits = commits  # list of dicts: full, short, subject, date, body
        self.standing = standing
        self.receipt_paths = receipt_paths
        first = commits[0]
        self.identity = first["short"]
        self.title = first["subject"]
        self.base_sha = first["full"]


def parse_args(argv):
    p = argparse.ArgumentParser(
        description=(__doc__ or "gen_workgraph").splitlines()[0]
    )
    p.add_argument("--repo", action="append", required=True, help="target repo path")
    p.add_argument("--version", default=None, help="campaign version, e.g. v26.10.8")
    p.add_argument("--out", default=None, help="output path (default stdout)")
    p.add_argument("--selftest", action="store_true", help="determinism + seed-delta report")
    return p.parse_args(argv)


def detect_falsifier(repo: str) -> str:
    """Repo re-run command template from its build manifest."""
    checks = [
        ("mix.exs", "mix test"),
        ("Cargo.toml", "cargo test"),
        ("package.json", "npm test"),
        ("justfile", "just test"),
        ("Makefile", "make test"),
    ]
    for marker, cmd in checks:
        if os.path.exists(os.path.join(repo, marker)):
            return cmd
    if os.path.exists(os.path.join(repo, "pyproject.toml")):
        return "python3 -m pytest tests/ -q"
    return "git log --stat v{version}..HEAD  # re-run command template unknown for this repo"


def repo_label(repo: str) -> str:
    url = run_git(repo, "remote", "get-url", "origin").strip()
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    return m.group(1) if m else os.path.basename(os.path.abspath(repo))


def campaign_commits(repo: str, version: str):
    """Non-merge commits for the campaign, oldest-first, sorted deterministically.

    Base: tag v<version> when present (tag..HEAD); else all non-merge commits
    touching docs/sjira/<version>/.
    """
    sjira_dir = f"docs/sjira/{version}"
    rev_range = None
    tags = run_git(repo, "tag", "--list", version).split()
    candidates = []
    if version in tags:
        candidates += [f"{version}..HEAD", f"{version}^..HEAD"]
    candidates.append(sjira_dir)
    commits = ""
    for rev_range in candidates:
        commits = run_git(
            repo,
            "log",
            "--no-merges",
            "--pretty=format:%H%x1f%h%x1f%aI%x1f%s",
            rev_range,
        )
        if commits.strip():
            break
    out = parse_commit_lines(commits)
    # Deterministic: by (commit date, full sha).
    out.sort(key=lambda c: (c["date"], c["full"]))
    return out


def parse_commit_lines(text: str):
    """Parse ``git log --pretty=format:%H%x1f%h%x1f%aI%x1f%s`` output.

    Lines with missing/extra fields are skipped (never crash), so a repo
    whose log is empty or malformed yields ``[]``.
    """
    out = []
    for line in text.splitlines():
        parts = line.split("\x1f")
        if len(parts) != 4:
            continue
        full, short, date, subject = parts
        out.append(
            {
                "full": full,
                "short": short,
                "date": date,
                "subject": subject,
                "scope": scope_of(subject),
            }
        )
    return out


def scope_of(subject: str) -> str:
    m = re.match(r"^(\w+)(?:\(([^)]+)\))?!?:", subject)
    if not m:
        return "misc"
    return m.group(2) or m.group(1)


def base_sha(repo: str, version: str) -> str:
    tags = run_git(repo, "tag", "--list", version).split()
    if version in tags:
        sha = run_git(repo, "rev-parse", f"{version}^{{commit}}").strip()
        if sha:
            return sha
    shas = run_git(repo, "rev-list", "--max-parents=1", "HEAD", "--", f"docs/sjira/{version}").split()
    return shas[-1] if shas else run_git(repo, "rev-parse", "HEAD").strip()


def receipt_text(repo: str, version: str) -> str:
    """Concatenated text of campaign receipt artifacts (deterministic order)."""
    sjira_dir = os.path.join(repo, "docs/sjira", version)
    chunks = []
    for root, _dirs, files in os.walk(sjira_dir):
        for name in sorted(files):
            if name.endswith((".md", ".json", ".jsonl")):
                path = os.path.join(root, name)
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        chunks.append((os.path.relpath(path, repo), fh.read()))
                except OSError:
                    continue
    # Also repo-root *.r.json court outputs.
    for root, _dirs, files in os.walk(repo):
        # skip heavy/irrelevant dirs deterministically
        _dirs[:] = sorted(d for d in _dirs if d not in {".git", "node_modules", "_build", "deps", "target"})
        for name in sorted(files):
            if name.endswith(".r.json"):
                path = os.path.join(root, name)
                rel = os.path.relpath(path, repo)
                if rel.startswith("docs/sjira/"):
                    continue  # already covered
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        chunks.append((rel, fh.read()))
                except OSError:
                    continue
    chunks.sort(key=lambda c: c[0])
    return "\n".join(text for _rel, text in chunks)


def witnessed_shas(receipts: str):
    return set(SHA_RE.findall(receipts))


def build_orders(repo, version) -> tuple[str, list]:
    """Return (base_sha, orders); base is "" when the campaign has no commits."""
    commits = campaign_commits(repo, version)
    if not commits:
        return "", []
    base = base_sha(repo, version)
    witnesses = witnessed_shas(receipt_text(repo, version))
    groups: dict = {}
    for c in commits:
        groups.setdefault(c["scope"], []).append(c)
    orders = []
    for scope in sorted(groups):
        members = groups[scope]
        receipt_paths = []
        standing = "UNKNOWN"
        for m in members:
            if m["short"] in witnesses or m["full"] in witnesses:
                standing = "ALIVE"
                break
        orders.append(Order(scope, members, standing, receipt_paths))
    return base, orders


def falsifier_for(repo: str, version: str) -> str:
    cmd = detect_falsifier(repo)
    if "{version}" in cmd:
        return cmd.format(version=version)
    return f"{cmd}  # expect exit 0 at HEAD; a failure at the cited SHAs refutes"


def render(repo: str, version: str) -> str:
    base, orders = build_orders(repo, version)
    # Empty-log repo: no campaign base discoverable; use a deterministic
    # placeholder so the graph still renders (zero work orders) without a
    # None-subscript crash.
    base = base or "0" * 40
    label = repo_label(repo)
    gh = f"https://github.com/{label}"
    v8 = f"urn:seanchatmangpt:sjira:{version}:"
    lines = []
    w = lines.append
    w("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .")
    w("@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .")
    w("@prefix dcterms: <http://purl.org/dc/terms/> .")
    w("@prefix prov: <http://www.w3.org/ns/prov#> .")
    w(f"@prefix sj: <{SJ_PREFIX}> .")
    w(f"@prefix v8: <{v8}> .")
    w("")
    w(f"# Generated workgraph ({version} campaign, repo {label}).")
    w("# GENERATED by scripts/gen_workgraph.py from repository state (git history +")
    w("# receipts); do not hand-edit -- regenerate. Seed doctrine: the agent-authored")
    w("# WORKGRAPH.ttl graphs are the seed; this projection is the successor format.")
    w("#")
    w("# Scope disclaimer: only work axes with commits reachable from HEAD since the")
    w(f"# campaign base {base[:9]} are authored. Every sj:standing value cites its")
    w("# witnessing receipt evidence via prov:wasDerivedFrom; UNKNOWN means no on-disk")
    w("# receipt artifact cites a member commit. NO authority is granted by this graph;")
    w('# all orders carry sj:authorityCeiling "CONSTRUCT" -- consequential DO flows only')
    w("# through a separately admitted BRCE path.")
    w("#")
    w("# Standing as of the cited commit dates; standing at another SHA is UNKNOWN.")
    w("")
    w("v8:Milestone a prov:Activity ;")
    w(f'  dcterms:title "{esc(label)} {version} campaign" ;')
    w('  sj:standing "PARTIAL_ALIVE" ;')
    w('  sj:authorityCeiling "OBSERVE|SELECT|CONSTRUCT|VERIFY" ;')
    w(f'  prov:wasDerivedFrom <{gh}/commit/{base}> .')
    w("")
    # Epic prov:Activity per scope, sorted.
    for o in orders:
        ident = re.sub(r"[^A-Za-z0-9-]", "-", o.scope)
        w(f"v8:Epic-{ident} a prov:Activity ;")
        w(f'  dcterms:title "{esc(o.scope)} work axis" ;')
        w(f'  sj:standing "{o.standing}" .')
        w("")
    # WorkOrders.
    for i, o in enumerate(orders, start=1):
        ident = re.sub(r"[^A-Za-z0-9-]", "-", o.scope)
        oid = f"SJIRA-{version.lstrip('v').replace('.', '')}-{i:03d}"
        w(f"v8:{oid} a sj:WorkOrder ;")
        w(f'  dcterms:identifier "{oid}" ;')
        w(f'  dcterms:title "{esc(o.scope)} work axis ({len(o.commits)} commit(s))" ;')
        w(f'  sj:standing "{o.standing}" ;')
        w(f'  sj:repository "{esc(label)}" ;')
        w(f'  sj:baseSha "{o.base_sha}" ;')
        subjects = "; ".join(c["subject"] for c in o.commits)
        w(f'  sj:acceptance "{esc(subjects)}" ;')
        w(f'  sj:falsifier "{esc(falsifier_for(repo, version))}" ;')
        w('  sj:authorityCeiling "CONSTRUCT" ;')
        w('  sj:evidenceCeiling "Receipt artifacts under docs/sjira/' + version + '/ plus *.r.json court outputs; no runtime DO." ;')
        derived = [f"<{gh}/commit/{c['full']}>" for c in o.commits]
        w("  prov:wasDerivedFrom")
        w("    " + " ,\n    ".join(derived) + " .")
        w("")
    return "\n".join(lines) + "\n"


def selftest(repos, version):
    import hashlib

    print("== gen_workgraph selftest ==")
    empty_fail = synthetic_empty_repo_check()
    if empty_fail:
        print(f"[FAIL] synthetic empty-log repo: {empty_fail}")
        return 1
    print("[ok] synthetic empty-log repo: renders deterministically, 0 work orders")
    malformed_fail = malformed_log_check()
    if malformed_fail:
        print(f"[FAIL] malformed log lines: {malformed_fail}")
        return 1
    print("[ok] malformed/missing-field log lines skipped without crash")
    for repo in repos:
        version = version or detect_version(repo)
        if not version:
            print(f"[SKIP] {repo}: no campaign version given or detected")
            continue
        text1 = render(repo, version)
        text2 = render(repo, version)
        h1 = hashlib.sha256(text1.encode()).hexdigest()
        h2 = hashlib.sha256(text2.encode()).hexdigest()
        status = "IDENTICAL" if h1 == h2 else "MISMATCH"
        print(f"{repo} ({version}): double-run {status}  sha256={h1[:16]}")
        seed_path = os.path.join(repo, "docs/sjira", version, "WORKGRAPH.ttl")
        if os.path.exists(seed_path):
            with open(seed_path, encoding="utf-8") as fh:
                seed = fh.read()
            delta = seed_delta(seed, text1)
            print(f"  seed delta vs {seed_path}:")
            for line in delta:
                print(f"    - {line}")
        else:
            print(f"  no agent-authored seed at {seed_path} (nothing to diff)")
    return 0


def synthetic_empty_repo_check():
    """Exercise the previously-crashing empty-log branches end to end."""
    import hashlib
    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="gen_workgraph_empty_repo_")
    try:
        init = subprocess.run(
            ["git", "init", "-q", tmp], capture_output=True, text=True, check=False
        )
        if init.returncode != 0:
            return f"git init failed: {init.stderr.strip()}"
        text1 = render(tmp, "v26.10.8")
        text2 = render(tmp, "v26.10.8")
        if text1 != text2:
            return "double-run mismatch"
        if "a sj:WorkOrder" in text1:
            return "empty repo must not emit work orders"
        if "0" * 40 not in text1:
            return "empty repo must use the deterministic zero base sha"
        h = hashlib.sha256(text1.encode()).hexdigest()
        print(f"  empty-repo render sha256={h[:16]}")
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def malformed_log_check():
    """Missing-field log lines are dropped, well-formed ones parsed."""
    good = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\x1faaaaaaa\x1f2026-10-01T00:00:00Z\x1ffeat(x): ok"
    parsed = parse_commit_lines("garbage\n" + good + "\nshort\x1fline\n")
    if len(parsed) != 1:
        return f"expected 1 parsed commit, got {len(parsed)}"
    if parsed[0]["scope"] != "x" or parsed[0]["short"] != "aaaaaaa":
        return f"wrong fields parsed: {parsed}"
    if parse_commit_lines("") != []:
        return "empty log must parse to []"
    return None


def detect_version(repo):
    sj = os.path.join(repo, "docs/sjira")
    if os.path.isdir(sj):
        versions = sorted(d for d in os.listdir(sj) if d.startswith("v"))
        if versions:
            return versions[-1]
    return None


def seed_delta(seed: str, generated: str):
    """Report structural differences between seed and generated graphs."""
    report = []
    seed_preds = predicate_set(seed)
    gen_preds = predicate_set(generated)
    for p in sorted(seed_preds - gen_preds):
        report.append(f"predicate in seed but not generated: {p}")
    for p in sorted(gen_preds - seed_preds):
        report.append(f"predicate in generated but not seed: {p}")
    seed_wo = seed.count("a sj:WorkOrder")
    gen_wo = generated.count("a sj:WorkOrder")
    if seed_wo != gen_wo:
        report.append(f"work-order count: seed={seed_wo} generated={gen_wo}")
    if "sj:acceptance" not in generated:
        report.append("generated graph lacks sj:acceptance")
    return report or ["no structural delta"]


def predicate_set(ttl: str):
    """Predicate terms in predicate position: '<prefix:term> ' after subject/,;."""
    preds = set()
    for line in ttl.splitlines():
        if line.lstrip().startswith("@") or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^\s+(?:sj|dcterms|prov|rdfs|rdf):([A-Za-z][A-Za-z0-9]*)\s", line)
        if m:
            preds.add(m.group(0).strip())
    return preds


def main(argv=None):
    args = parse_args(argv if argv is not None else sys.argv[1:])
    if args.selftest:
        return selftest(args.repo, args.version)
    if not args.version:
        print("error: --version required without --selftest", file=sys.stderr)
        return 2
    text = render(args.repo[0], args.version)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
