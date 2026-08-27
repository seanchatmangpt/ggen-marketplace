#!/usr/bin/env python3
"""Independent stdlib court for Challenger value + ERRC innovation.

No network, customer discovery, irreversible selection, or consequential DO.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from typing import Any

ALLOWED_AUDIENCES={"cio-cto","ciso","cfo","platform","fortune5-buyer","hiring-manager"}
ALLOWED_KINDS={"OBSERVED","VERIFIED","INFERRED","HYPOTHESIS"}
PHASE_KIND={"TEACH":{"OBSERVED","VERIFIED"},"REFRAME":{"INFERRED","HYPOTHESIS","VERIFIED"},"RATIONAL_IMPACT":{"HYPOTHESIS","VERIFIED"},"NEW_WAY":{"OBSERVED","VERIFIED","INFERRED"},"PROOF":{"VERIFIED"}}
ERRC_ACTIONS={"ELIMINATE","REDUCE","RAISE","CREATE"}
DIAGNOSTICS={"cio-cto":"Can you trace one AI-generated production change from exact input through independent acceptance evidence and replay?","ciso":"Which controls are mechanically outside your agents' authority to change?","cfo":"Can you separate AI construction savings from the human verification cost created downstream?","platform":"Which platform invariants are generated from canonical semantics rather than synchronized by hand?","fortune5-buyer":"Which coordination steps could disappear if constraints, evidence, and handoffs were executable?","hiring-manager":"How do you evaluate engineers who operate software factories rather than manually author every artifact?"}

class Refusal(ValueError):
    def __init__(self,code:str,detail:str): self.code,self.detail=code,detail; super().__init__(f"REFUSED:{code}: {detail}")

def canonical_digest(value:Any)->str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def _validate_claim(claim:dict[str,Any])->None:
    phase,kind,text=str(claim.get("phase","")),str(claim.get("kind","")),str(claim.get("text","")).strip()
    if phase not in PHASE_KIND: raise Refusal("UNSUPPORTED_PHASE",phase)
    if kind not in ALLOWED_KINDS or kind not in PHASE_KIND[phase]: raise Refusal("UNSUPPORTED_CLAIM",f"{phase} cannot use {kind}")
    if not text: raise Refusal("EMPTY_CLAIM",phase)
    if claim.get("metric") and not claim.get("source"): raise Refusal("METRIC_WITHOUT_SOURCE",phase)
    if phase=="PROOF":
        if not claim.get("source"): raise Refusal("PROOF_WITHOUT_SOURCE",text)
        exact=str(claim.get("exact_subject",""))
        if len(exact)!=40 or any(ch not in "0123456789abcdef" for ch in exact.lower()): raise Refusal("PROOF_WITHOUT_EXACT_SUBJECT",text)
        if claim.get("standing")=="ALIVE" and claim.get("standing_evidence") is not True: raise Refusal("ALIVE_WITHOUT_STANDING",text)
    if claim.get("customer_outcome") and kind!="VERIFIED": raise Refusal("OUTCOME_AS_FACT",text)

def compile_errc(items:list[dict[str,Any]])->dict[str,Any]:
    if not items: raise Refusal("NO_ERRC_FACTORS","ERRC requires admitted factors")
    by_action={a:[] for a in ERRC_ACTIONS}; names=set()
    for raw in items:
        action=str(raw.get("action","")).upper(); factor=str(raw.get("factor","")).strip(); kind=str(raw.get("kind","")); rationale=str(raw.get("rationale","")).strip()
        if action not in ERRC_ACTIONS: raise Refusal("UNSUPPORTED_ERRC_ACTION",action)
        if not factor: raise Refusal("EMPTY_ERRC_FACTOR",action)
        if factor in names: raise Refusal("DUPLICATE_ERRC_FACTOR",factor)
        names.add(factor)
        if kind not in ALLOWED_KINDS: raise Refusal("UNSUPPORTED_ERRC_EVIDENCE",factor)
        if kind in {"OBSERVED","VERIFIED"} and not raw.get("source"): raise Refusal("ERRC_EVIDENCE_WITHOUT_SOURCE",factor)
        if not rationale: raise Refusal("ERRC_WITHOUT_RATIONALE",factor)
        if raw.get("score") is not None:
            score=raw["score"]
            if isinstance(score,bool) or not isinstance(score,(int,float)) or not 0<=score<=10: raise Refusal("ERRC_SCORE_OUT_OF_RANGE",factor)
            if not raw.get("source"): raise Refusal("ERRC_METRIC_WITHOUT_SOURCE",factor)
        if action=="CREATE" and not str(raw.get("experiment","")).strip(): raise Refusal("CREATE_WITHOUT_EXPERIMENT",factor)
        if action=="CREATE" and not str(raw.get("falsifier","")).strip(): raise Refusal("CREATE_WITHOUT_FALSIFIER",factor)
        if raw.get("actuation") is True: raise Refusal("ERRC_ACTUATION_FORBIDDEN",factor)
        item={"action":action,"factor":factor,"kind":kind,"rationale":rationale,"source":raw.get("source"),"score":raw.get("score"),"unit_iri":raw.get("unit_iri"),"experiment":raw.get("experiment"),"falsifier":raw.get("falsifier"),"actuation":False}
        by_action[action].append(item)
    missing=sorted(a for a,v in by_action.items() if not v)
    if missing: raise Refusal("INCOMPLETE_ERRC_GRID",",".join(missing))
    frontier={a:sorted(v,key=lambda x:(canonical_digest(x),x["factor"])) for a,v in sorted(by_action.items())}
    result={"protocol":"challenger-errc/1","frontier":frontier,"irreversible_selections":0,"actuation":False}
    result["receipt_sha256"]=canonical_digest(result); return result

def compile_brief(case:dict[str,Any])->dict[str,Any]:
    audience=str(case.get("audience",""))
    if audience not in ALLOWED_AUDIENCES: raise Refusal("UNSUPPORTED_AUDIENCE",audience)
    claims=list(case.get("claims") or [])
    if not claims: raise Refusal("NO_CLAIMS","at least one admitted claim is required")
    for claim in claims: _validate_claim(claim)
    by_phase={p:[] for p in PHASE_KIND}
    for claim in claims: by_phase[claim["phase"]].append(claim)
    for required in ("TEACH","REFRAME","RATIONAL_IMPACT","NEW_WAY","PROOF"):
        if not by_phase[required]: raise Refusal("MISSING_PHASE",required)
    frontier={p:sorted(items,key=lambda c:(canonical_digest(c),c["text"])) for p,items in by_phase.items()}; selected={p:items[0] for p,items in frontier.items()}
    brief={"protocol":"challenger-value/2","audience":audience,"teach":selected["TEACH"]["text"],"reframe":selected["REFRAME"]["text"],"rational_impact":selected["RATIONAL_IMPACT"]["text"],"new_way":selected["NEW_WAY"]["text"],"proof":selected["PROOF"]["text"],"take_control":DIAGNOSTICS[audience],"frontier":frontier,"irreversible_selections":0,"actuation":False}
    if "errc" in case: brief["innovation"]=compile_errc(list(case.get("errc") or []))
    brief["receipt_sha256"]=canonical_digest(brief); return brief

def run_vectors(path:Path)->int:
    payload=json.loads(path.read_text(encoding="utf-8")); passed=0
    for vector in payload["vectors"]:
        try: result=compile_brief(vector["case"])
        except Refusal as exc:
            if vector["expect"].get("refusal")!=exc.code: raise AssertionError(f"{vector['id']}: got {exc.code}") from exc
        else:
            if vector["expect"].get("status")!="ADMITTED": raise AssertionError(f"{vector['id']}: unexpectedly admitted")
            assert result==compile_brief(vector["case"]); assert result["actuation"] is False; assert result["irreversible_selections"]==0; assert len(result["receipt_sha256"])==64
            if "innovation" in result: assert set(result["innovation"]["frontier"])==ERRC_ACTIONS and result["innovation"]["actuation"] is False
        passed+=1
    print(json.dumps({"protocol":"challenger-value/2","standing":"ADMITTED","vectors_passed":passed},sort_keys=True)); return 0

def main()->int:
    parser=argparse.ArgumentParser(); parser.add_argument("--vectors",type=Path,default=Path(__file__).parents[2]/"vectors"/"conformance.json"); return run_vectors(parser.parse_args().vectors)
if __name__=="__main__": raise SystemExit(main())
