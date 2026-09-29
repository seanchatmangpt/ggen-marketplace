#!/usr/bin/env python3
"""Performance-budget gate: the consumer's measured-performance section exists,
carries enough real measured rows, and its ES256-verify median agrees with a
fresh re-measurement on THIS machine.

Law (wave-4 W4-L10): a performance number in the consumer doc is a CLAIM; this
gate re-observes the claim's subject (one criterion smoke bench, es256 verify,
sample-size 10) and refuses when the claimed median drifts outside one order
of magnitude of the fresh measurement. The check is machine-relative: it never
asserts a hardware-independent budget, only that the documented number is still
a real output of the real bench suite where it is claimed.

Target-agnostic by contract: the gate runs in the pack (marketplace) context
where the consumer repo may not exist. If the consumer doc is absent there is
no claim to check -> printed SKIP, exit 0 (no vacuity: the check fires whenever
its subject exists; witnessed by direct execution, like 040_no_mock_crypto.py).

Consumer doc resolution: $CTP_CONSUMER_DOC, else ../../../affidavit/docs/
CRYPTO_TRUST_PLANE.md relative to the pack root (pack lives at
<marketplace>/packs/affidavit-trust-plane-pack). The consumer repo root (where
`cargo bench` runs) is $CTP_CONSUMER_REPO if set, else the doc's grandparent
directory — override it when witnessing against a doctored doc copy that does
not live inside the repo tree.

Usage: 120_performance_budget.py [consumer_doc]
Exit 0 ALIVE / SKIP; exit 2 REFUSED naming file:line:reason.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys

MIN_MEASURED_ROWS = 6
SMOKE_BENCH = "ctp_es256_verify"
DRIFT_FACTOR = 10.0  # machine-relative band: fresh/claimed within [1/10, 10]
BENCH_TIMEOUT_SECS = 1800

SECTION_RE = re.compile(r"^#{1,6}\s+.*Measured performance", re.IGNORECASE)
BENCH_ID_RE = re.compile(r"`(ctp_[a-z0-9_]+)`")
TIME_RE = re.compile(r"(?P<value>\d+(?:\.\d+)?)\s*(?P<unit>ns|µs|us|ms|s)\b")
UNIT_SECONDS = {"ns": 1e-9, "us": 1e-6, "µs": 1e-6, "ms": 1e-3, "s": 1.0}


def refused(reason: str) -> int:
    print(f"REFUSED[{reason.split(':', 1)[0]}]: {reason}")
    return 2


def parse_time_seconds(text: str) -> float | None:
    match = TIME_RE.search(text)
    if match is None:
        return None
    return float(match.group("value")) * UNIT_SECONDS[match.group("unit")]


def measured_rows(doc: pathlib.Path) -> tuple[int, dict[str, tuple[float, int]]]:
    """Return (row_count, {bench_id: (median_seconds, line_number)}) from the
    Measured performance section. A row is measured iff it names a ctp_ bench
    id in backticks and carries exactly one time value."""
    lines = doc.read_text(encoding="utf-8").split("\n")
    section_start = None
    for number, line in enumerate(lines, 1):
        if SECTION_RE.match(line):
            section_start = number
            break
    if section_start is None:
        return -1, {}
    rows: dict[str, tuple[float, int]] = {}
    count = 0
    for number, line in enumerate(lines[section_start:], section_start + 1):
        if number > section_start and re.match(r"^#{1,6}\s", line):
            break  # next section begins
        if not line.lstrip().startswith("|"):
            continue
        ids = BENCH_ID_RE.findall(line)
        if not ids:
            continue  # header/divider row
        times = TIME_RE.findall(line)
        if len(times) != 1:
            raise ValueError(
                f"{doc}:{number}: row for {ids[0]} must carry exactly one "
                f"time value (the median), found {len(times)}"
            )
        count += 1
        seconds = float(times[0][0]) * UNIT_SECONDS[times[0][1]]
        rows[ids[0]] = (seconds, number)
    return count, rows


def fresh_median_seconds(repo_root: pathlib.Path) -> float:
    """Re-run ONE smoke bench and read criterion's median estimate."""
    command = [
        "cargo", "bench",
        "--features", "crypto-trust",
        "--bench", "crypto_trust_bench",
        "--",
        "--sample-size", "10",
        "--warm-up-time", "1",
        "--measurement-time", "2",
        SMOKE_BENCH,
    ]
    completed = subprocess.run(
        command, cwd=repo_root, env=os.environ.copy(),
        capture_output=True, text=True, timeout=BENCH_TIMEOUT_SECS,
    )
    if completed.returncode != 0:
        tail = (completed.stdout + completed.stderr).strip().split("\n")[-3:]
        raise RuntimeError(
            f"smoke bench exited {completed.returncode}: {' | '.join(tail)}"
        )
    target_dir = os.environ.get("CARGO_TARGET_DIR", str(repo_root / "target"))
    estimates = pathlib.Path(target_dir) / "criterion" / SMOKE_BENCH / "new" / "estimates.json"
    if not estimates.is_file():
        raise RuntimeError(f"criterion estimates not found: {estimates}")
    median = json.loads(estimates.read_text(encoding="utf-8"))["median"]["point_estimate"]
    return float(median) * 1e-9  # criterion stores nanoseconds


