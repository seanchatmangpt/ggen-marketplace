#!/usr/bin/env python3
"""run_fleet_courts.py -- run the four standalone fleet courts and aggregate
their verdicts into one machine-readable report (JSON + summary table).

Courts (each is a standalone script; this runner only orchestrates them):

  1. validate_workgraphs.py  -- sj: WORKGRAPH.ttl / goal.ttl graphs vs the
                                semantic-jira-pack work-order SHACL shapes.
  2. validate_agent_cards.py -- fleet-wide v1.0 member-contract validation of
                                agent capability cards (69 cards).
  3. validate_f5ea_graph.py  -- f5ea: SolutionGroup graphs vs the
                                fortune5-enterprise-architecture pack shapes.
  4. git_trust_court.py      -- resolve every 40-hex SHA cited in fleet
                                WORKGRAPH.ttl files against the owning repo's
                                pushed trust root (origin/HEAD).

The runner invokes each court as a real subprocess over the real fleet state
(Chicago discipline: no mocks, no fakes) and aggregates:

  - per-repo / per-court pass-fail,
  - total violations per court and overall,
  - one JSON report (stdout via --json, or written via --json-out) and a
    human summary table.

Output is deterministic: no timestamps, no paths that vary between runs,
sorted keys. Exit 0 iff every court passes; 1 otherwise.

Usage:
    python3 scripts/run_fleet_courts.py            # table + JSON on stdout
    python3 scripts/run_fleet_courts.py --json     # JSON only
    python3 scripts/run_fleet_courts.py --json-out report.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"

# Fleet workgraph targets, mirroring validate_workgraphs.py TARGETS. The
# trust court needs the same file set so both courts see the same fleet.
FLEET_WORKGRAPHS = [
    "ash_a2a/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "ash_affidavit/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "ash_pplan/docs/sjira/v26.10.8-1/WORKGRAPH.ttl",
    "ash_r2rml/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "ash_surface/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "beam4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "castle/docs/sjira/v26.10.8/goal.ttl",
    "ex4pm/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "ggen-ecosystem/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "ggen-marketplace/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "xaas/docs/sjira/v26.10.8/WORKGRAPH.ttl",
    "zcode-cli/docs/sjira/v26.10.8/WORKGRAPH.ttl",
]


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


# ---------------------------------------------------------------- courts


def court_workgraphs(tmp: Path) -> dict:
    """sj: workgraph SHACL validation (style vs defect classification)."""
    json_out = tmp / "workgraphs.json"
    rc, _out, _err = run(
        [sys.executable, str(SCRIPTS / "validate_workgraphs.py"),
         "--json-out", str(json_out)]
    )
    results = json.loads(json_out.read_text()) if json_out.exists() else []
    courts_report = []
    total_violations = 0
    defect_violations = 0
    for r in results:
        if r.get("missing"):
            courts_report.append({
                "repo": r["repo"], "status": "MISSING",
                "violations": 0, "defects": 0,
            })
            continue
        class_counts = r.get("class_counts", {})
        n_style = class_counts.get("style-mismatch", 0)
        n_defect = sum(v for k, v in class_counts.items()
                       if k != "style-mismatch")
        total_violations += n_style + n_defect
        defect_violations += n_defect
        courts_report.append({
            "repo": r["repo"],
            "status": "STYLE-ONLY" if (n_defect == 0 and not r["conforms"])
                      else ("PASS" if r["conforms"] else "DEFECTS"),
            "violations": n_style + n_defect,
            "defects": n_defect,
        })
    return {
        "court": "workgraphs",
        "script": "scripts/validate_workgraphs.py",
        "verdict": "STYLE-ONLY" if (defect_violations == 0
                                    and total_violations > 0)
                   else ("PASS" if total_violations == 0 else "FAIL"),
        "repos": courts_report,
        "total_violations": total_violations,
        "defect_violations": defect_violations,
        "exit_code": rc,
    }


def court_agent_cards(tmp: Path) -> dict:
    """Agent capability card member-contract validation."""
    rc, out, _err = run(
        [sys.executable, str(SCRIPTS / "validate_agent_cards.py"), "--json"]
    )
    try:
        report = json.loads(out)
    except json.JSONDecodeError:
        report = []
    repos = []
    total_cards = 0
    total_violations = 0
    for r in report:
        cards = r.get("cards", [])
        n = len(cards)
        errs = r.get("error_count", 0)
        total_cards += n
        total_violations += errs
        repos.append({
            "repo": r["repo"],
            "status": r.get("status", "UNKNOWN"),
            "cards": n,
            "violations": errs,
        })
    return {
        "court": "agent-cards",
        "script": "scripts/validate_agent_cards.py",
        "verdict": "PASS" if (total_violations == 0 and rc == 0) else "FAIL",
        "repos": repos,
        "total_cards": total_cards,
        "total_violations": total_violations,
        "exit_code": rc,
    }


def court_f5ea(tmp: Path) -> dict:
    """f5ea SolutionGroup SHACL validation (fixtures + TV-01 fiber)."""
    rc, out, _err = run(
        [sys.executable, str(SCRIPTS / "validate_f5ea_graph.py")]
    )
    graphs = []
    for line in out.splitlines():
        s = line.strip()
        # rows look like:  "  <name>: CONFORMS (0 violations)"
        if ": CONFORMS (" in s:
            name, rest = s.rsplit(": CONFORMS (", 1)
            graphs.append({
                "graph": name,
                "conforms": True,
                "violations": int(rest.split()[0]),
            })
        elif ": VIOLATIONS (" in s:
            name, rest = s.rsplit(": VIOLATIONS (", 1)
            graphs.append({
                "graph": name,
                "conforms": False,
                "violations": int(rest.split()[0]),
            })
    total_violations = sum(g["violations"] for g in graphs)
    return {
        "court": "f5ea-graph",
        "script": "scripts/validate_f5ea_graph.py",
        "verdict": "PASS" if rc == 0 and total_violations == 0 else "FAIL",
        "graphs": graphs,
        "total_graphs": len(graphs),
        "total_violations": total_violations,
        "exit_code": rc,
    }


def court_git_trust(tmp: Path) -> dict:
    """SHA resolution + trust-root ancestry over fleet workgraphs."""
    json_out = tmp / "git_trust.json"
    files = [str(Path.home() / rel) for rel in FLEET_WORKGRAPHS]
    files = [f for f in files if Path(f).exists()]
    rc, _out, _err = run(
        [sys.executable, str(SCRIPTS / "git_trust_court.py"),
         *sum([["--file", f] for f in files], []),
         "--json", str(json_out)]
    )
    data = json.loads(json_out.read_text()) if json_out.exists() else {}
    totals = data.get("totals", {})
    workgraphs = [
        {
            "repo": w["repo"],
            "workgraph": w["workgraph"],
            "sha_count": w["sha_count"],
        }
        for w in data.get("workgraphs", [])
    ]
    return {
        "court": "git-trust",
        "script": "scripts/git_trust_court.py",
        "verdict": "PASS" if rc == 0 else "FAIL",
        "totals": totals,
        "workgraphs": workgraphs,
        "total_workgraphs": len(workgraphs),
        "total_shas": sum(totals.values()),
        "unresolved": totals.get("UNRESOLVED", 0),
        "exit_code": rc,
    }


# ---------------------------------------------------------------- report


def build_report(tmp: Path) -> dict:
    courts = [
        court_workgraphs(tmp),
        court_agent_cards(tmp),
        court_f5ea(tmp),
        court_git_trust(tmp),
    ]
    overall = "PASS" if all(
        c["verdict"] in ("PASS", "STYLE-ONLY") for c in courts
    ) else "FAIL"
    return {
        "runner": "scripts/run_fleet_courts.py",
        "overall": overall,
        "total_violations": sum(
            c.get("total_violations", 0) for c in courts
        ),
        "courts": courts,
    }


def summary_table(report: dict) -> str:
    lines = []
    lines.append("FLEET COURTS -- one verdict report")
    lines.append("")
    hdr = f"{'court':<14} {'verdict':<11} {'violations':>10}  detail"
    lines.append(hdr)
    lines.append("-" * len(hdr))
    for c in report["courts"]:
        if c["court"] == "git-trust":
            t = c["totals"]
            detail = (f"{t.get('RESOLVED-ROOTED', 0)} rooted / "
                      f"{t.get('RESOLVED-UNROOTED', 0)} unrooted / "
                      f"{t.get('UNRESOLVED', 0)} unresolved, "
                      f"{c['total_workgraphs']} workgraphs")
        elif c["court"] == "agent-cards":
            detail = f"{c['total_cards']} cards across {len(c['repos'])} repos"
        elif c["court"] == "f5ea-graph":
            detail = f"{c['total_graphs']} graphs conform"
        else:
            n_ok = sum(1 for r in c["repos"] if r["status"] != "MISSING")
            detail = f"{n_ok} workgraph repos"
        lines.append(
            f"{c['court']:<14} {c['verdict']:<11} "
            f"{c.get('total_violations', 0):>10}  {detail}"
        )
    lines.append("-" * len(hdr))
    lines.append(
        f"OVERALL: {report['overall']}  "
        f"(total violations: {report['total_violations']})"
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", dest="as_json", action="store_true",
                    help="print the JSON report only")
    ap.add_argument("--json-out", type=Path, default=None,
                    help="also write the JSON report to this path")
    args = ap.parse_args()

    with tempfile.TemporaryDirectory() as td:
        report = build_report(Path(td))

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2, sort_keys=True)
                                 + "\n")
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(summary_table(report))
        if args.json_out:
            print(f"\nJSON report: {args.json_out}")

    return 0 if report["overall"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
