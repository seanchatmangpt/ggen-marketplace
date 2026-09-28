#!/usr/bin/env python3
import argparse,hashlib,json
from pathlib import Path
RANK={"UNKNOWN":0,"CANDIDATE":1,"ADMITTED":2,"QUALIFIED":3,"PARTIAL_ALIVE":4,"ALIVE":5}
def digest(v): return "sha256:"+hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def qualify(root,p):
 r=[]
 if not root.get("exact_subject"): r.append("MISSING_ROOT_SUBJECT")
 if p.get("root_subject")!=root.get("exact_subject"): r.append("STALE_ROOT")
 if p.get("semantic_owner")!=root.get("semantic_owner"): r.append("OWNERSHIP_LAUNDERING")
 if p.get("authority")!="NONE": r.append("AUTHORITY_WIDENING")
 s=root.get("standing","UNKNOWN"); c=p.get("standing","UNKNOWN")
 if s not in RANK or c not in RANK: r.append("UNKNOWN_STANDING")
 elif RANK[c]>RANK[s]: r.append("STANDING_PROMOTION")
 missing=sorted(set(root.get("required_terms",[]))-set(p.get("projected_terms",[])))
 if missing:r.append("SEMANTIC_TERM_LOSS")
 m={"root_subject":root.get("exact_subject"),"consumer_subject":p.get("exact_subject"),"consumer_repo":p.get("consumer_repo"),"projected_terms":sorted(p.get("projected_terms",[]))}
 md=digest(m)
 if p.get("mapping_digest")!=md:r.append("MAPPING_DRIFT")
 out={"schema":"ggen-marketplace.ea-projection-court.v1","root_subject":root.get("exact_subject"),"consumer_subject":p.get("exact_subject"),"consumer_repo":p.get("consumer_repo"),"source_standing":s,"claimed_standing":c,"mapping_digest":md,"missing_terms":missing,"refusals":sorted(set(r)),"standing":"REFUSED" if r else "QUALIFIED_PROJECTION","authority":"NONE"}
 out["receipt_digest"]=digest(out);return out
def main():
 a=argparse.ArgumentParser();a.add_argument("root");a.add_argument("projection");a.add_argument("--expect-refusal");x=a.parse_args()
 root=json.loads(Path(x.root).read_text());p=json.loads(Path(x.projection).read_text());one=qualify(root,p)
 if one!=qualify(root,p):return 3
 print(json.dumps(one,sort_keys=True,separators=(",",":")))
 return (0 if x.expect_refusal in one["refusals"] else 4) if x.expect_refusal else (0 if not one["refusals"] else 2)
if __name__=="__main__":raise SystemExit(main())
