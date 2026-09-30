#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys, tomllib
from pathlib import Path
PACK_ROOT = Path(__file__).resolve().parents[1]
def main() -> int:
    court = tomllib.loads((PACK_ROOT / "gate-court.toml").read_text(encoding="utf-8"))["court"]
    runner = court["runner"].split()
    failures, executed = [], []
    for gate in sorted((PACK_ROOT / court["gate_dir"]).glob("*.rq")):
        for expectation in ("pass", "fail"):
            witness = PACK_ROOT / court[f"{expectation}_dir"] / f"{gate.stem}.ttl"
            argv = [token.format(gate=str(gate), witness=str(witness), expectation=expectation) for token in runner]
            result = subprocess.run(argv, cwd=PACK_ROOT, text=True, capture_output=True)
            executed.append({"gate":gate.stem,"expectation":expectation,"returncode":result.returncode})
            if result.returncode != 0:
                failures.append({"gate":gate.stem,"expectation":expectation,"stdout":result.stdout.strip(),"stderr":result.stderr.strip()})
    payload={"schema":"ggen.qri-semantic-court/1","executed":executed,"standing":"REFUSED" if failures else "ALIVE"}
    if failures:
        payload["failures"]=failures; print(json.dumps(payload,sort_keys=True),file=sys.stderr); return 2
    print(json.dumps(payload,sort_keys=True)); return 0
if __name__ == "__main__":
    raise SystemExit(main())
