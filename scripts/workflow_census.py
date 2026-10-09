#!/usr/bin/env python3
"""Read-only census of .github/workflows/*.yml (stdlib only, no YAML library).

Emits a deterministic table: name, triggers, path filters, pull_request/push/
schedule flags, family prefix, round number, ci.yml reference, plus a
consolidation-candidate list (families where more than 10 files share an
identical normalized job skeleton).

Usage:
  python3 scripts/workflow_census.py            # JSON to stdout
  python3 scripts/workflow_census.py --markdown # docs/reference/workflow-map.md body
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"
FAMILIES = ("develop", "measure", "explore", "implement", "compose")
THRESHOLD = 10  # more than this many files sharing a skeleton -> candidate


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _strip(value: str) -> str:
    value = value.strip()
    if value.startswith(("'", '"')) and len(value) >= 2 and value[-1] == value[0]:
        return value[1:-1]
    return re.sub(r"\s+#.*$", "", value)


def top_block(lines: list[str], key: str) -> tuple[str, list[str]]:
    """Return (inline value, indented child lines) for a top-level key."""
    pat = re.compile(rf"^(?:{key}|'{key}'|\"{key}\")\s*:\s*(.*)$")
    for i, line in enumerate(lines):
        m = pat.match(line)
        if m:
            body = []
            for nxt in lines[i + 1:]:
                if nxt.strip() and _indent(nxt) == 0 and not nxt.lstrip().startswith("#"):
                    break
                body.append(nxt)
            return _strip(m.group(1)), body
    return "", []


def parse_triggers(lines: list[str]) -> tuple[list[str], list[str], list[str]]:
    inline, body = top_block(lines, "on")
    events: list[str] = []
    paths: list[str] = []
    crons: list[str] = []
    if inline:
        inner = inline.strip("[]")
        events = sorted(e.strip() for e in inner.split(",") if e.strip())
        return events, paths, crons
    body = [b for b in body if b.strip() and not b.lstrip().startswith("#")]
    if not body:
        return events, paths, crons
    base = min(_indent(b) for b in body)
    current = None
    field = None
    for b in body:
        text = b.strip()
        ind = _indent(b)
        if ind == base and not text.startswith("-"):
            key = text.split(":", 1)[0].strip("'\"")
            events.append(key)
            current, field = key, None
        elif ind == base and text.startswith("-"):
            events.append(_strip(text[1:]))
        elif ind > base and re.match(r"^[\w-]+\s*:", text) and not text.startswith("-"):
            field = text.split(":", 1)[0]
            rest = _strip(text.split(":", 1)[1])
            if rest.startswith("["):
                for item in rest.strip("[]").split(","):
                    _add(current, field, _strip(item), paths, crons)
        elif text.startswith("-") and current:
            item = _strip(text[1:])
            if item.startswith("cron:"):
                item = _strip(item.split(":", 1)[1])
                field = "cron"
            _add(current, field, item, paths, crons)
    return sorted(dict.fromkeys(events)), sorted(dict.fromkeys(paths)), sorted(dict.fromkeys(crons))


def _add(event, field, item, paths, crons):
    if not item:
        return
    if field in ("paths", "paths-ignore"):
        paths.append(f"{event}:{'!' if field == 'paths-ignore' else ''}{item}")
    elif field == "cron":
        crons.append(item)


def family_of(stem: str) -> str:
    head = stem.split("-", 1)[0]
    return head if head in FAMILIES else "other"


def round_of(stem: str) -> int | None:
    m = re.search(r"(?:^|-)r(\d+)(?=-|$|[a-z]$)", stem)
    return int(m.group(1)) if m else None


def normalize_jobs(text: str, stem: str) -> str:
    """Job skeleton: the `jobs:` block with pack/receipt/round specifics erased."""
    lines = text.splitlines()
    _, body = top_block(lines, "jobs")
    out = "\n".join(l.rstrip() for l in body if l.strip() and not l.lstrip().startswith("#"))
    out = out.replace(stem, "@WF@")
    out = re.sub(r"packs/[A-Za-z0-9_.\-]+", "packs/@P@", out)
    out = re.sub(r"receipts/[A-Za-z0-9_./\-]+", "receipts/@R@", out)
    out = re.sub(r"\b[a-z0-9]+(?:-[a-z0-9]+)*-pack\b", "@PACK@", out)
    out = re.sub(r"\br\d+[a-z]?\b", "r@N@", out)
    out = re.sub(r"\d{4}-\d{2}-\d{2}", "@DATE@", out)
    return out


def job_shape(text: str) -> str:
    """Coarse skeleton: per job, runs-on plus the ordered kinds of steps
    (`uses:` action ref without version, or `run`). Ignores names and bodies."""
    _, body = top_block(text.splitlines(), "jobs")
    parts = []
    for line in body:
        if m := re.match(r"^  ([\w-]+):\s*$", line):
            parts.append(f"job:{m.group(1)}")
        elif m := re.match(r"^\s+runs-on:\s*(.+)$", line):
            parts.append(f"on:{_strip(m.group(1))}")
        elif m := re.match(r"^\s+-?\s*uses:\s*([^@\s]+)", line):
            parts.append(f"uses:{m.group(1)}")
        elif re.match(r"^\s+-?\s*run:", line):
            parts.append("run")
    return ">".join(parts)


def ci_references(ci_text: str) -> tuple[set[str], list[str]]:
    lines = ci_text.splitlines()
    _, body = top_block(lines, "jobs")
    jobs = [m.group(1) for l in body if (m := re.match(r"^  ([\w-]+):\s*$", l))]
    return {m for m in re.findall(r"[\w.-]+\.yml", ci_text)}, jobs


def census(directory: Path = WORKFLOWS) -> dict:
    files = sorted(directory.glob("*.yml"))
    ci_text = (directory / "ci.yml").read_text(encoding="utf-8") if (directory / "ci.yml").exists() else ""
    ci_files, ci_jobs = ci_references(ci_text)
    rows = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        lines = text.splitlines()
        nm = re.search(r"^name:\s*(.+)$", text, re.M)
        events, paths, crons = parse_triggers(lines)
        stem = f.stem
        skeleton = normalize_jobs(text, stem)
        rows.append({
            "file": f.name,
            "name": _strip(nm.group(1)) if nm else "",
            "triggers": events,
            "path_filters": paths,
            "schedule": crons,
            "pull_request": "pull_request" in events or "pull_request_target" in events,
            "push": "push" in events,
            "on_schedule": "schedule" in events,
            "family": family_of(stem),
            "round": round_of(stem),
            "in_ci_yml": f.name in ci_files and f.name != "ci.yml",
            "skeleton_sha256": hashlib.sha256(skeleton.encode()).hexdigest()[:12],
            "shape_sha256": hashlib.sha256(job_shape(text).encode()).hexdigest()[:12],
        })
    fam: dict[str, dict] = {}
    for r in rows:
        s = fam.setdefault(r["family"], {"files": 0, "pull_request": 0, "push": 0, "schedule": 0, "skeletons": defaultdict(list), "shapes": defaultdict(list)})
        s["files"] += 1
        s["pull_request"] += r["pull_request"]
        s["push"] += r["push"]
        s["schedule"] += r["on_schedule"]
        s["skeletons"][r["skeleton_sha256"]].append(r["file"])
        s["shapes"][r["shape_sha256"]].append(r["file"])
    families = {}
    candidates = []
    shape_groups = []
    for name in sorted(fam):
        s = fam[name]
        groups = sorted(s["skeletons"].items(), key=lambda kv: (-len(kv[1]), kv[0]))
        families[name] = {
            "files": s["files"], "pull_request": s["pull_request"], "push": s["push"],
            "schedule": s["schedule"], "distinct_skeletons": len(groups),
            "largest_identical_group": len(groups[0][1]) if groups else 0,
            "largest_shape_group": max((len(v) for v in s["shapes"].values()), default=0),
        }
        for sha, members in sorted(s["shapes"].items(), key=lambda kv: (-len(kv[1]), kv[0])):
            if len(members) > 1:
                shape_groups.append({"family": name, "shape_sha256": sha, "count": len(members), "files": sorted(members)})
        for sha, members in groups:
            if len(members) > THRESHOLD:
                candidates.append({"family": name, "skeleton_sha256": sha, "count": len(members), "files": sorted(members)})
    return {
        "schema": "ggen.workflow-census/1",
        "total": len(rows),
        "ci_jobs": ci_jobs,
        "workflows": rows,
        "families": families,
        "consolidation_candidates": candidates,
        "shape_groups": shape_groups,
    }


def render_markdown(c: dict) -> str:
    def cell(items, limit=3):
        if not items:
            return "-"
        shown = [f"`{i}`" for i in items[:limit]]
        if len(items) > limit:
            shown.append(f"+{len(items) - limit} more")
        return "<br>".join(shown)

    out = [
        "# Workflow map", "",
        "Generated by `python3 scripts/workflow_census.py --markdown`; do not edit by hand.",
        "The census is read-only over `.github/workflows/*.yml`.", "",
        "## Contents", "",
        "- [Family summary](#family-summary)",
        "- [Consolidation candidates](#consolidation-candidates)",
        "- [ci.yml](#ciyml)",
        "- [Workflow table](#workflow-table)",
        "- [See Also](#see-also)", "",
        "## Family summary", "",
        f"{c['total']} workflows. Family is the filename prefix; round is the `rNN` token.", "",
        "| family | files | pull_request | push | schedule | distinct job skeletons | largest identical group | largest shape group |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, f in c["families"].items():
        out.append(f"| {name} | {f['files']} | {f['pull_request']} | {f['push']} | {f['schedule']} | {f['distinct_skeletons']} | {f['largest_identical_group']} | {f['largest_shape_group']} |")
    out += ["", "## Consolidation candidates", "",
            f"Families where more than {THRESHOLD} files share an identical job skeleton after",
            "normalizing pack names, `packs/`/`receipts/` paths, round tokens, dates and the",
            "workflow's own name.", ""]
    if c["consolidation_candidates"]:
        for cand in c["consolidation_candidates"]:
            out.append(f"- **{cand['family']}**: {cand['count']} files, skeleton `{cand['skeleton_sha256']}`")
            for fn in cand["files"]:
                out.append(f"  - `{fn}`")
    else:
        out.append("None: no family has more than the threshold of files with an identical skeleton.")
    out += ["", "Shape groups (weaker signal: same job ids, runner and ordered step kinds, ignoring",
            "names and bodies); groups of two or more files. Groups over the threshold are the",
            "shape-level candidate-consolidation list:", ""]
    if c["shape_groups"]:
        for g in c["shape_groups"]:
            tag = " CANDIDATE" if g["count"] > THRESHOLD else ""
            out.append(f"- **{g['family']}**{tag}: {g['count']} files, shape `{g['shape_sha256']}`: "
                       + ", ".join(f"`{x}`" for x in g["files"]))
    else:
        out.append("None.")
    out += ["", "## ci.yml", "",
            "Jobs in `ci.yml`: " + (", ".join(f"`{j}`" for j in c["ci_jobs"]) or "none") + ".",
            "Workflow files named inside `ci.yml`: " + (
                ", ".join(f"`{r['file']}`" for r in c["workflows"] if r["in_ci_yml"]) or "none") + ".", "",
            "## Workflow table", "",
            "| file | name | triggers | path filters | PR | push | sched | family | round | in ci.yml |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    yn = lambda b: "yes" if b else "no"
    for r in c["workflows"]:
        name = r["name"].replace("|", "\\|")
        out.append(
            f"| `{r['file']}` | {name} | {', '.join(r['triggers']) or '-'} | {cell(r['path_filters'])} "
            f"| {yn(r['pull_request'])} | {yn(r['push'])} | {yn(r['on_schedule'])} | {r['family']} "
            f"| {r['round'] if r['round'] is not None else '-'} | {yn(r['in_ci_yml'])} |")
    out += ["", "## See Also", "", "- [Pack capabilities](pack-capabilities.md)", "- [Pack contract](pack-contract.md)", ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "usage").splitlines()[0])
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--workflows-dir", type=Path, default=WORKFLOWS)
    args = ap.parse_args(argv)
    c = census(args.workflows_dir)
    if args.markdown:
        sys.stdout.write(render_markdown(c))
    else:
        json.dump(c, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
