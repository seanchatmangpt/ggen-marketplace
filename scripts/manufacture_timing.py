#!/usr/bin/env python3
"""Summarize and compare manufacture wall-clock from qualification reports.

`qualify_packs.py --report` records per-pack wall-clock under the report's
top-level ``timings`` object, deliberately outside the deterministic per-pack
records. This tool turns one report into a summary, or two reports into an
exact-subject comparison, so a claim like "manufacturing time fell" is backed
by measurements rather than by activity counts such as commits.

What it measures: bounded ggen load/manufacture/replay wall-clock for admitted
packs, as observed by one qualification run on one machine.

What it does not establish: generated-program correctness, consumer or external
consequence, customer acceptance, or any standing other than the ALIVE/REFUSED
already carried by the report. Timing is an observation, never standing.

Comparison law: a pack is compared only when it is ALIVE in both reports with an
identical ``source_sha256`` (same subject). Packs whose source changed, or that
are missing/not ALIVE on either side, are listed as excluded with the reason and
never averaged in.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

QUALIFICATION_SCHEMA = "https://ggen.dev/marketplace/qualification/v1"
TIMINGS_SCHEMA = "https://ggen.dev/marketplace/qualification-timings/v1"
OUTPUT_SCHEMA = "https://ggen.dev/marketplace/manufacture-timing/v1"

CLAIMS_NOT_MADE = (
    "timing is an observation, not standing",
    "wall-clock depends on host load and worker count; repeat runs before trusting a delta",
    "a faster pack manufacture is not evidence of correctness, consumer behavior, or authority",
    "an improvement on unchanged sources is attributable to toolchain/generator change only when ggen differs",
)


class TimingContractError(ValueError):
    """The report does not carry the admitted qualification + timings shape."""


def load_report(path: Path) -> dict[str, Any]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise TimingContractError(f"REFUSED:TIMING_REPORT_UNREADABLE:{path}:{error}") from error
    if report.get("schema") != QUALIFICATION_SCHEMA:
        raise TimingContractError(f"REFUSED:TIMING_REPORT_SCHEMA:{path}")
    timings = report.get("timings")
    if not isinstance(timings, dict) or timings.get("schema") != TIMINGS_SCHEMA:
        raise TimingContractError(f"REFUSED:TIMING_REPORT_HAS_NO_TIMINGS:{path}")
    seconds = timings.get("pack_seconds")
    if not isinstance(seconds, dict) or not all(
        isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 for v in seconds.values()
    ):
        raise TimingContractError(f"REFUSED:TIMING_REPORT_PACK_SECONDS_INVALID:{path}")
    return report


def percentile(sorted_values: list[float], fraction: float) -> float:
    """Nearest-rank percentile; 0.0 for an empty list."""
    if not sorted_values:
        return 0.0
    rank = max(1, math.ceil(fraction * len(sorted_values)))
    return sorted_values[rank - 1]


def summarize(report: dict[str, Any]) -> dict[str, Any]:
    seconds: dict[str, float] = report["timings"]["pack_seconds"]
    statuses: dict[str, int] = {}
    for record in report["packs"]:
        statuses[record["status"]] = statuses.get(record["status"], 0) + 1
    alive = sorted(
        seconds[r["name"]] for r in report["packs"] if r["status"] == "ALIVE" and r["name"] in seconds
    )
    return {
        "alive_seconds": {
            "count": len(alive),
            "max": round(alive[-1], 3) if alive else 0.0,
            "p50": round(percentile(alive, 0.50), 3),
            "p95": round(percentile(alive, 0.95), 3),
            "total_serial": round(sum(alive), 3),
        },
        "ggen": report.get("ggen"),
        "pack_count": report.get("pack_count", len(report["packs"])),
        "status_counts": dict(sorted(statuses.items())),
        "workers": report["timings"].get("workers"),
    }


def compare(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    base = {r["name"]: r for r in baseline["packs"]}
    cand = {r["name"]: r for r in candidate["packs"]}
    base_s = baseline["timings"]["pack_seconds"]
    cand_s = candidate["timings"]["pack_seconds"]

    pairs: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    for name in sorted(set(base) | set(cand)):
        b, c = base.get(name), cand.get(name)
        if b is None or c is None:
            excluded.append({"name": name, "reason": "missing_in_baseline" if b is None else "missing_in_candidate"})
        elif b["status"] != "ALIVE" or c["status"] != "ALIVE":
            excluded.append({"name": name, "reason": f"not_alive_in_both:{b['status']}->{c['status']}"})
        elif b.get("source_sha256") != c.get("source_sha256"):
            excluded.append({"name": name, "reason": "source_changed"})
        elif name not in base_s or name not in cand_s:
            excluded.append({"name": name, "reason": "timing_missing"})
        else:
            before, after = float(base_s[name]), float(cand_s[name])
            pairs.append(
                {
                    "after_seconds": after,
                    "before_seconds": before,
                    "name": name,
                    "ratio": round(after / before, 4) if before > 0 else None,
                }
            )

    before_total = sum(p["before_seconds"] for p in pairs)
    after_total = sum(p["after_seconds"] for p in pairs)
    ratios = sorted(p["ratio"] for p in pairs if p["ratio"] is not None)
    toolchain_changed = baseline.get("ggen") != candidate.get("ggen")
    workers_match = baseline["timings"].get("workers") == candidate["timings"].get("workers")
    return {
        "caveats": {
            "toolchain_changed": toolchain_changed,
            "workers_match": workers_match,
        },
        "claims_not_made": list(CLAIMS_NOT_MADE),
        "comparable": {
            "after_total_serial": round(after_total, 3),
            "before_total_serial": round(before_total, 3),
            "count": len(pairs),
            "median_ratio": round(percentile(ratios, 0.50), 4) if ratios else None,
            "total_ratio": round(after_total / before_total, 4) if before_total > 0 else None,
        },
        "excluded": excluded,
        "pairs": pairs,
        "schema": OUTPUT_SCHEMA,
    }


def render_text(summary: dict[str, Any]) -> str:
    a = summary["alive_seconds"]
    return (
        f"packs={summary['pack_count']} statuses={json.dumps(summary['status_counts'], sort_keys=True)} "
        f"alive={a['count']} p50={a['p50']}s p95={a['p95']}s max={a['max']}s "
        f"total_serial={a['total_serial']}s workers={summary['workers']} ggen={json.dumps(summary['ggen'])}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    s = sub.add_parser("summarize", help="summarize one qualification report")
    s.add_argument("report", type=Path)
    s.add_argument("--json", action="store_true")
    c = sub.add_parser("compare", help="exact-subject comparison of two reports (baseline, candidate)")
    c.add_argument("baseline", type=Path)
    c.add_argument("candidate", type=Path)
    c.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.command == "summarize":
            summary = summarize(load_report(args.report))
            print(json.dumps(summary, indent=2, sort_keys=True) if args.json else render_text(summary))
            return 0
        result = compare(load_report(args.baseline), load_report(args.candidate))
    except TimingContractError as error:
        print(error, file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        cmp_ = result["comparable"]
        print(
            f"comparable={cmp_['count']} excluded={len(result['excluded'])} "
            f"total_ratio={cmp_['total_ratio']} median_ratio={cmp_['median_ratio']} "
            f"toolchain_changed={result['caveats']['toolchain_changed']} "
            f"workers_match={result['caveats']['workers_match']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
