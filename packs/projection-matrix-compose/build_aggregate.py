#!/usr/bin/env python3
"""Regenerate the root ontology.ttl aggregate from the ontology/ modules.

Canonical inputs (in order): ontology/core.ttl, ontology/bindings.ttl,
ontology/cs2-adapter.ttl. The root ontology.ttl is a GENERATED projection
(autofde-semantic-registry-pack convention): edit a module, re-run
`python3.11 build_aggregate.py`, never hand-edit the aggregate. Deterministic:
same module bytes -> byte-identical aggregate (byte-identical replay is the
ggen qualification contract).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULES = ("core.ttl", "bindings.ttl", "cs2-adapter.ttl")


def main() -> int:
    parts = [
        "# GENERATED AGGREGATE — DO NOT EDIT DIRECTLY.",
        f"# Canonical inputs: ontology/{MODULES[0]} … ontology/{MODULES[-1]} (full ordered list in build_aggregate.py).",
        "# Replay: python3.11 build_aggregate.py",
        "",
    ]
    for name in MODULES:
        text = (ROOT / "ontology" / name).read_text(encoding="utf-8")
        parts.append(f"# ===== SOURCE: ontology/{name} =====\n")
        parts.append(text if text.endswith("\n") else text + "\n")
        parts.append("\n")
    (ROOT / "ontology.ttl").write_text("".join(parts), encoding="utf-8")
    print(f"aggregated {len(MODULES)} modules -> ontology.ttl")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
