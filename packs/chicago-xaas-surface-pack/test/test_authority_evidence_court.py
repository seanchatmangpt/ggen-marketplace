#!/usr/bin/env python3
"""Authority + evidence court (L3) - authority NONE and standing law across all four
projections (R2) and the executive schema (R3).

Laws: every header carries authorityClaim NONE and the exact subject (no cross-projection
drift); executive `demonstrated` counts only receipt-backed layers (empty until real
receipts); scenarios are CHI-CASE-001..010 with CHI-CASE-001 positive and 002..010 negative
carrying exactly the R4 typed refusal atoms; failureRecovery covers every case; evidence is
layer-keyed with standing UNKNOWN until receipts; deliveryState requiredLayers == 10 and
overallStanding UNKNOWN; the token "contained" (pre-judged outcome, R8) never appears.
Run: python3 test/test_authority_evidence_court.py [rendered_dir]
"""
import copy
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import courts  # noqa: E402

STANDING_FIELDS = ("standing", "overallStanding", "status", "observedStanding", "lifecycle")


def _prejudged_outcomes(node):
    """Standing-shaped fields must never carry pre-judged outcome values (R8)."""
    hits = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in STANDING_FIELDS and isinstance(value, str) and value.lower() == "contained":
                hits.append(key)
            else:
                hits += _prejudged_outcomes(value)
    elif isinstance(node, list):
        for value in node:
            hits += _prejudged_outcomes(value)
    return hits


def run(rendered_dir):
    errs = []
    docs, missing = courts.all_four_docs(rendered_dir)
    errs += missing

    subjects = {}
    for ptype, doc in sorted(docs.items()):
        errs += courts.header_errors(doc, expected_type=None, label=ptype)
        subjects[ptype] = doc.get("subject")
    if len(set(subjects.values())) > 1:
        errs.append(f"cross-projection subject drift: {subjects}")
    for ptype, doc in docs.items():
        if _prejudged_outcomes(doc):
            errs.append(f"{ptype}: pre-judged outcome value 'contained' in a standing-shaped field (R8)")

    executive = docs.get("executive")
    if executive:
        capabilities = executive.get("capabilities")
        if not isinstance(capabilities, list):
            errs.append("executive: capabilities must be an array")
        else:
            for capability_id in courts.REQUIRED_CAPABILITY_IDS + courts.SUCCESSOR_CAPABILITY_IDS:
                if capability_id not in capabilities:
                    errs.append(f"executive.capabilities: missing {capability_id!r} (10 required + wasm4pm/castle successor)")
        demonstrated = executive.get("demonstrated")
        if not isinstance(demonstrated, list):
            errs.append("executive: demonstrated must be an array")
        else:
            machine = docs.get("machine") or {}
            receipt_backed = {
                layer.get("id")
                for layer in machine.get("layers", [])
                if layer.get("status") == "ALIVE" and layer.get("receiptRefs")
            }
            for entry in demonstrated:
                if entry not in receipt_backed:
                    errs.append(f"executive.demonstrated: {entry!r} is not a receipt-backed ALIVE layer (R3/R8)")
        scenarios = executive.get("scenarios")
        if not isinstance(scenarios, list):
            errs.append("executive: scenarios must be an array")
        else:
            seen = {}
            for scenario in scenarios:
                sid = scenario.get("id")
                seen[sid] = scenario
                if sid not in courts.CASE_IDS:
                    errs.append(f"executive.scenarios: unknown case id {sid!r}")
                    continue
                if sid == courts.POSITIVE_CASE:
                    if scenario.get("polarity") != "positive":
                        errs.append(f"executive.scenarios[{sid}]: must be the positive path")
                    if scenario.get("refusal") is not None:
                        errs.append(f"executive.scenarios[{sid}]: positive path must not carry a refusal atom")
                else:
                    if scenario.get("polarity") != "negative":
                        errs.append(f"executive.scenarios[{sid}]: must be negative")
                    if scenario.get("refusal") != courts.CASE_REFUSALS[sid]:
                        errs.append(f"executive.scenarios[{sid}]: refusal {scenario.get('refusal')!r} != pinned {courts.CASE_REFUSALS[sid]!r}")
            for required in courts.CASE_IDS:
                if required not in seen:
                    errs.append(f"executive.scenarios: missing case {required}")
        recovery = executive.get("failureRecovery")
        if not isinstance(recovery, list):
            errs.append("executive: failureRecovery must be an array")
        else:
            covered = {entry.get("id") for entry in recovery}
            for required in courts.CASE_IDS:
                if required not in covered:
                    errs.append(f"executive.failureRecovery: no recovery for case {required}")
            for entry in recovery:
                if not courts.nonempty_str(entry.get("recovery")):
                    errs.append(f"executive.failureRecovery[{entry.get('id')}]: recovery must be a non-empty string")
        evidence = executive.get("evidence")
        if not isinstance(evidence, list):
            errs.append("executive: evidence must be an array")
        else:
            keyed = {}
            for entry in evidence:
                layer_id = entry.get("layer")
                if layer_id in keyed:
                    errs.append(f"executive.evidence: duplicate layer key {layer_id!r}")
                keyed[layer_id] = entry
                standing = entry.get("standing")
                if standing not in courts.STANDING_VOCAB:
                    errs.append(f"executive.evidence[{layer_id}]: standing {standing!r} outside standing vocabulary")
                if standing == "ALIVE" and not entry.get("receiptRefs"):
                    errs.append(f"executive.evidence[{layer_id}]: ALIVE without receiptRefs")
            for required in courts.REQUIRED_LAYER_IDS:
                if required not in keyed:
                    errs.append(f"executive.evidence: missing layer key {required!r}")
        delivery = executive.get("deliveryState")
        if not isinstance(delivery, dict):
            errs.append("executive: deliveryState must be an object")
        else:
            if delivery.get("requiredLayers") != len(courts.REQUIRED_LAYER_IDS):
                errs.append(f"executive.deliveryState: requiredLayers {delivery.get('requiredLayers')!r} != 10")
            if not isinstance(demonstrated, list) or delivery.get("demonstratedLayers") != len(demonstrated or []):
                errs.append("executive.deliveryState: demonstratedLayers must equal len(demonstrated)")
            if delivery.get("overallStanding") not in courts.STANDING_VOCAB:
                errs.append(f"executive.deliveryState: overallStanding {delivery.get('overallStanding')!r} outside vocabulary")
            if delivery.get("overallStanding") != "UNKNOWN" and not (demonstrated or []):
                errs.append("executive.deliveryState: overallStanding promoted without demonstrated receipt-backed layers")
    return errs


