#!/usr/bin/env python3
"""doc_surface.py — stub for the rust-doc-hdit-pack doc-surface toolchain.

STATUS: stub. The real extraction/vectorization/audit lives in the
rust-doc-hdit binary (tree-sitter + oxigraph + wasi). This stub exists so the
pack layout is inspectable and CI has a seam to wire the binary into; it
performs no extraction and refuses to certify anything.

Verbs (all REFUSED until the binary lands):
    doc-hdit:scaffold / :vectorize / :audit / :certify
"""

from __future__ import annotations

import argparse
import sys

VERBS = ("scaffold", "vectorize", "audit", "certify")


def main() -> int:
    parser = argparse.ArgumentParser(prog="doc-hdit")
    parser.add_argument("verb", choices=VERBS)
    parser.add_argument("crate", help="path to the Rust crate to document")
    args = parser.parse_args()
    print(f"REFUSED:DOC_HDIT_STUB:{args.verb}:{args.crate}:executable lands with the rust-doc-hdit binary")
    return 2


if __name__ == "__main__":
    sys.exit(main())
