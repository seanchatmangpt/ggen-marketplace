from pathlib import Path

ROOT = Path(__file__).parents[1]
TEMPLATES = [
    ROOT / "templates" / "option-observability-r27.json.tera",
    ROOT / "templates" / "option-observability-r27-court.py.tera",
]

for path in TEMPLATES:
    text = path.read_text()
    assert 'default(value=\\"' not in text, f"REFUSED[ESCAPED_TERA_DEFAULT]:{path.name}"
    assert 'default(value="UNKNOWN")' in text, f"REFUSED[MISSING_TERA_DEFAULT]:{path.name}"