def selftest(rendered_dir):
    """Anti-vacuity: (a) a non-NONE header authority claim MUST fire; (b) an unbacked
    demonstrated entry MUST fire; (c) a negative scenario with an invented refusal
    atom MUST fire."""
    docs, _ = courts.all_four_docs(rendered_dir)
    if "executive" not in docs or "machine" not in docs:
        return ["selftest skipped: missing executive/machine fixtures"]
    gaps = []

    def write_set(tmp, mutate):
        mutated = copy.deepcopy(docs)
        mutate(mutated)
        for ptype, doc in mutated.items():
            pathlib.Path(tmp, f"{ptype}.json").write_text(json.dumps(doc))

    def fired(mutate, needle):
        with tempfile.TemporaryDirectory() as tmp:
            write_set(tmp, mutate)
            return any(needle in e for e in run(tmp))

    if not fired(lambda d: d["replay"].__setitem__("authorityClaim", "DO"), "authorityClaim"):
        gaps.append("selftest: authority-widening mutation did NOT fire (admission vacuous)")
    if not fired(lambda d: d["executive"].__setitem__("demonstrated", ["xaas"]), "demonstrated"):
        gaps.append("selftest: unbacked demonstrated mutation did NOT fire")
    if not fired(lambda d: d["executive"]["scenarios"][1].__setitem__("refusal", "made_up_refusal"), "refusal"):
        gaps.append("selftest: invented refusal atom did NOT fire")
    if not fired(lambda d: d["executive"]["deliveryState"].__setitem__("overallStanding", "contained"), "contained"):
        gaps.append("selftest: pre-judged 'contained' standing did NOT fire")
    return gaps


if __name__ == "__main__":
    rendered = sys.argv[1] if len(sys.argv) > 1 else str(courts.RENDERED_CANONICAL)
    errors = run(rendered) + selftest(rendered)
    for err in errors:
        print(f"VIOLATION: {err}")
    print("RESULT:", "REFUSED" if errors else "AUTHORITY_EVIDENCE_OK", f"({len(errors)} problems)")
    sys.exit(1 if errors else 0)
