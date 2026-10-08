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
        [--seed-commits seeds.json]      # v3 item 7: bind orders to the seed's
                                         # exact commits ({"<scope>": ["<sha>", ...], "_base": "<sha>"})
        [--seed-commits seeds.json]      # bind orders to the seed's exact commits
                                         # ({"<scope>": ["<sha>", ...], "_base": "<sha>"})
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

# The 15-class projection vocabulary, canonical in
# ggen_igniter:lib/ggen_igniter/semantic_jira.ex (@projection_types).
PROJECTION_TYPES = [
    "jira", "wbpr", "prd", "ard", "vision", "fond", "hddl", "sa2a",
    "a2a_agent_card", "worker", "verification", "executive", "machine",
    "receipt", "replay",
]

# Conventional-commit scope/type keyword -> projection type. First match per
# scope string wins; unmatched scopes keep the default {jira, receipt} floor.
SCOPE_ALIASES = [
    ("verification", ("test", "court", "verify", "ci", "gate")),
    ("hddl", ("hddl", "planning")),
    ("fond", ("fond", "pddl")),
    ("sa2a", ("sa2a",)),
    ("a2a_agent_card", ("a2a",)),
    ("worker", ("worker", "lane")),
    ("executive", ("executive", "status")),
    ("machine", ("machine", "telemetry", "ocel")),
    ("replay", ("replay",)),
    ("receipt", ("receipt", "ledger")),
    ("wbpr", ("wbpr", "working-backwards")),
    ("prd", ("prd", "requirements")),
    ("ard", ("ard", "architecture")),
    ("vision", ("vision",)),
    ("jira", ("jira", "ticket", "sjira", "doc")),
]

PROJECTION_META = {
    "jira": ("Jira/Markdown ticket", "Deterministic jira/markdown ticket projection; authority is NONE."),
    "wbpr": ("Working-backwards plan", "Deterministic working-backwards plan projection; authority is NONE."),
    "prd": ("Product requirements document", "Deterministic product requirements document projection; authority is NONE."),
    "ard": ("Architecture requirements document", "Deterministic architecture requirements document projection; authority is NONE."),
    "vision": ("Vision document", "Deterministic vision document projection; authority is NONE."),
    "fond": ("FOND planning projection", "Deterministic fond planning projection; authority is NONE."),
    "hddl": ("HDDL task/method projection", "Deterministic hddl task/method projection; authority is NONE."),
    "sa2a": ("SA2A work/execution package", "Deterministic sa2a work/execution package projection; authority is NONE."),
    "a2a_agent_card": ("A2A agent card", "Deterministic a2a agent card projection; authority is NONE."),
    "worker": ("Bounded worker input envelope", "Deterministic bounded worker input envelope projection; authority is NONE."),
    "verification": ("Verification plan", "Deterministic verification plan projection; authority is NONE."),
    "executive": ("Executive status view", "Deterministic executive status view projection; authority is NONE."),
    "machine": ("Machine status view", "Deterministic machine status view projection; authority is NONE."),
    "receipt": ("Receipt requirement summary", "Deterministic receipt requirement summary projection; authority is NONE."),
    "replay": ("Replay manifest", "Deterministic replay manifest projection; authority is NONE."),
}

EVIDENCE_FLOOR = [
    ("source-evidence", "Source evidence", "Exact canonical-source identity evidence."),
    ("local-execution-evidence", "Local execution evidence", "Observed repository-local exact-subject execution evidence."),
    ("receipt-evidence", "Receipt evidence", "Durable receipt evidence for the exact subject and transition."),
    ("replay-evidence", "Replay evidence", "Fresh replay over pack, dependency, graph, consequence, toolchain, and environment identities."),
]


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
        # Unfolded-emission extras (populated in build_orders).
        self.court_files: list = []      # court artifacts witnessing this order
        self.witnessed: list = []        # member SHAs cited by receipt artifacts
        self.dependencies: list = []     # SHAs from Fixes:/Refs: trailers
        self.projections: list = []      # projection types (15-class vocabulary)
        self.cross_refs: list = []       # v3 item 6: sibling-repo references
        self.files: list = []            # files touched by member commits (sorted)
        self.acceptance: list = []       # (index, description, witnessed_by)
        self.falsifiers: list = []       # (index, description)
        self.edges: list = []            # (upstream, dep_type)
        self.path_scope: list = []       # path-scope tokens (sorted, capped)

        # ---- v3 item 1: acceptance/falsifier items ------------------------
        # Witnessable seed: a receipt/court artifact on disk cites the member
        # SHA. Otherwise an UNKNOWN-honest placeholder (no invented verdict).
        for idx, c in enumerate(self.commits):
            witness_rel = self._witness_for(c)
            if witness_rel:
                self.acceptance.append(
                    (idx, f"commit {c['short']} lands: {c['subject']} "
                          f"(witnessed by {witness_rel})", witness_rel)
                )
                self.falsifiers.append(
                    (idx, f"the witnessing artifact {witness_rel} no longer "
                          f"cites {c['short']} (witness-set change refutes)")
                )
            else:
                self.acceptance.append(
                    (idx, f"commit {c['short']} lands: {c['subject']} "
                          f"(UNKNOWN: no on-disk receipt/court artifact "
                          f"witnesses this commit)", None)
                )
                self.falsifiers.append(
                    (idx, f"UNKNOWN: no on-disk receipt/court artifact "
                          f"witnesses {c['short']}; no falsifier command is "
                          f"available for this member commit")
                )

        # ---- v3 item 4: pathScope (computed in build_orders, after
        # self.files is populated) -----------------------------------------
        self.path_scope: list = []

    def _witness_for(self, c) -> str | None:
        for rel in self.receipt_paths:
            if rel in _COURT_PATH_CACHE.get(c["full"], []):
                return rel
        for rel in self.receipt_paths:
            text = _CHUNK_CACHE.get(rel)
            if text is not None and (c["short"] in text or c["full"] in text):
                return rel
        return None


