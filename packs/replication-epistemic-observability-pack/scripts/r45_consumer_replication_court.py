#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
QUERY_DIR = ROOT / "queries"
SENSORS = sorted(p for p in QUERY_DIR.glob("*.rq") if 86 <= int(p.name.split("_")[0]) <= 135)

assert len(SENSORS) == 50, f"expected 50 R45 sensors, found {len(SENSORS)}"
for path in SENSORS:
    text = path.read_text()
    assert "SELECT" in text, f"non-query sensor: {path.name}"
    assert "https://ggen.dev/ontology/replication-epistemic#" in text, f"foreign ontology: {path.name}"
    assert len(text.strip()) > 80, f"vacuous sensor: {path.name}"
    assert not re.search(r"(?im)^\s*(INSERT|DELETE|LOAD|CLEAR|DROP|CREATE|COPY|MOVE|ADD)\b", text), f"ambient update authority: {path.name}"

print(f"R45_CONSUMER_REPLICATION_COURT=ALIVE sensors={len(SENSORS)} actuation_performed=false")
