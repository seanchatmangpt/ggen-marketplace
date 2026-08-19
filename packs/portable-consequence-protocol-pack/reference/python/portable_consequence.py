#!/usr/bin/env python3
"""Dependency-free witness for portable-consequence/1; no authority or actuation."""
from __future__ import annotations
import json, sys
from typing import Any

def refused(code: str) -> dict[str,str]: return {"disposition":"REFUSED","code":f"REFUSED:{code}"}

def admit(r: dict[str,Any]) -> dict[str,str]:
    i=r.get("intent") or {}; c=r.get("consequence") or {}; a=r.get("authority"); rc=r.get("receipt_capability") or {}
    if i.get("mode") != "DO": return refused("NOT_CONSEQUENTIAL_DO")
    if not c.get("digest"): return refused("CONSEQUENCE_IDENTITY_REQUIRED")
    if not i.get("replay_key"): return refused("REPLAY_KEY_REQUIRED")
    if not a: return refused("AUTHORITY_REQUIRED")
    if a.get("decision") != "ALLOW" or not a.get("decision_id"): return refused("AUTHORITY_DENIED")
    if a.get("consequence_digest") != c.get("digest"): return refused("AUTHORITY_SCOPE_MISMATCH")
    if rc.get("available") is not True: return refused("RECEIPT_CAPABILITY_REQUIRED")
    if not rc.get("digest_algorithm") or not rc.get("replay_scheme"): return refused("RECEIPT_CAPABILITY_INCOMPLETE")
    return {"disposition":"ADMITTED","code":"ALLOWED"}

def verify_receipt(r: dict[str,Any]) -> dict[str,str]:
    c=r.get("consequence") or {}; a=r.get("authority") or {}; o=r.get("observation") or {}; x=r.get("receipt") or {}; d=c.get("digest")
    if not d or a.get("consequence_digest") != d: return refused("AUTHORITY_SCOPE_MISMATCH")
    if o.get("consequence_digest") != d: return refused("OBSERVATION_CONSEQUENCE_MISMATCH")
    if x.get("consequence_digest") != d: return refused("RECEIPT_CONSEQUENCE_MISMATCH")
    if x.get("authority_decision_id") != a.get("decision_id"): return refused("RECEIPT_AUTHORITY_MISMATCH")
    if x.get("observation_digest") != o.get("digest"): return refused("RECEIPT_OBSERVATION_MISMATCH")
    if not x.get("replay_key"): return refused("REPLAY_KEY_REQUIRED")
    return {"disposition":"VERIFIED","code":"RECEIPT_VALID"}

def replay(r: dict[str,Any]) -> dict[str,str]:
    o=r.get("original") or {}; c=r.get("candidate") or {}
    if not o.get("replay_key") or o.get("replay_key") != c.get("replay_key"): return refused("REPLAY_KEY_MISMATCH")
    if o.get("consequence_digest") != c.get("consequence_digest"): return refused("REPLAY_KEY_CONFLICT")
    if not o.get("receipt_digest"): return refused("ORIGINAL_RECEIPT_REQUIRED")
    return {"disposition":"REPLAY","code":"REPLAY_MATCH"}

def evaluate(r: dict[str,Any]) -> dict[str,str]:
    return {"admit":admit,"verify_receipt":verify_receipt,"replay":replay}.get(r.get("op"),lambda _r: refused("UNSUPPORTED_OPERATION"))(r)

def main() -> int:
    try:
        r=json.load(sys.stdin)
        if not isinstance(r,dict): raise ValueError("object required")
        out=evaluate(r)
    except Exception as exc:
        out={"disposition":"REFUSED","code":"REFUSED:MALFORMED_REQUEST","detail":type(exc).__name__}
    json.dump(out,sys.stdout,sort_keys=True,separators=(",",":")); sys.stdout.write("\n"); return 0

if __name__ == "__main__": raise SystemExit(main())
