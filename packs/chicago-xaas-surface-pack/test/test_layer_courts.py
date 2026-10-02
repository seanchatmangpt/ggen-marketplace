#!/usr/bin/env python3
"""Layer courts (L3) - R2 machine layers against the pinned v26.10.1 layer table.

Laws: the 10 contract-required layer ids are present and unique; each layer's identifier,
repository, capabilityId and boundaryClass match the pinned source graph (ex4pm=ocel,
ashsurface=surface); every layer defaults to status UNKNOWN with empty evidence/receipt
slots; a non-UNKNOWN status requires receipt refs and ALIVE requires them (R8: standing
comes only from receipts, never adjacency). Run: python3 test/test_layer_courts.py [dir]
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
    if not machine:
        return errs
    layers = machine.get("layers")
    if not isinstance(layers, list) or not layers:
        errs.append("machine: layers must be a non-empty array")
        return errs
    by_id = {}
    for layer in layers:
        lid = layer.get("id")
        if lid in by_id:
            errs.append(f"machine.layers: duplicate layer id {lid!r}")
        by_id[lid] = layer
    for required in courts.REQUIRED_LAYER_IDS:
        if required not in by_id:
            errs.append(f"machine.layers: missing required layer id {required!r}")
    for lid, layer in sorted(by_id.items(), key=lambda kv: str(kv[0])):
        tag = f"machine.layers[{lid}]"
        pinned = courts.LAYER_TABLE.get(lid)
        if pinned is None:
            errs.append(f"{tag}: id {lid!r} outside the pinned layer table")
            continue
        _, identifier, repository, capability_id, boundary_class, _ = pinned
        for field in ("identifier", "label", "repository", "pathScope", "boundaryClass",
                      "authorityCeiling", "capabilityId", "evidenceHorizon"):
            if not courts.nonempty_str(layer.get(field)):
                errs.append(f"{tag}: field {field} must be a non-empty string")
        if layer.get("identifier") != identifier:
            errs.append(f"{tag}: identifier {layer.get('identifier')!r} != pinned {identifier!r}")
        if layer.get("repository") != repository:
            errs.append(f"{tag}: repository {layer.get('repository')!r} != pinned {repository!r}")
        if not str(layer.get("repository", "")).startswith("seanchatmangpt/"):
            errs.append(f"{tag}: repository owner must be inside seanchatmangpt/")
        if layer.get("capabilityId") != capability_id:
            errs.append(f"{tag}: capabilityId {layer.get('capabilityId')!r} != pinned {capability_id!r}")
        if layer.get("boundaryClass") not in courts.BOUNDARY_CLASSES:
            errs.append(f"{tag}: boundaryClass {layer.get('boundaryClass')!r} outside {courts.BOUNDARY_CLASSES}")
        if layer.get("boundaryClass") != boundary_class:
            errs.append(f"{tag}: boundaryClass {layer.get('boundaryClass')!r} != pinned {boundary_class!r}")
        if layer.get("authorityCeiling") != "CONSTRUCT":
            errs.append(f"{tag}: layer authorityCeiling {layer.get('authorityCeiling')!r} != pinned CONSTRUCT")
        if layer.get("required") is not True:
            errs.append(f"{tag}: required must be true for a contract-required layer")
        status = layer.get("status")
        if status not in courts.STANDING_VOCAB:
            errs.append(f"{tag}: status {status!r} outside standing vocabulary")
        if status != "UNKNOWN":
            errs.append(f"{tag}: status must default to UNKNOWN (R8: no inherited standing)")
        receipts = layer.get("receiptRefs")
        evidence = layer.get("evidenceRefs")
        if not isinstance(receipts, list):
            errs.append(f"{tag}: receiptRefs must be an array")
        if not isinstance(evidence, list):
            errs.append(f"{tag}: evidenceRefs must be an array")
        if isinstance(receipts, list) and len(receipts) == 0 and status not in ("UNKNOWN",):
            errs.append(f"{tag}: status {status!r} without receiptRefs (R8: standing only from receipts)")
        if status == "ALIVE" and (not isinstance(receipts, list) or not receipts):
            errs.append(f"{tag}: ALIVE without receiptRefs (standing-by-adjacency falsifier)")
    return errs


def selftest(rendered_dir):
    """Anti-vacuity: (a) a wrong pinned repository MUST fire; (b) a fabricated ALIVE
    layer without receiptRefs MUST fire."""
    docs, _ = courts.all_four_docs(rendered_dir)
    if "machine" not in docs:
        return ["selftest skipped: no machine.json fixture"]
    gaps = []
    mutated = json.loads(json.dumps(docs["machine"]))
    mutated["layers"][0]["repository"] = "someone-else/xaas"
    with tempfile.TemporaryDirectory() as tmp:
        pathlib.Path(tmp, "machine.json").write_text(json.dumps(mutated))
        for ptype in ("verification", "executive", "replay"):
            if ptype in docs:
                pathlib.Path(tmp, f"{ptype}.json").write_text(json.dumps(docs[ptype]))
        if not any("repository" in e for e in run(tmp)):
            gaps.append("selftest: repository-owner mutation did NOT fire (admission vacuous)")
    mutated2 = json.loads(json.dumps(docs["machine"]))
    mutated2["layers"][1]["status"] = "ALIVE"
    with tempfile.TemporaryDirectory() as tmp:
        pathlib.Path(tmp, "machine.json").write_text(json.dumps(mutated2))
        for ptype in ("verification", "executive", "replay"):
            if ptype in docs:
                pathlib.Path(tmp, f"{ptype}.json").write_text(json.dumps(docs[ptype]))
        if not any("ALIVE" in e for e in run(tmp)):
            gaps.append("selftest: fabricated-ALIVE mutation did NOT fire (standing-by-adjacency undetected)")
    return gaps


if __name__ == "__main__":
    rendered = sys.argv[1] if len(sys.argv) > 1 else str(courts.RENDERED_CANONICAL)
    errors = run(rendered) + selftest(rendered)
    for err in errors:
        print(f"VIOLATION: {err}")
    print("RESULT:", "REFUSED" if errors else "LAYER_COURTS_OK", f"({len(errors)} problems)")
    sys.exit(1 if errors else 0)