def main(argv: list[str]) -> int:
    pack_root = pathlib.Path(__file__).resolve().parent.parent
    doc = (
        pathlib.Path(argv[1]).resolve() if len(argv) > 1
        else pathlib.Path(os.environ.get("CTP_CONSUMER_DOC",
                                         pack_root / "../../../affidavit/docs/CRYPTO_TRUST_PLANE.md"))
        .resolve()
    )
    if not doc.is_file():
        print(f"SKIP[NO_CONSUMER_DOC]: {doc} does not exist — no consumer, "
              f"no claim; performance-budget check not applicable here")
        return 0
    repo_root = pathlib.Path(
        os.environ.get("CTP_CONSUMER_REPO", doc.parent.parent)).resolve()

    try:
        count, rows = measured_rows(doc)
    except ValueError as error:
        return refused(f"PERF_ROW_UNPARSEABLE: {error}")
    if count == -1:
        return refused(f"PERF_SECTION_MISSING: {doc}: no 'Measured performance' section")
    if count < MIN_MEASURED_ROWS:
        return refused(
            f"PERF_SECTION_TOO_THIN: {doc}: measured-performance section carries "
            f"{count} measured rows, law requires >= {MIN_MEASURED_ROWS}"
        )
    if SMOKE_BENCH not in rows:
        return refused(f"PERF_SMOKE_ROW_MISSING: {doc}: no measured row for `{SMOKE_BENCH}`")
    claimed_seconds, claimed_line = rows[SMOKE_BENCH]

    try:
        fresh_seconds = fresh_median_seconds(repo_root)
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as error:
        return refused(f"PERF_BENCH_UNRUNNABLE: could not re-observe {SMOKE_BENCH}: {error}")

    ratio = claimed_seconds / fresh_seconds
    if not (1.0 / DRIFT_FACTOR <= ratio <= DRIFT_FACTOR):
        return refused(
            f"PERF_DRIFT_ALARM: {doc}:{claimed_line}: claimed `{SMOKE_BENCH}` median "
            f"{claimed_seconds * 1e6:.2f} µs is {ratio:.2f}x the fresh measurement "
            f"{fresh_seconds * 1e6:.2f} µs (band ±{DRIFT_FACTOR:.0f}x, machine-relative)"
        )
    print(
        f"ALIVE: {count} measured rows in {doc.name}; `{SMOKE_BENCH}` claimed "
        f"{claimed_seconds * 1e6:.2f} µs vs fresh {fresh_seconds * 1e6:.2f} µs "
        f"(ratio {ratio:.2f}, within ±{DRIFT_FACTOR:.0f}x)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
