#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import sys

try:
    import tomllib
except ImportError as exc:
    raise SystemExit("Python 3.11+ required") from exc

ALLOWED_KINDS = {
    "ontology", "taxonomy", "controlled-vocabulary-family", "rights-vocabulary",
    "schema", "schema-standard", "ontology-schema", "protocol-schema",
    "schema-protocol", "semantic-conventions", "provider-schema", "knowledge-base",
    "risk-taxonomy", "process-standard", "decision-standard",
    "enterprise-architecture-standard", "secure-sdl-standard", "secure-sdl-model",
    "application-security-standard",
}
ALLOWED_MODES = {"vendor", "project", "reference"}


def main() -> int:
    path = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "sources.lock.toml")
    doc = tomllib.loads(path.read_text(encoding="utf-8"))
    sources = doc.get("source", [])
    ids: set[str] = set()
    errors: list[str] = []
    for i, source in enumerate(sources, 1):
        sid = source.get("id")
        if not sid:
            errors.append(f"source[{i}] missing id")
            continue
        if sid in ids:
            errors.append(f"duplicate id: {sid}")
        ids.add(sid)
        if source.get("kind") not in ALLOWED_KINDS:
            errors.append(f"{sid}: unsupported kind {source.get('kind')!r}")
        if source.get("mode") not in ALLOWED_MODES:
            errors.append(f"{sid}: unsupported mode {source.get('mode')!r}")
        if not source.get("canonical"):
            errors.append(f"{sid}: missing canonical authority URL")
        if not source.get("steward"):
            errors.append(f"{sid}: missing steward")
        if not source.get("license"):
            errors.append(f"{sid}: missing license standing")
        if source.get("mode") == "vendor" and not source.get("retrieval_url"):
            errors.append(f"{sid}: vendor source missing retrieval_url")
    if errors:
        print("REFUSED")
        for error in errors:
            print(f"- {error}")
        return 2
    print(f"ALIVE: {len(sources)} public semantic source records; {len(ids)} unique ids")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
