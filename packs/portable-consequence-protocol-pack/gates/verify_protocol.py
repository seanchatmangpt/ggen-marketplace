#!/usr/bin/env python3
"""Independent process court for portable-consequence/1."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT=ROOT/"reference"/"python"/"portable_consequence.py"

def run(command:list[str], request:dict)->dict:
    p=subprocess.run(command,input=json.dumps(request,sort_keys=True),text=True,capture_output=True,check=False,timeout=5)
    if p.returncode: raise AssertionError(f"implementation exit={p.returncode}: {p.stderr}")
    lines=[x for x in p.stdout.splitlines() if x.strip()]
    if len(lines)!=1: raise AssertionError(f"expected one JSON response, got {len(lines)}")
    out=json.loads(lines[0])
    if not isinstance(out,dict): raise AssertionError("response must be object")
    return out

def verify(command:list[str])->dict:
    contract=json.loads((ROOT/"contract"/"protocol.json").read_text())
    vectors=json.loads((ROOT/"vectors"/"conformance.json").read_text())
    assert contract["protocol"]=="portable-consequence/1"
    assert contract["laws"]["ambient_authority"] is False
    assert contract["laws"]["receiptability_precedes_do"] is True
    passed=[]
    for v in vectors:
        actual=run(command,v["request"])
        for k,val in v["expect"].items():
            if actual.get(k)!=val: raise AssertionError(f"{v['id']}: {k} expected {val!r}, got {actual.get(k)!r}: {actual!r}")
        passed.append(v["id"])
    return {"protocol":contract["protocol"],"status":"PARTIAL_ALIVE","vectors":len(passed),"passed":passed}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("command",nargs="*"); args=ap.parse_args()
    print(json.dumps(verify(args.command or [sys.executable,str(DEFAULT)]),sort_keys=True,separators=(",",":")))
    return 0
if __name__=="__main__": raise SystemExit(main())
