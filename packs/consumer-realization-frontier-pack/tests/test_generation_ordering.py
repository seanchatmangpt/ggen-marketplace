#!/usr/bin/env python3
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GGEN = (ROOT / "ggen.toml").read_text()
QUERY_DIR = ROOT / "queries"

files = re.findall(r'query\s*=\s*\{\s*file\s*=\s*"([^"]+)"\s*\}', GGEN)
failures = []
for rel in files:
    text = (ROOT / rel).read_text()
    if "SELECT" in text.upper() and "ORDER BY" not in text.upper():
        failures.append(rel)

if failures:
    print("REFUSED[NONDETERMINISTIC_GENERATION_QUERY]=" + ",".join(failures))
    sys.exit(1)

print(f"GENERATION_QUERY_ORDERING=ALIVE count={len(files)}")
