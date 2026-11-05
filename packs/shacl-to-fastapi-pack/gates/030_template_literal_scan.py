#!/usr/bin/env python3
"""# MESSAGE: templates/ must be ontology-driven; banned domain literals or hardcoded
route/model identifiers are a refusal. Fail-closed: any hit exits 1; an unreadable template
file also exits 1."""
import pathlib, re, sys

BANNED = ("zcode", "xaas", "autofde", "ggen-marketplace", "praxis", "wasm4pm", "ex4pm", "affidavit")
# A projected route/handler must come from the graph ({{ ... }}), never hardcoded.
HARDCODED_DEF = re.compile(r"def\s+[A-Za-z_][A-Za-z0-9_]*\s*\(")
HARDCODED_ROUTE = re.compile(r"@APIRouter|@router\.|APIRouter\(\)\.deco")

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
            hits.append(f"REFUSED[030_UNREADABLE_TEMPLATE]: {path.name}: {e}")
            continue
        for n, line in enumerate(lines, 1):
            for word in BANNED:
                if re.search(re.escape(word), line, re.IGNORECASE):
                    hits.append(
                    f"REFUSED[030_BANNED_LITERAL]: {path.name}:{n}: {word}"
                )
            # Handler defs / route decorators are lawful only when graph-driven
            # (the line carries a Jinja binding).
            if (HARDCODED_DEF.search(line) or HARDCODED_ROUTE.search(line)) and "{{" not in line:
                hits.append(f"REFUSED[030_HARDCODED_ROUTE]: {path.name}:{n}: {line.strip()}")
    return hits

if __name__ == "__main__":
    default_root = pathlib.Path(__file__).resolve().parent.parent
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else default_root
    found = scan(root)
    print("\n".join(found) if found else "ALIVE: templates ontology-driven, no banned literals")
    raise SystemExit(1 if found else 0)
