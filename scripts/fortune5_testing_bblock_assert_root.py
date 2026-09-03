#!/usr/bin/env python3
"""Assert the generated `testing_bblock.py`'s `protocol-unit` suite discovered
the SCRATCH consumer's own project root -- not a ggen-repo-specific path
(`crates/ggen-cli`, `ggen-cli-lib`, or any other hardcoded default). This is
the exact regression GM-03 (v26.9.1) fixed: before that fix, root discovery
was a `Cargo.toml` + `crates/ggen-cli` filesystem walk baked into the
template, not the consumer-admitted `tb:consumerRootMarker` fact.

Reads the `protocol-unit` suite's own report + evidence (written by running
`testing_bblock.py run protocol-unit --report <path>` against the scratch
consumer) and checks the real `cwd` the suite's subprocess command actually
ran under -- not merely that the script exited zero, which a stale hardcoded
root would also do as long as some ancestor of the real filesystem happened
to contain the marker it was looking for.

Verified adversarially while building this script: pointing the scratch
consumer's admitted root marker at a decoy file that exists only in a PARENT
directory (not the scratch consumer itself) makes this assertion fail with
`REFUSED:DISCOVERED_ROOT_MISMATCH`, proving it distinguishes a correct
resolution from an incorrect one rather than passing unconditionally.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scratch_consumer", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    scratch = args.scratch_consumer.resolve()
    if not args.report.is_file():
        print(f"REFUSED:REPORT_MISSING:{args.report}", file=sys.stderr)
        return 2
    report = json.loads(args.report.read_text(encoding="utf-8"))

    if report.get("standing") != "ALIVE":
        print(f"REFUSED:SUITE_NOT_ALIVE:{report.get('standing')}", file=sys.stderr)
        return 2
    receipts = report.get("receipts") or []
    if not receipts:
        print("REFUSED:NO_RECEIPTS", file=sys.stderr)
        return 2
    receipt = receipts[0]
    evidence_path = Path(receipt["evidence_path"])
    if not evidence_path.is_file():
        print(f"REFUSED:EVIDENCE_MISSING:{evidence_path}", file=sys.stderr)
        return 2
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    commands = evidence.get("details", {}).get("commands") or []
    if not commands:
        print("REFUSED:NO_COMMANDS_IN_EVIDENCE", file=sys.stderr)
        return 2
    cwd = commands[0]["cwd"]
    expected = str(scratch)

    if cwd != expected:
        print(f"REFUSED:DISCOVERED_ROOT_MISMATCH:expected={expected!r}:actual={cwd!r}", file=sys.stderr)
        return 2
    if "crates/ggen-cli" in cwd or "ggen-cli-lib" in cwd:
        print(f"REFUSED:DISCOVERED_ROOT_LOOKS_GGEN_REPO_SPECIFIC:{cwd!r}", file=sys.stderr)
        return 2

    print(f"PASS: discovered root == scratch consumer root ({cwd})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
