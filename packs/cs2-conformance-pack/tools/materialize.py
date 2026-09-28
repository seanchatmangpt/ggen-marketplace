#!/usr/bin/env python3
"""Materialize a directory of deterministic CS2 consumer projections."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from project import ExactSubject, canonical
from registry import batch_construct


def load_json(path: Path):
    return json.loads(path.read_text())


def safe_name(kind: str) -> str:
    normalized = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in kind.lower())
    normalized = normalized.strip("-")
    if not normalized:
        raise ValueError("INVALID_PROJECTION_KIND")
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("subject", type=Path)
    parser.add_argument("specs", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    subject = ExactSubject.parse(load_json(args.subject))
    specs = load_json(args.specs)
    if not isinstance(specs, list):
        raise ValueError("SPECS_MUST_BE_ARRAY")

    projections, receipt = batch_construct(subject, specs)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    index = []
    for item in projections:
        name = safe_name(item["projection_kind"]) + ".json"
        (args.out_dir / name).write_bytes(canonical(item) + b"\n")
        index.append({"kind": item["projection_kind"], "file": name, "digest": item["projection_digest"]})
    (args.out_dir / "index.json").write_bytes(canonical({"subject": subject.subject, "projections": index}) + b"\n")
    (args.out_dir / "receipt.json").write_bytes(canonical(receipt) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
