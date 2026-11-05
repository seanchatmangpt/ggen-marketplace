#!/usr/bin/env python3
"""aoq-pack semantic-gate witness court (ggen.semantic-gate-witness-court/1).

Executable arm of gate-court.toml (runner = "python3 qualification/verify.py").

For every gate stem in gates/ (sorted; the directory listing is the truth,
never a hand list):

  pass witness (witnesses/pass/<stem>.ttl): gate must return ZERO violations
  fail witness (witnesses/fail/<stem>.ttl): gate must return >= 1 violation

Violation classes:

  SELECT gate: any row = violation.
  ASK gate:    askAnswer true = violation.

A gate that cannot flip (0 violations on BOTH witnesses) is a VACUOUS-GATE
failure (exit 1), never a pass. An ASK gate that also fires on the clean
seed graph (qualification/seed.ttl) is unconditional and is classified
VACUOUS-GATE as well. A fail witness that is not the seed graph plus a
targeted mutation (missing the seed's core individuals) is a JUNK-FAIL-
WITNESS court failure (exit 2). A missing witness is typed (COURT-BROKEN,
exit 2), never silent.

Verdict JSON on stdout. Exit codes:
  0 = CONFORMANT   1 = VIOLATION (incl. VACUOUS-GATE)
  2 = COURT-BROKEN (missing witness / unreadable gate or witness /
                     junk fail witness)

Run from the pack root: python3 qualification/verify.py
"""
import json
import re
import sys
from pathlib import Path

from rdflib import Graph
from rdflib.namespace import RDF

PACK_ROOT = Path(__file__).resolve().parent.parent
GATES_DIR = PACK_ROOT / "gates"
PASS_DIR = PACK_ROOT / "witnesses" / "pass"
FAIL_DIR = PACK_ROOT / "witnesses" / "fail"
SEED_PATH = PACK_ROOT / "qualification" / "seed.ttl"
SCHEMA = "ggen.semantic-gate-witness-court/1"

EXIT_CONFORMANT = 0
EXIT_VIOLATION = 1
EXIT_COURT_BROKEN = 2


def parse_ttl(ttl_path: Path) -> Graph:
    return Graph().parse(ttl_path, format="turtle")


def violation_count(gate_text: str, graph: Graph) -> int:
    """Violations of one gate against one witness graph."""
    head = gate_text.split("{", 1)[0].upper()
    if "ASK" in head:
        return 1 if graph.query(gate_text).askAnswer else 0
    return len(list(graph.query(gate_text)))


def fail_witness_junk(seed: Graph, fail_graph: Graph, gate_text: str) -> bool:
    """A fail witness must be the seed graph plus a targeted mutation.

    A fail witness may drop a seed core individual only when the gate
    itself documents that removal (the individual's local name or its
    class local-name appearing in the gate's own text). A fail witness
    missing undocumented seed core individuals is junk (e.g. an emptied
    witness).
    """
    norm = re.sub(r"[^a-z0-9]", "", gate_text.lower())
    seed_subjects = {s for s in seed.subjects() if (s, RDF.type, None) in seed}
    fail_subjects = set(fail_graph.subjects())
    dropped = seed_subjects - fail_subjects
    for subject in dropped:
        classes = {str(o).rsplit(":", 1)[-1] for o in seed.objects(subject, RDF.type)}
        if any(re.sub(r"[^a-z0-9]", "", c.lower()) in norm for c in classes):
            continue
        local = re.sub(r"[^a-z0-9]", "", str(subject).rsplit("/", 1)[-1].lower())
        if local and local in norm:
            continue
        return True
    return False


def main() -> int:
    gates = sorted(GATES_DIR.glob("*.rq"))
    if not gates:
        print(json.dumps({"verdict": "COURT-BROKEN",
                          "reason": "no gates found under gates/"}))
        return EXIT_COURT_BROKEN
    try:
        seed = parse_ttl(SEED_PATH)
    except Exception as e:  # noqa: BLE001 -- typed court failure
        print(json.dumps({"verdict": "COURT-BROKEN",
                          "reason": f"unreadable seed graph: {e}"}))
        return EXIT_COURT_BROKEN

    flips = []
    vacuous = []
    violated = []
    broken = []

    for gate in gates:
        stem = gate.stem
        pw = PASS_DIR / f"{stem}.ttl"
        fw = FAIL_DIR / f"{stem}.ttl"
        if not pw.exists() or not fw.exists():
            broken.append({"gate": stem, "reason": "missing witness",
                           "missing": [p.name for p in (pw, fw) if not p.exists()]})
            continue
        try:
            gate_text = gate.read_text()
            pg = parse_ttl(pw)
            fg = parse_ttl(fw)
            pv = violation_count(gate_text, pg)
            fv = violation_count(gate_text, fg)
            seed_rows = violation_count(gate_text, seed)
        except Exception as e:  # noqa: BLE001 -- typed court failure, not a silent pass
            broken.append({"gate": stem, "reason": f"query error: {e}"})
            continue
        if fail_witness_junk(seed, fg, gate_text):
            broken.append({"gate": stem, "verdict": "JUNK-FAIL-WITNESS",
                           "reason": "fail witness is missing seed core individuals"})
            continue
        if seed_rows >= 1:
            # Gate fires on the clean seed graph: unconditional, cannot flip.
            vacuous.append({"gate": stem, "verdict": "VACUOUS-GATE",
                            "reason": "gate fires on clean seed graph",
                            "seed_rows": seed_rows,
                            "pass_rows": pv, "fail_rows": fv})
        elif pv == 0 and fv >= 1:
            flips.append({"gate": stem, "verdict": "FLIP-OK",
                          "pass_rows": pv, "fail_rows": fv})
        elif pv == 0 and fv == 0:
            vacuous.append({"gate": stem, "verdict": "VACUOUS-GATE",
                            "reason": "gate cannot flip on either witness",
                            "pass_rows": pv, "fail_rows": fv})
        else:
            violated.append({"verdict": "PASS-WITNESS-VIOLATION", "gate": stem,
                             "pass_rows": pv, "fail_rows": fv})

    if broken:
        print(json.dumps({"verdict": "COURT-BROKEN", "schema": SCHEMA,
                          "broken": broken}, indent=2))
        return EXIT_COURT_BROKEN
    if violated:
        print(json.dumps({"verdict": "VIOLATION", "schema": SCHEMA,
                          "violations": violated}, indent=2))
        return EXIT_VIOLATION
    if vacuous:
        print(json.dumps({"verdict": "VACUOUS-GATE", "schema": SCHEMA,
                          "vacuous": vacuous}, indent=2))
        return EXIT_VIOLATION
    if len(flips) != len(gates):
        print(json.dumps({"verdict": "COURT-BROKEN", "schema": SCHEMA,
                          "reason": "flip accounting mismatch",
                          "gates": len(gates), "flips": len(flips)}, indent=2))
        return EXIT_COURT_BROKEN
    print(json.dumps({"verdict": "CONFORMANT", "schema": SCHEMA,
                      "gates": len(gates),
                      "flips": len(flips),
                      "per_gate": flips}, indent=2))
    return EXIT_CONFORMANT


if __name__ == "__main__":
    sys.exit(main())
