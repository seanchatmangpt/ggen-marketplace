#!/usr/bin/env python3
"""Rewrite fortune5-testing-bblock-pack's consumer-admitted facts in a copied
scratch consumer's `ontology.ttl` (v26.9.1 GM-03 portability contract).

Used by `.github/workflows/fortune5-testing-bblock-execution.yml` to point a
*copy* of the pack at a scratch consumer project instead of the pack's own
baked-in ggen-repo defaults (`tb:consumerRootMarker "Cargo.toml"`,
`tb:consumerBinaryCommand "ggen"`, `tb:consumerTestCommand "cargo test -p
ggen-cli-lib bblock --lib"`, ...). This edits the single copied
`ontology.ttl` file in place -- it never merges a second RDF graph over the
pack's own individual, which would leave two triples for the same predicate
on `tb:TestingBBlock` and an unspecified `LIMIT 1` tie-break in
`queries/testing-bblock.rq` (verified empirically against the real ggen
runtime while building this script: composing the pack via a consumer
`[packs]` table entry instead of copying+editing it fails outright, since
this pack's templates carry no per-file frontmatter `to:` routing -- they
rely entirely on the pack's own `ggen.toml` `[[generation.rules]]` table,
which only applies when the pack is synced as its own project root).

Fails closed (non-zero exit, no partial rewrite) if a targeted triple is not
found exactly once, so a future edit to the pack's ontology.ttl shape that
silently breaks this rewrite is a loud CI failure, not a quiet no-op.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# (predicate local name, replacement literal value)
DEFAULT_FACTS: dict[str, str] = {
    "consumerRootMarker": "CONSUMER_PROJECT_ROOT.marker",
    "consumerBinaryCommand": "true",
    "consumerTestCommand": "true",
    "consumerForbiddenTokenFiles": "",
    "consumerForbiddenTokens": "",
}


def rewrite(consumer_root: Path, facts: dict[str, str]) -> None:
    ontology = consumer_root / "ontology.ttl"
    text = ontology.read_text(encoding="utf-8")
    for predicate, value in facts.items():
        pattern = re.compile(rf'tb:{re.escape(predicate)} "[^"]*"')
        new_text, count = pattern.subn(f'tb:{predicate} "{value}"', text)
        if count != 1:
            raise SystemExit(
                f"REFUSED:EXPECTED_EXACTLY_ONE_{predicate}_TRIPLE:found={count}:file={ontology}"
            )
        text = new_text
    ontology.write_text(text, encoding="utf-8")
    print(f"rewrote consumer-admitted facts in {ontology}: {facts}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consumer_root", type=Path, help="path to the copied pack (scratch consumer root)")
    parser.add_argument("--root-marker", default=DEFAULT_FACTS["consumerRootMarker"])
    parser.add_argument("--binary-command", default=DEFAULT_FACTS["consumerBinaryCommand"])
    parser.add_argument("--test-command", default=DEFAULT_FACTS["consumerTestCommand"])
    parser.add_argument("--forbidden-token-files", default=DEFAULT_FACTS["consumerForbiddenTokenFiles"])
    parser.add_argument("--forbidden-tokens", default=DEFAULT_FACTS["consumerForbiddenTokens"])
    args = parser.parse_args()

    if not (args.consumer_root / "ontology.ttl").is_file():
        print(f"REFUSED:CONSUMER_ONTOLOGY_MISSING:{args.consumer_root}", file=sys.stderr)
        return 2

    rewrite(
        args.consumer_root,
        {
            "consumerRootMarker": args.root_marker,
            "consumerBinaryCommand": args.binary_command,
            "consumerTestCommand": args.test_command,
            "consumerForbiddenTokenFiles": args.forbidden_token_files,
            "consumerForbiddenTokens": args.forbidden_tokens,
        },
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
