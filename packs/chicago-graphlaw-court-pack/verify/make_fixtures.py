#!/usr/bin/env python3
"""Regenerate verify/fixtures/*.ttl and witnesses/{pass,fail}/*.ttl (hand-maintained tooling
for the pack's own self-proof; the case corpora cases/a.ttl and cases/b.ttl are NOT touched)."""
import json, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
HDR = ("@prefix cc: <https://chicago.graphlaw.dev/court#> .\n"
       "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")

def lit(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'

N3 = "@prefix : <urn:x:> .\n:a :p :b .\n{ ?x :p ?y } => { ?y :q ?x } ."
N3_NORULE = "@prefix : <urn:x:> .\n:a :p :b ."
POS_REQ = json.dumps({"op": "n3", "text": N3})
POS_EXP = json.dumps([{"ptr": "/ok", "eq": True}, {"ptr": "/derived", "contains": ":b :q :a"}])
NEG_REQ = json.dumps({"op": "n3", "text": "{ ?x a } =>"})
NEG_EXP = json.dumps([{"ptr": "/ok", "eq": False}])
MUT_REQ = json.dumps({"op": "n3", "text": N3_NORULE})
MUT_EXP_OK = json.dumps([{"ptr": "/ok", "eq": True}, {"ptr": "/derived", "eq": ""}])
CMP = json.dumps([{"a": "/derived", "rel": "eq", "b": "/derived"}])

def case(court, pfx, ordinal, cid, kind, req, exp, extra=""):
    cls = {"positive": "Positive", "negative": "Negative", "invariance": "Invariance",
           "cross-authority": "CrossAuthority", "boundary-mutation": "BoundaryMutation"}[kind]
    return (f"cc:case_{cid} a cc:{cls}Case, cc:Case ;\n  cc:court cc:{court} ; cc:caseId {lit(cid)} ; cc:ordinal {ordinal} ;\n"
            f"  cc:kind {lit(kind)} ; cc:title {lit('min fixture ' + kind)} ; cc:op \"n3\" ;\n"
            f"  cc:request {lit(req)} ;\n  cc:expect {lit(exp)} ;\n  cc:coversAxiom cc:ax_min ; cc:ceiling \"observe\"{extra} .\n\n")

def court_block(court, pfx, base):
    out = ""
    out += case(court, pfx, base + 1, f"{pfx}_pos", "positive", POS_REQ, POS_EXP)
    out += case(court, pfx, base + 2, f"{pfx}_neg", "negative", NEG_REQ, NEG_EXP)
    out += case(court, pfx, base + 3, f"{pfx}_inv", "invariance", POS_REQ, POS_EXP,
                f' ;\n  cc:requestB {lit(POS_REQ)} ;\n  cc:expectB {lit(POS_EXP)} ;\n  cc:compare {lit(CMP)}')
    out += case(court, pfx, base + 4, f"{pfx}_xa", "cross-authority", POS_REQ, POS_EXP,
                f' ;\n  cc:requestB {lit(POS_REQ)} ;\n  cc:compare {lit(CMP)}')
    out += case(court, pfx, base + 5, f"{pfx}_mut", "boundary-mutation", MUT_REQ, MUT_EXP_OK,
                f' ;\n  cc:mutates cc:case_{pfx}_pos')
    return out

AX = 'cc:ax_min a cc:Axiom ; cc:source "verify/fixtures: synthetic self-proof axiom" .\n\n'

def base_graph(mut=lambda s: s):
    return HDR + AX + court_block("cross_authority_court", "xa", 0) + court_block("fibo_court", "fibo", 500)

# NOTE: boundary-mutation expectation must differ from its base expectation: base expects a
# derived q, the mutant only asserts ok.
(ROOT / "verify/fixtures/cases_min.ttl").write_text(base_graph())
bad = base_graph().replace('cc:kind "negative"', 'cc:kind "wrongkind"', 1)
(ROOT / "verify/fixtures/cases_bad.ttl").write_text(bad)

# ---- witnesses: pass = base graph; fail = one targeted mutation per gate -----------------
def rep(s, a, b, n=1):
    assert a in s, a
    return s.replace(a, b, n)

BASE = base_graph()
FAIL = {
 "010_court_authority_none": BASE + 'cc:w_court a cc:Court ; cc:courtId "w" ; cc:testFile "tests/w.rs" ; cc:authority "ADMIT" ; cc:consequence "EVIDENCE_ONLY" .\n',
 "020_case_required_fields": BASE + 'cc:case_w_bare a cc:PositiveCase, cc:Case ; cc:court cc:fibo_court .\n',
 "030_kind_matches_class": rep(BASE, 'cc:kind "negative"', 'cc:kind "positive"'),
 "040_caseid_format": rep(BASE, 'cc:caseId "xa_pos"', 'cc:caseId "XA-Pos"'),
 "050_caseid_unique": rep(BASE, 'cc:caseId "xa_neg"', 'cc:caseId "xa_pos"'),
 "060_ordinal_unique": rep(BASE, "cc:ordinal 2 ;", "cc:ordinal 1 ;"),
 "070_ordinal_range_per_court": rep(BASE, "cc:ordinal 501 ;", "cc:ordinal 5 ;"),
 "080_axiom_declared_with_source": rep(BASE, 'cc:ax_min a cc:Axiom ; cc:source "verify/fixtures: synthetic self-proof axiom" .', 'cc:ax_min a cc:Axiom .'),
 "090_kind_coverage_per_court": BASE.split("cc:case_fibo_pos")[0] + "\n",
 "100_boundary_mutation_distinct_from_base": rep(BASE, f"cc:expect {lit(MUT_EXP_OK)}", f"cc:expect {lit(POS_EXP)}"),
 "110_ceiling_enumerated": rep(BASE, 'cc:ceiling "observe"', 'cc:ceiling "actuate"'),
 "120_byte_identity_single_request": rep(BASE, "cc:ceiling \"observe\" .\n\ncc:case_xa_neg", "cc:ceiling \"observe\" ; cc:byteIdentity true .\n\ncc:case_xa_neg").replace(
     f"cc:request {lit(POS_REQ)} ;\n  cc:expect {lit(POS_EXP)} ;\n  cc:coversAxiom cc:ax_min ; cc:ceiling \"observe\" ; cc:byteIdentity true",
     f"cc:request {lit('[' + POS_REQ + ']')} ;\n  cc:expect {lit(POS_EXP)} ;\n  cc:coversAxiom cc:ax_min ; cc:ceiling \"observe\" ; cc:byteIdentity true", 1),
 "130_compare_pairs_with_request_b": rep(BASE, f" ;\n  cc:requestB {lit(POS_REQ)} ;\n  cc:expectB {lit(POS_EXP)}", ""),
}
FAIL["140_fibo_threshold_policy"] = BASE + "cc:fibo_court cc:thresholdMicros 5000 .\n"
gates = sorted(p.stem for p in (ROOT / "gates").glob("*.rq"))
for g in gates:
    (ROOT / "witnesses/pass" / f"{g}.ttl").write_text(BASE)
    body = FAIL[g]
    (ROOT / "witnesses/fail" / f"{g}.ttl").write_text(body)
print("fixtures + witnesses written:", len(gates), "gates")
