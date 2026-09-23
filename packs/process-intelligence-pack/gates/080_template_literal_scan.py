#!/usr/bin/env python3
"""Refuse banned domain literals in templates/.

Templates must be driven by ontology individuals only. Namespace IRIs
(`<https://...>`) are vocabulary identifiers, not domain literals, and are
stripped before scanning. Usage: 080_template_literal_scan.py [pack_dir]
Exit 0 = clean; exit 2 = REFUSED, one `path:line: literal` row per hit.
"""
import pathlib
import re
import sys

BANNED = (
    "zcode", "xaas", "ggen", "autofde", "affidavit", "wasm4pm", "ex4pm",
    "praxis", "clap-noun-verb", "turbo-fieldfare", "otel-weaver", "gdmcp",
    "process-intelligence-pack",
)
IRI = re.compile(r"<https?://[^>\s]*>")


def scan(pack: pathlib.Path) -> list[str]:
    hits: list[str] = []
    for path in sorted((pack / "templates").rglob("*")):
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            text = IRI.sub("", line).lower()
            for literal in BANNED:
                if literal in text:
                    hits.append(f"{path.relative_to(pack).as_posix()}:{number}: {literal}")
    return hits


def main(argv: list[str]) -> int:
    pack = pathlib.Path(argv[1]) if len(argv) > 1 else pathlib.Path(__file__).resolve().parent.parent
    hits = scan(pack)
    for hit in hits:
        print(f"REFUSED[BANNED_LITERAL]: {hit}")
    if hits:
        return 2
    print("ALIVE: no banned domain literals in templates/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
