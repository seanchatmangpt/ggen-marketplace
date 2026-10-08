#!/usr/bin/env python3
"""doc_surface.py — doc-hdit doc-surface toolchain entry point.

`scaffold` is wired: it dispatches to the rust-doc-hdit-pack's `doc-hdit`
binary, which renders the pack's Tera templates from a code-surface JSON
(`gen_doc_surface.py code REPO`) into a docs directory with
AGENT-FORBIDDEN-fenced reference tables and AGENT-COMMENTARY merge.
`vectorize`/`audit` remain executable in the Rust binary too;
`certify` is still REFUSED.

Verbs:
    doc-hdit:scaffold   --code <json> --templates <dir> --out <docsdir>
    doc-hdit:vectorize / :audit  <inputs.json> [court-file]
    doc-hdit:certify    (REFUSED:DOC_HDIT_STUB)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

VERBS = ("scaffold", "vectorize", "audit", "certify")
PACK_DIR = Path(__file__).resolve().parent.parent / "packs" / "rust-doc-hdit-pack"


def find_binary() -> str | None:
    """Locate the built doc-hdit binary (env override, then pack target dir)."""
    candidates = [
        os.environ.get("DOC_HDIT_BIN"),
        str(PACK_DIR / "target" / "release" / "doc-hdit"),
        str(PACK_DIR / "target" / "debug" / "doc-hdit"),
    ]
    for cand in candidates:
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def main() -> int:
    parser = argparse.ArgumentParser(prog="doc-hdit")
    parser.add_argument("verb", choices=VERBS)
    parser.add_argument("rest", nargs=argparse.REMAINDER, help="verb-specific flags")
    args = parser.parse_args()

    if args.verb == "certify":
        print(
            "REFUSED:DOC_HDIT_STUB:certify:certification lands with the rust-doc-hdit binary"
        )
        return 2

    binary = find_binary()
    if binary is None:
        print(
            "REFUSED:DOC_HDIT_STUB:"
            f"{args.verb}:no doc-hdit binary found under {PACK_DIR}/target "
            "(build with: cargo build --release -p doc-hdit)"
        )
        return 2

    try:
        proc = subprocess.run(
            [binary, args.verb, *args.rest],
            capture_output=True,
            text=True,
        )
    except OSError as exc:
        print(f"REFUSED:DOC_HDIT_STUB:{args.verb}:{exc}")
        return 2
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
