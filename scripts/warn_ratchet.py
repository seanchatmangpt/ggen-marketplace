#!/usr/bin/env python3
"""WARN -> ALIVE ratchet over the machine-readable qualification baseline.

    warn_ratchet.py baseline <report.json> [--out PATH]
    warn_ratchet.py check    <report.json> [--baseline PATH]

`baseline` projects a qualify_packs.py report into qualification/baseline.json
deterministically (sorted keys, no timestamps). `check` refuses
(REFUSED:WARN_RATCHET, exit 2) when any pack regressed (ALIVE->WARN/REFUSED/
SKIPPED, WARN->REFUSED/SKIPPED) or the WARN count rose versus the baseline.
Improvements are allowed; the tool then says the baseline should be re-recorded.
By default the report must cover every baselined pack and be non-empty; a
--pack subset run must pass --subset, which skips absent packs and the WARN-count
rule. Malformed reports are REFUSED:WARN_RATCHET:report_invalid (exit 2).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASELINE = ROOT / "qualification" / "baseline.json"
SCHEMA = "https://ggen.dev/marketplace/qualification-baseline/v1"
RANK = {"ALIVE": 3, "WARN": 2, "SKIPPED": 1, "REFUSED": 0}
STATUSES = ("ALIVE", "WARN", "SKIPPED", "REFUSED")


def load_report(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("report is not a JSON object")
    packs = data.get("packs")
    if not isinstance(packs, list):
        raise ValueError("report has no 'packs' list")
    if not packs:
        raise ValueError("report 'packs' list is empty")
    for record in packs:
        if not isinstance(record, dict):
            raise ValueError("report pack entry is not an object")
        if not isinstance(record.get("name"), str) or record.get("status") not in STATUSES:
            raise ValueError(f"report pack entry has invalid name/status: {record!r}")
        if record.get("warn_reason") is not None and not isinstance(record["warn_reason"], str):
            raise ValueError("report warn_reason is not a string")
    return data


def project(report: dict[str, Any]) -> dict[str, Any]:
    packs: dict[str, dict[str, str]] = {}
    for record in report["packs"]:
        entry = {"status": record["status"]}
        if record["status"] == "WARN" and record.get("warn_reason"):
            entry["warn_reason"] = re.sub(
                r"/(?:[^/`\s]+/)+([^/`\s]+/[^/`\s]+)", r"\1", record["warn_reason"]
            )
        packs[record["name"]] = entry
    counts = {s: 0 for s in STATUSES}
    for entry in packs.values():
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    return {
        "counts": counts,
        "ggen_version": report.get("ggen", ""),
        "packs": packs,
        "schema": SCHEMA,
    }


def write_baseline(report_path: Path, out: Path) -> int:
    baseline = project(load_report(report_path))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(baseline, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"baseline written packs={len(baseline['packs'])} counts={json.dumps(baseline['counts'], sort_keys=True)}")
    return 0


def compare(
    baseline: dict[str, Any], current: dict[str, Any], subset: bool = False
) -> tuple[list[str], list[str]]:
    """Return (regressions, improvements) of current versus baseline."""
    regressions: list[str] = []
    improvements: list[str] = []
    base_packs = baseline["packs"]
    cur_packs = current["packs"]
    for name in sorted(cur_packs):
        new = cur_packs[name]["status"]
        old = base_packs.get(name, {}).get("status")
        if old is None:
            if new != "ALIVE":
                regressions.append(f"{name}: new pack is {new}, must be ALIVE")
            else:
                improvements.append(f"{name}: new pack ALIVE")
            continue
        if RANK[new] < RANK[old]:
            regressions.append(f"{name}: {old} -> {new}")
        elif RANK[new] > RANK[old]:
            improvements.append(f"{name}: {old} -> {new}")
    missing = sorted(set(base_packs) - set(cur_packs))
    if missing and not subset:
        regressions.append(
            f"report does not cover {len(missing)} baselined pack(s), e.g. {missing[0]} "
            "(pass --subset for a --pack subset run)"
        )
    if not missing:
        base_warn = sum(1 for e in base_packs.values() if e["status"] == "WARN")
        cur_warn = sum(1 for e in cur_packs.values() if e["status"] == "WARN")
        if cur_warn > base_warn:
            regressions.append(f"WARN count rose {base_warn} -> {cur_warn}")
    return regressions, improvements


def check(report_path: Path, baseline_path: Path, subset: bool = False) -> int:
    if not baseline_path.is_file():
        print(f"REFUSED:WARN_RATCHET:baseline_missing:{baseline_path}", file=sys.stderr)
        return 2
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    if not isinstance(baseline, dict) or not isinstance(baseline.get("packs"), dict):
        raise ValueError("baseline has no 'packs' object")
    current = project(load_report(report_path))
    regressions, improvements = compare(baseline, current, subset)
    for line in improvements:
        print(f"improved {line}")
    if regressions:
        for line in regressions:
            print(f"regressed {line}", file=sys.stderr)
        print(f"REFUSED:WARN_RATCHET:regressions={len(regressions)}", file=sys.stderr)
        return 2
    if improvements:
        print(f"ratchet ok; {len(improvements)} improvement(s): re-record the baseline "
              f"(warn_ratchet.py baseline <report.json>)")
    else:
        print(f"ratchet ok counts={json.dumps(current['counts'], sort_keys=True)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    b = sub.add_parser("baseline", help="write qualification/baseline.json from a report")
    b.add_argument("report", type=Path)
    b.add_argument("--out", type=Path, default=DEFAULT_BASELINE)
    c = sub.add_parser("check", help="refuse if the report regressed versus the baseline")
    c.add_argument("report", type=Path)
    c.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    c.add_argument("--subset", action="store_true",
                   help="report is a --pack subset run; absent baselined packs are not compared")
    args = parser.parse_args(argv)
    try:
        if args.command == "baseline":
            return write_baseline(args.report, args.out)
        return check(args.report, args.baseline, args.subset)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"REFUSED:WARN_RATCHET:report_invalid:{error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
