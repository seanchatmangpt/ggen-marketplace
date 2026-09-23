#!/usr/bin/env python3
"""# MESSAGE: templates/ must be ontology-driven; banned domain literals are a refusal."""
import pathlib, re, sys

BANNED = ("zcode", "xaas", "ggen", "autofde", "ggen-marketplace", "praxis", "wasm4pm", "ex4pm", "affidavit")


def scan(root: pathlib.Path) -> list[str]:
    hits = []
    for path in sorted((root / "templates").rglob("*")):
        if not path.is_file():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for word in BANNED:
                if re.search(re.escape(word), line, re.IGNORECASE):
                    hits.append(f"REFUSED[BANNED_LITERAL]: {path.name}:{n}: {word}")
    return hits


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent
    found = scan(root)
    print("\n".join(found) if found else "ALIVE: no banned literals in templates/")
    raise SystemExit(1 if found else 0)
