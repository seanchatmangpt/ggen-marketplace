#!/usr/bin/env python3
"""Subject integrity court (L3) - exact-subject law over the R2 machine projection.

Subject is identity: the header subject, every case subject and the cross-projection
subject must be the exact literal "urn:chicago:agentic-payment:purchase-001" (falsifier
'subject drift'). Run: python3 test/test_subject_integrity.py [rendered_dir]
"""
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import courts  # noqa: E402


def run(rendered_dir):
    errs = []
    docs, missing = courts.all_four_docs(rendered_dir)
    errs += missing
    machine = docs.get("machine")
    if machine:
        errs += courts.header_errors(machine, expected_type="machine", label="machine")
        root = machine.get("rootGoal")
        if not isinstance(root, dict):
            errs.append("machine: rootGoal must be an object")
        else:
            if root.get("identifier") != "GC-XAAS-26.10.1-CHICAGO":
                errs.append(f"machine.rootGoal: identifier {root.get('identifier')!r} != GC-XAAS-26.10.1-CHICAGO")
            if root.get("repository") != "seanchatmangpt/xaas":
                errs.append(f"machine.rootGoal: repository {root.get('repository')!r} != seanchatmangpt/xaas")
            if not courts.HEX40.match(str(root.get("baseSha", ""))):
                errs.append(f"machine.rootGoal: baseSha {root.get('baseSha')!r} is not a 40-hex sha")
            if root.get("authorityCeiling") != "CONSTRUCT":
                errs.append(f"machine.rootGoal: authorityCeiling {root.get('authorityCeiling')!r} != CONSTRUCT")
            if not courts.nonempty_str(root.get("evidenceHorizon")):
                errs.append("machine.rootGoal: evidenceHorizon must be a non-empty string")
            if not courts.nonempty_str(root.get("replayIdentity")):
                errs.append("machine.rootGoal: replayIdentity must be a non-empty string")
        cases = machine.get("cases")
        if not isinstance(cases, list) or not cases:
            errs.append("machine: cases must be a non-empty array")
        else:
            seen = set()
            for case in cases:
                cid = case.get("id")
                if cid in seen:
                    errs.append(f"machine.cases: duplicate case id {cid!r}")
                seen.add(cid)
                if case.get("subject") != courts.EXACT_SUBJECT:
                    errs.append(f"machine.cases[{cid}]: subject drift: {case.get('subject')!r}")
                if case.get("candidateOnly") is not True:
                    errs.append(f"machine.cases[{cid}]: candidateOnly must be true (cases are predictions)")
                if case.get("authorityClaim") != "NONE":
                    errs.append(f"machine.cases[{cid}]: authorityClaim must be NONE")
                if case.get("observedStanding") not in courts.STANDING_VOCAB:
                    errs.append(f"machine.cases[{cid}]: observedStanding {case.get('observedStanding')!r} outside standing vocabulary")
                if case.get("observedStanding") != "UNKNOWN":
                    errs.append(f"machine.cases[{cid}]: observedStanding must default to UNKNOWN (R8: no inherited standing)")
            for required in courts.CASE_IDS:
                if required not in seen:
                    errs.append(f"machine.cases: missing required case id {required}")
    # cross-projection subject drift
    for ptype, doc in sorted(docs.items()):
        if doc.get("subject") != courts.EXACT_SUBJECT:
            errs.append(f"{ptype}: header subject drift: {doc.get('subject')!r}")
    return errs


def selftest(rendered_dir):
    """Anti-vacuity: a machine doc with a drifted subject MUST fire this court."""
    docs, _ = courts.all_four_docs(rendered_dir)
    if "machine" not in docs:
        return ["selftest skipped: no machine.json fixture"]
    mutated = json.loads(json.dumps(docs["machine"]))
    cases = mutated.get("cases") or [{}]
    cases[0]["subject"] = "urn:chicago:agentic-payment:purchase-999"
    with tempfile.TemporaryDirectory() as tmp:
        pathlib.Path(tmp, "machine.json").write_text(json.dumps(mutated))
        for ptype in ("verification", "executive", "replay"):
            if ptype in docs:
                pathlib.Path(tmp, f"{ptype}.json").write_text(json.dumps(docs[ptype]))
        fired = bool(run(tmp))
    return [] if fired else ["selftest: subject drift mutation did NOT fire the court (admission vacuous)"]


if __name__ == "__main__":
    rendered = sys.argv[1] if len(sys.argv) > 1 else str(courts.RENDERED_CANONICAL)
    errors = run(rendered) + selftest(rendered)
    for err in errors:
        print(f"VIOLATION: {err}")
    print("RESULT:", "REFUSED" if errors else "SUBJECT_INTEGRITY_OK", f"({len(errors)} problems)")
    sys.exit(1 if errors else 0)