def truncate(text: str, limit: int = 400) -> str:
    """Deterministic word-boundary truncation (never mid-token)."""
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + " ..."


def parse_args(argv):
    p = argparse.ArgumentParser(
        description=(__doc__ or "gen_workgraph").splitlines()[0]
    )
    p.add_argument("--repo", action="append", required=True, help="target repo path")
    p.add_argument("--version", default=None, help="campaign version, e.g. v26.10.8")
    p.add_argument("--out", default=None, help="output path (default stdout)")
    p.add_argument(
        "--seed-commits", default=None,
        help="JSON file binding orders to the seed's exact commits: "
             '{"<scope>": ["<sha>", ...], "_base": "<sha>"}',
    )
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


def campaign_commits(repo: str, version: str, want_range: bool = False):
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
            "--pretty=format:%x1e%H%x1f%h%x1f%aI%x1f%s%x1f%b",
            rev_range,
        )
        if commits.strip():
            break
    out = parse_commit_lines(commits)
    # Deterministic: by (commit date, full sha).
    out.sort(key=lambda c: (c["date"], c["full"]))
    if want_range:
        return out, rev_range
    return out


def parse_commit_lines(text: str):
    """Parse ``git log --pretty=format:%x1e%H%x1f%h%x1f%aI%x1f%s%x1f%b`` output.

    Records are separated by \\x1e (so multi-line bodies survive); each record
    must carry exactly 5 fields or it is skipped (never crash), so a repo
    whose log is empty or malformed yields ``[]``.
    """
    out = []
    for record in text.split("\x1e"):
        record = record.lstrip("\n")
        if not record.strip():
            continue
        parts = record.split("\x1f")
        if len(parts) != 5:
            continue
        full, short, date, subject, body = parts
        out.append(
            {
                "full": full,
                "short": short,
                "date": date,
                "subject": subject,
                "body": body.strip(),
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


def receipt_chunks(repo: str, version: str):
    """Campaign receipt artifacts as sorted (repo-relative path, text) pairs."""
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
    # Also repo-wide *.r.json court outputs and test-court artifacts
    # (test files matching *court*): v3 item 2 witness classes.
    for root, _dirs, files in os.walk(repo):
        # skip heavy/irrelevant dirs deterministically
        _dirs[:] = sorted(d for d in _dirs if d not in {".git", "node_modules", "_build", "deps", "target", "__pycache__"})
        for name in sorted(files):
            rel_probe = os.path.relpath(os.path.join(root, name), repo)
            is_rjson = name.endswith(".r.json")
            is_test_court = (
                "court" in name.lower()
                and any(part in {"test", "tests", "spec", "specs"} for part in rel_probe.split(os.sep)[:-1])
            )
            if is_rjson or is_test_court:
                path = os.path.join(root, name)
                rel = rel_probe
                if rel.startswith("docs/sjira/"):
                    continue  # already covered
                try:
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        chunks.append((rel, fh.read()))
                except OSError:
                    continue
    chunks.sort(key=lambda c: c[0])
    return chunks


def receipt_text(repo: str, version: str) -> str:
    """Concatenated text of campaign receipt artifacts (deterministic order)."""
    return "\n".join(text for _rel, text in receipt_chunks(repo, version))


def court_file_paths(chunks):
    """Receipt chunks that are court artifacts (name says court, or *.r.json)."""
    out = []
    for rel, _text in chunks:
        base = os.path.basename(rel)
        if "court" in base.lower() or base.endswith(".r.json"):
            out.append(rel)
    return sorted(out)


def witnessed_shas(receipts: str):
    return set(SHA_RE.findall(receipts))


TRAILER_RE = re.compile(r"^(?:Fixes|Refs|Closes|Resolves):\s*(.+)$", re.MULTILINE)

# Co-change edge threshold (v3 item 3): two axes sharing files in >= this many
# campaign commits get one sj:DependencyEdge with dependencyType "coChange".
CO_CHANGE_MIN = 3


def dependency_shas(commits):
    """SHAs cited by Fixes:/Refs:/Closes:/Resolves: trailers in commit bodies."""
    out = set()
    for c in commits:
        for trailer in TRAILER_RE.findall(c.get("body") or ""):
            for token in re.split(r"[,\s]+", trailer.strip()):
                if SHA_RE.fullmatch(token):
                    out.add(token)
    return sorted(out)

# Per-render caches (bounded to one render; populated in build_orders).
_CHUNK_CACHE: dict = {}
_COURT_PATH_CACHE: dict = {}


def commit_files_map(repo, commits, rev_range: str = "") -> dict:
    """full sha -> sorted list of changed paths (deterministic).

    Uses --no-walk over the exact commit SHAs: a pathspec would also filter
    the listed file paths, not just the selected commits.
    """
    if not commits:
        return {}
    text = run_git(
        repo,
        "log", "--no-merges", "--no-walk", "--name-only",
        "--pretty=format:%x1e%H",
        *[c["full"] for c in commits],
    )
    out: dict = {}
    cur = None
    for line in text.split("\n"):
        # split("\n"), NOT splitlines(): splitlines() also splits on the \x1e
        # record marker itself (it is a Unicode line boundary), which would
        # silently drop the SHA header lines.
        if line.startswith("\x1e"):
            cur = line[1:].strip()
            out.setdefault(cur, [])
            continue
        line = line.strip()
        if not line or cur is None:
            continue
        out[cur].append(line)
    for k in out:
        out[k] = sorted(set(out[k]))
    return {c["full"]: out.get(c["full"], []) for c in commits}


def projections_for(scope: str):
    """Map a conventional-commit scope/type to the 15-class projection set.

    Every order carries the {jira, receipt} floor; scope keywords widen it.
    Output order follows PROJECTION_TYPES (vocabulary-canonical).
    """
    low = scope.lower()
    extra = [
        ptype for ptype, aliases in SCOPE_ALIASES
        if any(a in low for a in aliases)
    ]
    chosen = {t for t in extra if t in PROJECTION_TYPES} | {"jira", "receipt"}
    return [t for t in PROJECTION_TYPES if t in chosen]


def build_orders(repo, version) -> tuple[str, list]:
    """Return (base_sha, orders); base is "" when the campaign has no commits."""
    commits, rev_range = campaign_commits(repo, version, want_range=True)
    if not commits:
        return "", []
    base = base_sha(repo, version)
    chunks = receipt_chunks(repo, version)
    courts = court_file_paths(chunks)
    witnesses = witnessed_shas(receipt_text(repo, version))
    # Per-render caches for Order._witness_for.
    _CHUNK_CACHE.clear()
    _COURT_PATH_CACHE.clear()
    for rel, text in chunks:
        _CHUNK_CACHE[rel] = text or ""
        for sha in witnessed_shas(text):
            _COURT_PATH_CACHE.setdefault(sha, []).append(rel)
    fmap = commit_files_map(repo, commits, rev_range)
    groups: dict = {}
    for c in commits:
        groups.setdefault(c["scope"], []).append(c)
    orders = []
    for scope in sorted(groups):
        members = groups[scope]
        # Receipt paths witnessing any member commit (deterministic, sorted).
        order_receipt_paths = []
        for rel, text in chunks:
            hits = witnessed_shas(text)
            if any(m["short"] in hits or m["full"] in hits for m in members):
                order_receipt_paths.append(rel)
        witnessed = [
            m["full"] for m in members
            if m["short"] in witnesses or m["full"] in witnesses
        ]
        order_courts = [rel for rel in courts if rel in order_receipt_paths]
        deps = dependency_shas(members)
        o = Order(scope, members, standing_for(witnessed), order_receipt_paths)
        o.court_files = order_courts
        o.witnessed = witnessed
        o.dependencies = deps
        o.projections = projections_for(scope)
        o.files = sorted({f for m in members for f in fmap.get(m["full"], [])})
        # v3 item 4: pathScope — first path component per touched file,
        # sorted, capped (deterministic bounded projection).
        comps = set()
        for f in o.files:
            comps.add(f.split("/", 1)[0] if "/" in f else f)
        o.path_scope = sorted(comps)[:12]
        # v3 item 6: sibling-repo references across the order's member commits.
        o.cross_refs = sorted({
            ref
            for m in members
            for ref in cross_repo_refs({"files": fmap.get(m["full"], []), "body": m.get("body")})
        })
        orders.append(o)
    # ---- v3 item 3: DependencyEdge chains -------------------------------
    # (a) trailer edges: cited SHAs resolve to the order owning the SHA
    # (requiresReceipt); unresolved SHAs stay as raw-SHA upstreams.
    sha_to_order = {}
    for o in orders:
        for m in o.commits:
            sha_to_order[m["full"]] = o
            sha_to_order[m["short"]] = o
    for o in orders:
        for sha in o.dependencies:
            target = sha_to_order.get(sha)
            if target is o:
                continue
            upstream = target.scope if target is not None else sha
            o.edges.append((upstream, "requiresReceipt"))
    # (b) co-change clustering: two axes whose member commits touch the same
    # file in >= CO_CHANGE_MIN campaign commits get one coChange edge
    # (lexically-later scope points at the lexically-earlier scope).
    for i, a in enumerate(orders):
        for b in orders[i + 1:]:
            shared_hits = sum(
                1 for c in commits
                if any(f in a.files for f in fmap.get(c["full"], []))
                and any(f in b.files for f in fmap.get(c["full"], []))
            )
            if shared_hits >= CO_CHANGE_MIN:
                later, earlier = (b, a) if b.scope > a.scope else (a, b)
                later.edges.append((earlier.scope, "coChange"))
    return base, orders


def standing_for(witnessed: list) -> str:
    """Conservative standing rule (unchanged): ALIVE only on receipt witness."""
    return "ALIVE" if witnessed else "UNKNOWN"


def court_node_id(oid: str, k: int) -> str:
    """Deterministic node id for the k-th court artifact of an order."""
    return f"v8:Court-{oid}-{k:02d}"


def falsifier_for(repo: str, version: str) -> str:
    cmd = detect_falsifier(repo)
    if "{version}" in cmd:
        return cmd.format(version=version)
    return f"{cmd}  # expect exit 0 at HEAD; a failure at the cited SHAs refutes"


def repo_manifest(repo):
    """The repo's build manifest filename, first match in fixed order."""
    for marker in ("mix.exs", "Cargo.toml", "package.json", "justfile", "Makefile"):
        if os.path.exists(os.path.join(repo, marker)):
            return marker
    if os.path.exists(os.path.join(repo, "pyproject.toml")):
        return "pyproject.toml"
    return None


def falsifier_for_order(repo, version, order) -> str:
    """v3 item 5: per-order re-run command, scope-targeted when a real target
    exists on disk (mix test <file> / cargo test -p <crate> / pytest
    tests/<scope>), falling back to the repo-wide template. Deterministic:
    target discovery is a fixed candidate list checked with os.path.exists."""
    scope = re.sub(r"[^A-Za-z0-9_-]", "-", order.scope.lower())
    def first_existing(*paths):
        for p in paths:
            if os.path.exists(os.path.join(repo, p)):
                return p
        return None
    manifest = repo_manifest(repo)
    if manifest == "mix.exs":
        target = first_existing(
            "test/%s_test.exs" % scope, "test/%s" % scope, "apps/%s/test" % scope
        )
        cmd = "mix test %s" % target if target else "mix test"
    elif manifest == "Cargo.toml":
        target = first_existing(
            "%s/Cargo.toml" % scope, "crates/%s/Cargo.toml" % scope
        )
        cmd = "cargo test -p %s" % order.scope if target else "cargo test"
    elif manifest == "pyproject.toml":
        target = first_existing("tests/%s" % scope, "tests/%s.py" % scope)
        cmd = (
            "python3 -m pytest %s -q" % target if target
            else "python3 -m pytest tests/ -q"
        )
    else:
        cmd = detect_falsifier(repo)
    if "{version}" in cmd:
        return cmd.format(version=version)
    if cmd.startswith("git log"):
        return cmd.format(version=version)
    return cmd + "  # expect exit 0 at HEAD; a failure at the cited SHAs refutes"


SIBLING_PATH_RE = re.compile(r"^vendor/([^/]+)/")
SIBLING_MENTION_RE = re.compile(r"~/([A-Za-z0-9][A-Za-z0-9._-]*)")


def cross_repo_refs(commit):
    """v3 item 6: sibling-repo references, deterministic only. A commit is
    cross-repo when it touches a vendored path (vendor/<sibling>/...) or its
    body mentions a sibling checkout (~/<sibling>...)."""
    refs = set()
    for p in commit.get("files") or ():
        m = SIBLING_PATH_RE.match(p)
        if m:
            refs.add(m.group(1))
    for name in SIBLING_MENTION_RE.findall(commit.get("body") or ""):
        refs.add(name)
    return sorted(refs)


def compress_acceptance(commits, limit=400):
    """v3 item 9: deterministic bounded phrasing of acceptance text. Subjects
    are '; '-joined; over the limit, the longest fitting subject prefix is kept
    and the remainder summarized as "(+N more commit(s))"."""
    subjects = [c["subject"] for c in commits]
    text = "; ".join(subjects)
    if len(text) <= limit:
        return text
    reserve = 32
    kept = []
    used = 0
    for s in subjects:
        add = len(s) + (2 if kept else 0)
        if used + add > limit - reserve:
            break
        kept.append(s)
        used += add
    if not kept:
        return truncate(text, limit)
    remaining = len(subjects) - len(kept)
    return "; ".join(kept) + " (+" + str(remaining) + " more commit(s))"


def render(repo: str, version: str, seed_commits: dict | None = None) -> str:
    base, orders = build_orders(repo, version)
    # v3 item 7: seed binding. An optional "_base" key overrides the discovered
    # base with the seed's exact base commit.
    seed_base = (seed_commits or {}).get("_base")
    if isinstance(seed_base, str) and re.fullmatch(r"[0-9a-f]{7,40}", seed_base):
        base = seed_base
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
    # EvidenceRequirement floor (unfolded shape, per the zcode seed).
    for ident, lbl, desc in EVIDENCE_FLOOR:
        w(f"sj:{ident} a sj:EvidenceRequirement ;")
        w(f'  rdfs:label "{esc(lbl)}" ;')
        w(f'  dcterms:description "{esc(desc)}" .')
        w("")
    # ProjectionSpec declarations: v3 item 8, the FULL projection catalog is
    # declared every render; per-order sj:projection still lists the scope
    # keyword's applicable classes over the {jira, receipt} floor.
    used_types = list(PROJECTION_TYPES)
    for ptype in used_types:
        plabel, pdesc = PROJECTION_META[ptype]
        w(f"sj:projection-{ptype} a sj:ProjectionSpec ;")
        w(f'  rdfs:label "{esc(plabel)}" ;')
        w(f'  dcterms:description "{esc(pdesc)}" ;')
        w(f'  sj:projectionType "{ptype}" ;')
        w(f'  sj:generatorIdentity "gen_workgraph@{version}" ;')
        w('  sj:authorityClaim "NONE" .')
        w("")
    # WorkOrders.
    for i, o in enumerate(orders, start=1):
        ident = re.sub(r"[^A-Za-z0-9-]", "-", o.scope)
        oid = f"SJIRA-{version.lstrip('v').replace('.', '')}-{i:03d}"
        w(f"v8:{oid} a sj:WorkOrder ;")
        w(f'  rdfs:label "{oid}: {esc(truncate(o.title, 120))}" ;')
        w(f'  dcterms:identifier "{oid}" ;')
        w(f'  dcterms:title "{esc(o.scope)} work axis ({len(o.commits)} commit(s))" ;')
        body_digest = truncate(
            " ".join(
                filter(None, ((c.get("body") or "").strip() for c in o.commits))
            )
            or f"Conventional-commit axis '{o.scope}': {len(o.commits)} commit(s).",
            400,
        )
        w(f'  dcterms:description "{esc(body_digest)}" ;')
        w(f'  sj:subject "{esc(label)}:{esc(o.scope)}@{o.identity}" ;')
        w(f'  sj:promotionRule "Standing may advance only from an independent exact-head court receipt binding this order member SHAs and a durable 5-field receipt." ;')
        w(f'  sj:standing "{o.standing}" ;')
        w(f'  sj:repository "{esc(label)}" ;')
        w(f'  sj:baseSha "{o.base_sha}" ;')
        # v3 item 7: seed-commits binding (landedCommit/subjectSha).
        landed = None
        if seed_commits and o.scope in seed_commits:
            raw = seed_commits[o.scope]
            if isinstance(raw, list):
                landed = [
                    s for s in raw
                    if isinstance(s, str) and re.fullmatch(r"[0-9a-f]{7,40}", s)
                ]
        if landed:
            for sha in sorted(landed):
                w('  sj:landedCommit "' + esc(sha) + '" ;')
            w('  sj:subjectSha "' + esc(sorted(landed)[0]) + '" ;')
        # v3 item 9: bounded acceptance phrasing.
        subjects = compress_acceptance(o.commits, 400)
        w(f'  sj:replayIdentity "{esc(label)}:{version}:{esc(o.scope)}" ;')
        w(f'  sj:acceptance "{esc(subjects)}" ;')
        # v3 item 5: per-order falsifier command.
        w(f'  sj:falsifier "{esc(falsifier_for_order(repo, version, o))}" ;')
        w('  sj:authorityCeiling "CONSTRUCT" ;')
        w('  sj:evidenceCeiling "Receipt artifacts under docs/sjira/' + version + '/ plus *.r.json court outputs; no runtime DO." ;')
        # v3 item 4: pathScope (bounded, sorted, deterministic).
        if o.path_scope:
            w("  sj:pathScope")
            w("    " + " ,\n    ".join(f'"{esc(p)}"' for p in o.path_scope) + " ;")
        # Unfolded emission: projections.
        if o.projections:
            w("  sj:projection")
            w("    " + " ,\n    ".join(f"sj:projection-{t}" for t in o.projections) + " ;")
        # Unfolded emission: court requirements (witnessed court files only).
        if o.court_files:
            w("  sj:requiresCourt")
            w("    " + " ,\n    ".join(
                court_node_id(oid, k) for k in range(len(o.court_files))
            ) + " ;")
        # v3 item 1: acceptance/falsifier items as folded blank nodes.
        for idx, desc, _witness in o.acceptance:
            w(f"  sj:acceptanceItem [ a sj:AcceptanceCriterion ; sj:index {idx} ;")
            w(f'    dcterms:description "{esc(desc)}" ] ;')
        for idx, desc in o.falsifiers:
            w(f"  sj:falsifierItem [ a sj:Falsifier ; sj:index {idx} ;")
            w(f'    dcterms:description "{esc(desc)}" ] ;')
        # Unfolded emission: receipt-path evidence requirements.
        for rel in o.receipt_paths:
            w(f'  sj:requiresEvidence "{esc(rel)}" ;')
        # Unfolded emission: receipt SHA citations (witness heuristic).
        for sha in o.witnessed:
            w(f'  sj:receipt "{sha}" ;')
        # Unfolded emission: dependency SHAs from trailers (kept as literals).
        for sha in o.dependencies:
            w(f'  sj:dependency "{esc(sha)}" ;')
        # v3 item 3: DependencyEdge blank nodes (trailer + co-change chains).
        # Predicate sj:dependency with sj:DependencyEdge node type, matching
        # the ash_affidavit seed shape.
        for upstream, dep_type in o.edges:
            w("  sj:dependency [ a sj:DependencyEdge ;")
            w(f'    sj:upstream "{esc(upstream)}" ; sj:dependencyType "{dep_type}" ] ;')
        # v3 item 6: cross-repo notes. sj:repository above stays the PRIMARY
        # repo; each sibling is emitted as a derived-from note entity.
        xrefs = [r for r in o.cross_refs if r != label]
        xrids = []
        for ref in xrefs:
            xr = "XRepo-" + ident + "-" + re.sub(r"[^A-Za-z0-9-]", "-", ref)
            xrids.append(xr)
            w("  sj:crossRepo v8:" + xr + " ;")
        # v3 item 4: nextCheckpoint forward link (zcode seed shape).
        w(f"  sj:nextCheckpoint v8:cp-{oid} ;")
        derived = [f"<{gh}/commit/{c['full']}>" for c in o.commits]
        w("  prov:wasDerivedFrom")
        w("    " + " ,\n    ".join(derived) + " .")
        for ref, xr in zip(xrefs, xrids):
            w("")
            w("v8:" + xr + " a prov:Entity ;")
            w('  rdfs:label "cross-repo reference: ' + esc(ref) + ' (V8-004 invalid_repository class)" ;')
            w('  sj:repository "' + esc(label) + '" ;')
            w("  prov:wasDerivedFrom <https://github.com/" + esc(ref) + "> .")
        # v3 item 4: checkpoint individual (order -> nextCheckpoint, checkpoint
        # -> checkpointOf back-link; conservative standing copied from order).
        w(f"v8:cp-{oid} a sj:Checkpoint ;")
        w(f'  rdfs:label "checkpoint: {esc(o.scope)} axis" ;')
        w(f"  sj:checkpointOf v8:{oid} ;")
        w(f'  sj:standing "{o.standing}" ;')
        w(f'  dcterms:description "{esc(f"checkpoint after {len(o.commits)} commit(s) on the {o.scope} axis; standing inherited from the order, never asserted")}" .')
        # v3 item 2: sj:Court individuals from witnessed court artifacts.
        for k, rel in enumerate(o.court_files):
            w("")
            w(f"{court_node_id(oid, k)} a sj:Court ;")
            w(f'  rdfs:label "court: {esc(os.path.basename(rel))}" ;')
            w(f'  dcterms:description "{esc(truncate(f"Court artifact {rel} witnesses member commit(s) of order {oid}.", 400))}" ;')
            w(f'  sj:repository "{esc(label)}" ;')
            w(f'  sj:baseSha "{o.base_sha}" ;')
            w(f'  sj:standing "{o.standing}" ;')
            w("  prov:wasDerivedFrom")
            w(f"    <{gh}/blob/main/{rel}> .")
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
    v3_fail = v3_fixture_check()
    if v3_fail:
        print(f"[FAIL] v3 fixture (items 1-4): {v3_fail}")
        return 1
    print("[ok] v3 fixture: acceptance/falsifier nodes, courts, dependency "
          "chains, pathScope/replayIdentity/checkpoint all emitted")
    v3_gap_fail = v3_gap_legs()
    if v3_gap_fail:
        print(f"[FAIL] v3 gap legs (items 5-9): {v3_gap_fail}")
        return 1
    print("[ok] v3 gap legs: per-order falsifier command, cross-repo note, "
          "seed-commits binding, full projection catalog, acceptance compression")
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
    """Missing-field log records are dropped, well-formed ones parsed."""
    good = (
        "\x1eaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\x1faaaaaaa"
        "\x1f2026-10-01T00:00:00Z\x1ffeat(x): ok\x1fFixes: bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
        "Body prose.\n"
    )
    parsed = parse_commit_lines("garbage\n" + good + "\n\x1eshort\x1fline\n")
    if len(parsed) != 1:
        return f"expected 1 parsed commit, got {len(parsed)}"
    if parsed[0]["scope"] != "x" or parsed[0]["short"] != "aaaaaaa":
        return f"wrong fields parsed: {parsed}"
    if dependency_shas(parsed) != ["bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"]:
        return "Fixes: trailer must yield the dependency SHA"
    if parse_commit_lines("") != []:
        return "exit-0 gate: empty log must parse to []"
    return None


def v3_fixture_check():
    """v3 items 1-4: one synthetic repo exercising every new structure.

    Chicago-style: real git subprocess, real files, assertions on rendered
    state (never call counts). Determinism double-run asserted at the end.
    """
    import hashlib
    import shutil
    import subprocess
    import tempfile

    tmp = tempfile.mkdtemp(prefix="gen_workgraph_v3_fixture_")
    try:
        def git(*args):
            proc = subprocess.run(
                ["git", "-C", tmp, *args], capture_output=True, text=True,
                check=False, env={**os.environ, "GIT_AUTHOR_DATE": "2026-10-01T00:00:00Z",
                                  "GIT_COMMITTER_DATE": "2026-10-01T00:00:00Z"},
            )
            if proc.returncode != 0:
                raise RuntimeError(f"git {args[0]} failed: {proc.stderr.strip()}")
            return proc.stdout.strip()

        def write(path, content):
            os.makedirs(os.path.dirname(os.path.join(tmp, path)), exist_ok=True)
            with open(os.path.join(tmp, path), "w") as fh:
                fh.write(content)

        git("init", "-q")
        git("config", "user.email", "court@ggen.dev")
        git("config", "user.name", "Court")
        git("config", "commit.gpgsign", "false")
        journal = "docs/sjira/v26.10.8/journal.md"
        write(journal, "campaign journal\n")
        write("shared/lib.txt", "shared surface\n")
        git("add", "-A")
        git("commit", "-m", "feat(alpha): alpha base")
        sha_a = git("rev-parse", "HEAD")

        # Court artifact (v3 item 2 witness class: test file matching *court*)
        # citing SHA_A -> alpha ALIVE + requiresCourt + Court individual.
        # Every commit touches the campaign journal so git's docs/sjira/<v>/
        # path filter keeps all of them in the campaign commit set.
        write("tests/test_court_alpha.py", f"Court witness for {sha_a}\n")
        write("shared/lib.txt", "shared surface v2\n")
        write(journal, "campaign journal 2\n")
        git("add", "-A"); git("commit", "-m", "feat(beta): beta base")

        # Trailer edge: beta cites alpha's SHA via Fixes:.
        write("shared/lib.txt", "shared surface v3\n")
        write(journal, "campaign journal 3\n")
        git("add", "-A")
        git("commit", "-m", "feat(beta): beta follow-up",
            "-m", f"Fixes: {sha_a}")

        # Third co-change commit touching the shared file (>= CO_CHANGE_MIN).
        write("shared/lib.txt", "shared surface v4\n")
        write(journal, "campaign journal 4\n")
        git("add", "-A"); git("commit", "-m", "feat(gamma): gamma touch")

        text1 = render(tmp, "v26.10.8")
        text2 = render(tmp, "v26.10.8")
        if text1 != text2:
            return "double-run mismatch"

        def need(cond, msg):
            if not cond:
                return msg
            return None
        fails = [
            need("a sj:AcceptanceCriterion" in text1, "missing acceptance criterion blank node"),
            need("a sj:Falsifier" in text1, "missing falsifier blank node"),
            need(f"witnessed by tests/test_court_alpha.py" in text1,
                 "witnessed acceptance must cite the court artifact"),
            need("UNKNOWN: no on-disk receipt/court artifact" in text1,
                 "missing UNKNOWN-honest falsifier placeholder"),
            need("a sj:Court" in text1, "missing sj:Court individual"),
            need("sj:requiresCourt" in text1, "missing sj:requiresCourt"),
            need("a sj:DependencyEdge" in text1, "missing DependencyEdge"),
            need('"requiresReceipt"' in text1, "missing trailer requiresReceipt edge"),
            need('"coChange"' in text1, "missing coChange edge"),
            need(f'sj:replayIdentity "{os.path.basename(tmp)}:v26.10.8:alpha"' in text1,
                 "missing deterministic replayIdentity"),
            need("sj:pathScope" in text1, "missing pathScope"),
            need("a sj:Checkpoint" in text1, "missing checkpoint individual"),
            need("sj:checkpointOf" in text1,
                 "missing checkpointOf back-link"),
        ]
        fails = [f for f in fails if f]
        if fails:
            return "; ".join(fails)
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def make_synth_repo(tmp: str) -> None:
    """Deterministic synthetic campaign repo exercising v3 items 5-9."""
    import datetime

    env = dict(
        os.environ,
        GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com",
        GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.com",
    )
    base = datetime.datetime(2026, 10, 1, 0, 0, 0)

    def git(*args, date=None, body=None):
        e = dict(env)
        if date:
            e["GIT_AUTHOR_DATE"] = e["GIT_COMMITTER_DATE"] = date
        argv = ["git", "-C", tmp, *args]
        if body:
            argv += ["-m", body]
        proc = subprocess.run(
            argv, capture_output=True, text=True, env=e, check=False,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"git {args}: {proc.stderr.strip()}")

    def write(rel, text):
        path = os.path.join(tmp, rel)
        d = os.path.dirname(path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)

    def stamp(hour):
        return (base + datetime.timedelta(hours=hour)).strftime(
            "%Y-%m-%dT%H:%M:%SZ")

    git("init", "-q")
    write("docs/sjira/v26.10.8/W.md", "campaign seed\n")
    git("add", "-A", date=stamp(0))
    git("commit", "-m", "chore(sjira): campaign start", date=stamp(0))
    git("tag", "v26.10.8")
    # item 5: elixir-scope order with a real test target.
    write("mix.exs", "defmodule Synth.MixProject do\nend\n")
    write("lib/gen_workgraph.ex", "defmodule Synth do\nend\n")
    write("test/gen_workgraph_test.exs", "defmodule SynthTest do\nend\n")
    write("docs/sjira/v26.10.8/a.md", "axis one\n")
    git("add", "-A", date=stamp(1))
    git("commit", "-m", "feat(gen_workgraph): axis one", date=stamp(1))
    # item 6: vendored sibling + ~/<sibling> body mention.
    write("vendor/sibling-go/lib.go", "package siblinggo\n")
    write("docs/sjira/v26.10.8/v.md", "vendored\n")
    git("add", "-A", date=stamp(2))
    git("commit", "-m", "feat(vendor): vendored sibling",
        body="pulls from ~/other-synth-repo checkout", date=stamp(2))
    # item 9: enough long subjects to force compression.
    for n in range(1, 7):
        write(
            f"docs/sjira/v26.10.8/c{n}.md",
            f"acceptance line {n} with a deliberately long deterministic phrase\n",
        )
        git("add", "-A", date=stamp(2 + n))
        git(
            "commit", "-m",
            f"feat(compress): bounded acceptance subject number {n} "
            f"with a fairly long deterministic acceptance phrase tail {n}",
            date=stamp(2 + n),
        )

def v3_gap_legs():
    """Selftest legs for v3 gap items 5-9. Returns a failure string or None."""
    import shutil
    import tempfile

    tmp = tempfile.mkdtemp(prefix="gen_workgraph_v3_gap_legs_")
    try:
        try:
            make_synth_repo(tmp)
        except RuntimeError as exc:
            return f"synthetic repo setup failed: {exc}"
        ver = "v26.10.8"
        text = render(tmp, ver)
        # Item 5: per-order falsifier targets the real elixir test file.
        if "mix test test/gen_workgraph_test.exs" not in text:
            return "item 5: elixir-scope falsifier did not target the test file"
        # Item 6: vendor/ path and ~/mention both detected; primary repo intact.
        if "sj:crossRepo v8:XRepo-vendor-sibling-go" not in text:
            return "item 6: vendor/ sibling not emitted"
        if "cross-repo reference: other-synth-repo" not in text:
            return "item 6: ~/mention sibling not emitted"
        # Item 7: seed-commits binding.
        seeded = render(
            tmp, ver,
            seed_commits={"compress": ["b" * 40], "_base": "c" * 40},
        )
        if 'sj:landedCommit "' + "b" * 40 not in seeded:
            return "item 7: sj:landedCommit missing for bound scope"
        if 'sj:subjectSha "' + "b" * 40 not in seeded:
            return "item 7: sj:subjectSha missing for bound scope"
        if "commit/" + "c" * 40 not in seeded:
            return "item 7: seed _base override not applied"
        if render(tmp, ver, seed_commits={"compress": ["b" * 40]}) != render(
            tmp, ver, seed_commits={"compress": ["b" * 40]}
        ):
            return "item 7: seeded double-run mismatch"
        # Item 8: full 15-class catalog declared regardless of use.
        for ptype in PROJECTION_TYPES:
            if "sj:projection-" + ptype + " a sj:ProjectionSpec" not in text:
                return "item 8: catalog missing projection-" + ptype
        # Item 9: compression bound holds.
        long_commits = [
            {"subject": "feat(c): subject number %d with a long tail %d" % (n, n)}
            for n in range(30)
        ]
        compressed = compress_acceptance(long_commits, 400)
        if len(compressed) > 400 or "(+" not in compressed:
            return "item 9: compression failed (len=%d)" % len(compressed)
        return None
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
        m = re.match(r"^\s+(?:sj|dcterms|prov|rdfs|rdf):([A-Za-z][A-Za-z0-9]*)(?:\s|$)", line)
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
    seed_commits = None
    if args.seed_commits:
        try:
            with open(args.seed_commits, encoding="utf-8") as fh:
                seed_commits = json.load(fh)
        except (OSError, ValueError) as exc:
            print("error: --seed-commits unusable: " + str(exc), file=sys.stderr)
            return 2
        if not isinstance(seed_commits, dict):
            print("error: --seed-commits must be a JSON object", file=sys.stderr)
            return 2
    text = render(args.repo[0], args.version, seed_commits=seed_commits)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
