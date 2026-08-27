#!/usr/bin/env python3
"""Fail-closed structural qualification for configured semantic gate witness courts."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from collections import Counter
from pathlib import Path

SCHEMA = "ggen.semantic-gate-witness-court/1"
GATE_SUFFIXES = {".rq", ".sparql"}


class CourtError(ValueError):
    pass


def safe_dir(pack: Path, raw: object, field: str) -> Path:
    if not isinstance(raw, str) or not raw:
        raise CourtError(f"{field}: expected non-empty relative path")
    relative = Path(raw)
    if relative.is_absolute() or ".." in relative.parts:
        raise CourtError(f"{field}: unsafe path {raw!r}")
    target = (pack / relative).resolve()
    try:
        target.relative_to(pack.resolve())
    except ValueError as error:
        raise CourtError(f"{field}: path escapes pack: {raw!r}") from error
    if not target.is_dir():
        raise CourtError(f"{field}: directory does not exist: {raw!r}")
    return target


def stems(directory: Path, *, gates: bool = False) -> tuple[set[str], list[str]]:
    files = sorted(path for path in directory.iterdir() if path.is_file())
    if gates:
        files = [path for path in files if path.suffix.lower() in GATE_SUFFIXES]
    values = [path.stem for path in files]
    duplicates = sorted(name for name, count in Counter(values).items() if count > 1)
    return set(values), duplicates


def qualify(pack: Path) -> dict[str, object]:
    contract_path = pack / "gate-court.toml"
    try:
        payload = tomllib.loads(contract_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise CourtError(f"invalid gate-court.toml: {error}") from error
    court = payload.get("court")
    if not isinstance(court, dict):
        raise CourtError("missing [court] table")
    if court.get("schema") != SCHEMA:
        raise CourtError(f"schema: expected {SCHEMA!r}")
    if court.get("case_key") != "exact-stem":
        raise CourtError("case_key: only exact-stem is admitted")

    gate_dir = safe_dir(pack, court.get("gate_dir"), "gate_dir")
    pass_dir = safe_dir(pack, court.get("pass_dir"), "pass_dir")
    fail_dir = safe_dir(pack, court.get("fail_dir"), "fail_dir")
    gate_cases, gate_dupes = stems(gate_dir, gates=True)
    pass_cases, pass_dupes = stems(pass_dir)
    fail_cases, fail_dupes = stems(fail_dir)
    if not gate_cases:
        raise CourtError("gate_dir: no .rq/.sparql gates")
    if gate_dupes or pass_dupes or fail_dupes:
        raise CourtError(
            "duplicate case stems: "
            + json.dumps({"gates": gate_dupes, "pass": pass_dupes, "fail": fail_dupes}, sort_keys=True)
        )

    require_pass = court.get("require_pass") is True
    require_fail = court.get("require_fail") is True
    missing_pass = sorted(gate_cases - pass_cases) if require_pass else []
    missing_fail = sorted(gate_cases - fail_cases) if require_fail else []
    orphan_pass = sorted(pass_cases - gate_cases)
    orphan_fail = sorted(fail_cases - gate_cases)
    if missing_pass or missing_fail or orphan_pass or orphan_fail:
        raise CourtError(
            "case correspondence failure: "
            + json.dumps(
                {
                    "missing_fail": missing_fail,
                    "missing_pass": missing_pass,
                    "orphan_fail": orphan_fail,
                    "orphan_pass": orphan_pass,
                },
                sort_keys=True,
            )
        )

    return {
        "case_count": len(gate_cases),
        "pack": pack.name,
        "require_fail": require_fail,
        "require_pass": require_pass,
        "schema": SCHEMA,
        "standing": "ALIVE",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packs", type=Path, default=Path("packs"))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    configured = sorted(path.parent for path in args.packs.glob("*/gate-court.toml"))
    records: list[dict[str, object]] = []
    failures: list[str] = []
    for pack in configured:
        try:
            records.append(qualify(pack))
        except CourtError as error:
            failures.append(f"{pack.name}: {error}")

    payload = {
        "configured_pack_count": len(configured),
        "courts": records,
        "schema": "ggen.marketplace.gate-witness-courts/1",
        "standing": "REFUSED" if failures else "ALIVE",
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if failures:
        for failure in failures:
            print(f"REFUSED:GATE_WITNESS_COURT:{failure}", file=sys.stderr)
        return 2
    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
