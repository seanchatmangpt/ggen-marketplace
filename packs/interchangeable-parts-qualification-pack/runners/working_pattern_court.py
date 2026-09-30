#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys, tempfile
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PACK_ROOT / "working-patterns" / "source"
NEGATIVE_DIR = PACK_ROOT / "working-patterns" / "negative"
RENDERED_DIR = PACK_ROOT / "working-patterns" / "rendered"
REQUIRED_TOP = {"pattern_id","source_pack","source_evidence","capability","contract","procedure","context","required_invariants","realizations"}
REQUIRED_REALIZATION = {"id","artifact","evidence","preserves","authority_evidence"}

class Refusal(ValueError): pass

def canonical_json(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True, separators=(",", ": ")) + "\n"

def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def validate_source(doc: dict) -> None:
    missing = sorted(REQUIRED_TOP - doc.keys())
    if missing: raise Refusal("MISSING_TOP_LEVEL:" + ",".join(missing))
    if not isinstance(doc["source_evidence"], dict) or not doc["source_evidence"]:
        raise Refusal("MISSING_SOURCE_EVIDENCE")
    rs = doc["realizations"]
    if not isinstance(rs, list) or len(rs) != 2:
        raise Refusal("REQUIRES_EXACTLY_TWO_REALIZATIONS")
    required = set(doc["required_invariants"])
    if not required: raise Refusal("EMPTY_INVARIANT_SET")
    ids = []
    for item in rs:
        if not isinstance(item, dict): raise Refusal("REALIZATION_NOT_OBJECT")
        missing_r = sorted(REQUIRED_REALIZATION - item.keys())
        if missing_r: raise Refusal("MISSING_REALIZATION_FIELDS:" + ",".join(missing_r))
        ids.append(item["id"])
        missing_i = sorted(required - set(item["preserves"]))
        if missing_i:
            raise Refusal(f"MISSING_REQUIRED_INVARIANT:{item['id']}:" + ",".join(missing_i))
    if len(set(ids)) != 2: raise Refusal("REALIZATIONS_NOT_DISTINCT")

def project(doc: dict) -> dict:
    validate_source(doc)
    x = doc["context"]["id"]
    qs, ds, ss = [], [], []
    for index, item in enumerate(doc["realizations"], start=1):
        qid=f"{doc['pattern_id']}#qualification-{index}"
        did=f"{doc['pattern_id']}#admission-{index}"
        sid=f"{doc['pattern_id']}#standing-{index}"
        qs.append({"id":qid,"subject_realization":item["id"],"contract":doc["contract"],"context":x,
                   "verdict":"Pass","evidence":item["evidence"],"preserves":sorted(item["preserves"])})
        ds.append({"id":did,"qualification":qid,"decision":"Permit","authority_evidence":item["authority_evidence"]})
        ss.append({"id":sid,"standing_of":item["id"],"contract":doc["contract"],"context":x,
                   "state":"Admitted","based_on_qualification":qid,"supersedes":None})
    payload={
      "schema":"ggen.qri-working-pattern/1","pattern_id":doc["pattern_id"],"source_pack":doc["source_pack"],
      "source_evidence":doc["source_evidence"],"capability":doc["capability"],"contract":doc["contract"],
      "procedure":doc["procedure"],"context":doc["context"],"required_invariants":sorted(doc["required_invariants"]),
      "realizations":[{"id":i["id"],"artifact":i["artifact"]} for i in doc["realizations"]],
      "qualifications":qs,
      "interchangeability":{"members":sorted(i["id"] for i in doc["realizations"]),"contract":doc["contract"],
        "context":x,"based_on_qualification":sorted(q["id"] for q in qs),"preserves":sorted(doc["required_invariants"])},
      "admissions":ds,"standing_heads":ss
    }
    payload["receipt"]={"algorithm":"sha256","digest":digest(payload),"claim":"qualified-runtime-interchangeability"}
    return payload

def generated_bytes(source_path: Path) -> str:
    return canonical_json(project(json.loads(source_path.read_text(encoding="utf-8"))))

def overwrite(target_dir: Path) -> list[str]:
    target_dir.mkdir(parents=True, exist_ok=True)
    names=[]; expected=set()
    for src in sorted(SOURCE_DIR.glob("*.json")):
        name=src.stem+".qri.json"; expected.add(name)
        (target_dir/name).write_text(generated_bytes(src), encoding="utf-8"); names.append(name)
    for stale in target_dir.glob("*.qri.json"):
        if stale.name not in expected: stale.unlink()
    return names

def negative_court() -> list[str]:
    failures=[]
    for src in sorted(NEGATIVE_DIR.glob("*.json")):
        try: generated_bytes(src)
        except Refusal: continue
        failures.append("NEGATIVE_ACCEPTED:"+src.name)
    return failures

def check() -> int:
    with tempfile.TemporaryDirectory(prefix="qri-working-patterns-") as tmp:
        scratch=Path(tmp); names=overwrite(scratch); failures=negative_court()
        for name in names:
            expected, actual=RENDERED_DIR/name, scratch/name
            if not expected.is_file(): failures.append("MISSING_RENDERED:"+name)
            elif expected.read_bytes()!=actual.read_bytes(): failures.append("DRIFT:"+name)
        committed=sorted(p.name for p in RENDERED_DIR.glob("*.qri.json"))
        if committed!=sorted(names): failures.append("RENDERED_SET_DRIFT")
        payload={"schema":"ggen.qri-working-pattern-court/1","standing":"REFUSED" if failures else "ALIVE",
                 "patterns":names,"negative_cases":sorted(p.name for p in NEGATIVE_DIR.glob("*.json"))}
        if failures:
            payload["failures"]=failures
            print(json.dumps(payload,sort_keys=True),file=sys.stderr); return 2
        print(json.dumps(payload,sort_keys=True)); return 0

def main() -> int:
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--overwrite",action="store_true"); mode.add_argument("--check",action="store_true")
    args=parser.parse_args()
    try:
        if args.overwrite:
            names=overwrite(RENDERED_DIR)
            print(json.dumps({"standing":"ALIVE","overwritten":names},sort_keys=True)); return 0
        return check()
    except (OSError,json.JSONDecodeError,Refusal) as error:
        print(json.dumps({"standing":"REFUSED","error":str(error)},sort_keys=True),file=sys.stderr); return 2
if __name__=="__main__":
    raise SystemExit(main())
