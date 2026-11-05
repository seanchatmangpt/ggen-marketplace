#!/usr/bin/env python3
"""# MESSAGE: templates/ must be ontology-driven; banned domain literals or hardcoded
class identifiers are a refusal. Fail-closed: any hit exits 1; an unreadable template
file also exits 1."""
import pathlib, re, sys

BANNED = ("zcode", "xaas", "autofde", "ggen-marketplace", "praxis", "wasm4pm", "ex4pm", "affidavit")
# A projected class must come from the graph ({{ ... }}), never a hardcoded identifier.
HARDCODED_CLASS = re.compile(r"class\s+[A-Za-z_][A-Za-z0-9_]*\s*\(")


def scan(root: pathlib.Path) -> list[str]:
    hits = []
    tdir = root / "templates"
    if not tdir.is_dir():
        return [f"REFUSED[NO_TEMPLATES_DIR]: {tdir} missing — pack renders nothing"]
    for path in sorted(tdir.rglob("*")):
        if not path.is_file():
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except Exception as e:  # fail-closed on unreadable template
            hits.append(f"REFUSED[UNREADABLE_TEMPLATE]: {path.name}: {e}")
            continue
        for n, line in enumerate(lines, 1):
            for word in BANNED:
                if re.search(re.escape(word), line, re.IGNORECASE):
                    hits.append(f"REFUSED[BANNED_LITERAL]: {path.name}:{n}: {word}")
            # Class lines are lawful only when graph-driven (contain a Jinja binding).
            if HARDCODED_CLASS.search(line) and "{{" not in line:
                hits.append(f"REFUSED[HARDCODED_CLASS]: {path.name}:{n}: {line.strip()}")
    return hits


if __name__ == "__main__":
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parent.parent
    found = scan(root)
    print("\n".join(found) if found else "ALIVE: templates ontology-driven, no banned literals")
    raise SystemExit(1 if found else 0)
