#!/usr/bin/env python3
"""Gate-level mutation court for evolvable-capability-pack (court-507 repair).

Every clause added or kept by the court-507 repair order must be non-vacuous
in both directions: a mutant that drops the clause must let a declared-refuse
case through (killed), and a mutant proven logically equivalent must show zero
corpus change (equivalent). Mutants are applied to the real gate text, the
real ``verify.py`` court, and the real ``bench.py`` judge - never to copies of
the laws inside this file.

Gate-mutant corpus: single-defect inline probes, the mutated gate's own
pass/fail witness pair, and every declared fixture (gate expectations only;
the digest-binding matrix is exercised by the verify.py mutants, which run in
a temp copy of the pack where the planted corpus must stay refused).

Usage:
    python3 mutations.py    # exit 0 iff every mutant shows its declared verdict
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify  # noqa: E402  (sibling module, real collaborator)

PACK = verify.PACK

ECAP = "https://seanchatmangpt.github.io/packs/evolvable-capability#"
PREFIXES = (
    f"@prefix ecap: <{ECAP}> .\n"
    "@prefix prov: <http://www.w3.org/ns/prov#> .\n"
    "@prefix dcterms: <http://purl.org/dc/terms/> .\n"
)
HEX = {"a": "a" * 64, "b": "b" * 64, "c": "c" * 64, "d": "d" * 64}


def _bound(row: tuple[str, str, str, str]) -> str:
    return verify.closure_digest([row])[len("sha256:"):]


def _member(name: str, version: str, digest: str, typed: bool = True, state: str = "Released") -> str:
    typ = "a ecap:Capability ;\n  " if typed else ""
    state_line = f"  ecap:lifecycleState ecap:{state} ;\n" if state else ""
    evidence = (
        f"  ecap:admissionEvidence <urn:p:{name}-admission> ;\n"
        f"  ecap:releaseEvidence <urn:p:{name}-release> .\n"
        f"<urn:p:{name}-admission> a prov:Entity .\n"
        f"<urn:p:{name}-release> a prov:Entity .\n"
    ) if state == "Released" else ".\n"
    return (
        f"<urn:p:{name}> {typ}{state_line}"
        f'  dcterms:hasVersion "{version}" ;\n'
        f'  ecap:implementationDigest "sha256:{digest}" ;\n'
        f"{evidence}"
    )


def _closure(digest_hex: str, *members: str) -> str:
    return (
        "<urn:p:closure> a ecap:ExecutionClosure ;\n"
        f'  ecap:closureDigest "sha256:{digest_hex}" ;\n'
        f"  ecap:closureMember {' , '.join(members)} .\n"
    )


def _released_member_probe(name: str, digest_hex: str, version_statements: str) -> str:
    body = (
        f"<urn:p:{name}> a ecap:Capability ;\n"
        "  ecap:lifecycleState ecap:Released ;\n"
        f"{version_statements}"
        f'  ecap:implementationDigest "sha256:{digest_hex}" ;\n'
        f"  ecap:admissionEvidence <urn:p:{name}-admission> ;\n"
        f"  ecap:releaseEvidence <urn:p:{name}-release> .\n"
        f"<urn:p:{name}-admission> a prov:Entity .\n"
        f"<urn:p:{name}-release> a prov:Entity .\n"
    )
    return body


def _admitted_capability(digest_term: str) -> str:
    """digest_term is a complete Turtle literal/IRI term, quotes included."""
    return (
        '<urn:p:cap> a ecap:Capability ;\n'
        "  ecap:lifecycleState ecap:Admitted ;\n"
        '  dcterms:hasVersion "1" ;\n'
        f"  ecap:implementationDigest {digest_term} .\n"
    )


# Single-defect probes: (id, turtle, gate stems that must refuse).
PROBES: list[tuple[str, str, frozenset[str]]] = [
    (
        "p030_candidate_member",
        PREFIXES + _member("cand", "1", HEX["a"], state="Candidate")
        + _closure(_bound(("urn:p:closure", "urn:p:cand", "1", "sha256:" + HEX["a"])), "<urn:p:cand>"),
        frozenset({"030_closure_released_only"}),
    ),
    (
        "p030_admitted_member",
        PREFIXES + _member("adm", "2", HEX["b"], state="Admitted")
        + _closure(_bound(("urn:p:closure", "urn:p:adm", "2", "sha256:" + HEX["b"])), "<urn:p:adm>"),
        frozenset({"030_closure_released_only"}),
    ),
    (
        "p030_untyped_member",
        PREFIXES + _member("untyped", "3", HEX["c"], typed=False)
        + _closure(_bound(("urn:p:closure", "urn:p:untyped", "3", "sha256:" + HEX["c"])), "<urn:p:untyped>"),
        frozenset({"030_closure_released_only", "130_declared_lifecycle_state"}),
    ),
    (
        "p030_stateless_ghost_member",
        # Bare member (untyped, stateless) with version+digest so that exactly
        # 030 and 130 refuse it (090/040 are satisfied).
        PREFIXES + '<urn:p:ghost> ecap:implementationDigest "sha256:' + HEX["a"] + '" ;\n'
        '  dcterms:hasVersion "0" .\n'
        + _closure("0" * 64, "<urn:p:ghost>"),
        frozenset({"030_closure_released_only", "130_declared_lifecycle_state"}),
    ),
    (
        "p030_retired_member",
        PREFIXES + _member("ret", "9", HEX["d"], state="Retired")
        + _closure(_bound(("urn:p:closure", "urn:p:ret", "9", "sha256:" + HEX["d"])), "<urn:p:ret>"),
        frozenset({"030_closure_released_only"}),
    ),
    (
        "p090_missing_version",
        PREFIXES + _released_member_probe("no.ver", HEX["a"], "")
        + _closure(_bound(("urn:p:closure", "urn:p:no.ver", "", "sha256:" + HEX["a"])), "<urn:p:no.ver>"),
        frozenset({"090_closure_member_version_required"}),
    ),
    (
        "p090_empty_version",
        PREFIXES + _released_member_probe("empty", HEX["b"], '  dcterms:hasVersion "" ;\n')
        + _closure(_bound(("urn:p:closure", "urn:p:empty", "", "sha256:" + HEX["b"])), "<urn:p:empty>"),
        frozenset({"090_closure_member_version_required"}),
    ),
    (
        "p090_duplicate_version",
        PREFIXES + _released_member_probe("dup", HEX["c"], '  dcterms:hasVersion "3" , "2" ;\n')
        + _closure(_bound(("urn:p:closure", "urn:p:dup", "2", "sha256:" + HEX["c"])), "<urn:p:dup>"),
        frozenset({"090_closure_member_version_required"}),
    ),
    (
        "p090_conforming",
        PREFIXES + _released_member_probe("ok", HEX["d"], '  dcterms:hasVersion "1" ;\n')
        + _closure(_bound(("urn:p:closure", "urn:p:ok", "1", "sha256:" + HEX["d"])), "<urn:p:ok>"),
        frozenset(),
    ),
    (
        "p110_iri_digest",
        PREFIXES + _admitted_capability(f"<sha256:{HEX['a']}>"),
        frozenset({"110_digest_format"}),
    ),
    (
        "p110_trailing_newline_digest",
        PREFIXES + _admitted_capability(f'"sha256:{HEX["a"]}\\n"'),
        frozenset({"110_digest_format"}),
    ),
    (
        "p110_trailing_junk_digest",
        PREFIXES + _admitted_capability(f'"sha256:{HEX["a"][:-2]}zz"'),
        frozenset({"110_digest_format"}),
    ),
    (
        "p110_typed_literal_digest",
        PREFIXES + _admitted_capability(f'"sha256:{HEX["a"]}"^^<http://www.w3.org/2001/XMLSchema#anyURI>'),
        frozenset({"110_digest_format"}),
    ),
    (
        "p110_lang_tagged_digest",
        PREFIXES + _admitted_capability(f'"sha256:{HEX["a"]}"@en'),
        frozenset({"110_digest_format"}),
    ),
    (
        "p110_uppercase_digest",
        PREFIXES + _admitted_capability(f'"sha256:{HEX["a"].upper()}"'),
        frozenset({"110_digest_format"}),
    ),
    (
        "p110_conforming_digest",
        PREFIXES + _admitted_capability(f'"sha256:{HEX["a"]}"'),
        frozenset(),
    ),
]

# (id, gate stem, old substring, new substring, expected verdict, note).
# expected: "killed" = some corpus case must change verdict under the mutant;
# "equivalent" = no corpus case may change (with the proof in the note).
GATE_MUTANTS: list[tuple[str, str, str, str, str, str]] = [
    (
        "G030A_drop_typed_membership",
        "030_closure_released_only",
        "    NOT EXISTS { ?capability a ecap:Capability }\n    || ",
        "",
        "killed",
        "court-507 A4: an untyped member must stay refused by 030 itself.",
    ),
    (
        "G030B_drop_released_only",
        "030_closure_released_only",
        "    || NOT EXISTS {\n         ?capability ecap:lifecycleState ?state .\n         FILTER(sameTerm(?state, ecap:Released))\n       }",
        "",
        "killed",
        "court-499 M05 class: an any-state closure must be refused.",
    ),
    (
        "G030C_admit_admitted",
        "030_closure_released_only",
        "FILTER(sameTerm(?state, ecap:Released))",
        "FILTER(sameTerm(?state, ecap:Released) || sameTerm(?state, ecap:Admitted))",
        "killed",
        "court-507 M5 (survived there): an Admitted member must stay refused.",
    ),
    (
        "G090A_drop_missing_version",
        "090_closure_member_version_required",
        "    NOT EXISTS {\n      ?capability dcterms:hasVersion ?version .\n      FILTER(STRLEN(STR(?version)) > 0)\n    }\n    || EXISTS",
        "    EXISTS",
        "killed",
        "A versionless member must stay refused.",
    ),
    (
        "G090B_admit_empty_version",
        "090_closure_member_version_required",
        "FILTER(STRLEN(STR(?version)) > 0)",
        "FILTER(STRLEN(STR(?version)) >= 0)",
        "killed",
        "court-507 A6: an empty version projects as missing; must be refused.",
    ),
    (
        "G090C_drop_duplicate_version",
        "090_closure_member_version_required",
        "    || EXISTS {\n         ?capability dcterms:hasVersion ?first , ?second .\n         FILTER(?first != ?second)\n       }",
        "",
        "killed",
        "court-507 A2: duplicate conflicting versions must be refused.",
    ),
    (
        "G110A_drop_isLiteral",
        "110_digest_format",
        "    !isLiteral(?digest)\n    || ",
        "",
        "killed",
        "court-499 M03: without the guard, LANG/STRLEN on an IRI error the "
        "filter and the IRI carrier slips through.",
    ),
    (
        "G110B_drop_end_anchor",
        "110_digest_format",
        '"^sha256:[0-9a-f]{64}$"',
        '"^sha256:[0-9a-f]{64}"',
        "equivalent",
        "court-499 M04: equivalent under the co-resident STRLEN==71 clause. "
        "Proof: an unanchored re.search over a 71-char string matches "
        "'^sha256:[0-9a-f]{64}' only when the match starts at position 0 and "
        "the 64-hex run fills the whole string - exactly the anchored "
        "language; 71 chars leave no room for residue. The trailing-newline "
        "carrier is refused by STRLEN (see G110C), so the corpus must show "
        "zero verdict change.",
    ),
    (
        "G110C_drop_strlen",
        "110_digest_format",
        "    || STRLEN(STR(?digest)) != 71",
        "",
        "killed",
        "court-507 M1: Python re lets $ match before a trailing newline; only "
        "STRLEN refuses 'sha256:<hex>\\n' in rdflib.",
    ),
    (
        "G110D_drop_datatype",
        "110_digest_format",
        "    || DATATYPE(?digest) != xsd:string",
        "",
        "killed",
        "The xsd:anyURI carrier must stay refused.",
    ),
    (
        "G110E_drop_lang",
        "110_digest_format",
        '    || LANG(?digest) != ""',
        "",
        "equivalent",
        "Equivalent under the co-resident DATATYPE clause: a language-tagged "
        "literal has datatype rdf:langString (RDF 1.1), so "
        "DATATYPE(?digest) != xsd:string already refuses every carrier the "
        "LANG clause refuses; the corpus must show zero verdict change. The "
        "converse does not hold - G110D is killed by the xsd:anyURI probe, "
        "and the lang-tagged probe witnesses the surviving pair.",
    ),
]

# (id, [(old, new), ...], law note). verify.py runs mutated in a temp copy of
# the pack; the planted corpus (A3 fixture / stowaway / truncated fixture)
# must keep the mutated court at exit 2 - exit 0 kills the mutant.
VERIFY_MUTANTS: list[tuple[str, list[tuple[str, str]], str, str]] = [
    (
        "V_A3_drop_digest_binding_enforcement",
        [
            (
                'binding_ok = (binding != "MISMATCH") if expected_binding else (binding == "MISMATCH")',
                "binding_ok = True",
            )
        ],
        "plant_nothing",
        "Law (court-507 A3): a format-valid closureDigest unbound to member "
        "rows must keep verify.py at exit 2 (the A3 fixture is in the "
        "corpus). Mutating the detector instead would be equivalent - the "
        "MISMATCH expectation side doubles it - so the enforcement clause is "
        "the mutation site.",
    ),
    (
        "V_M15_ignore_undeclared_fixture",
        [
            ("expected = expectations.get(key)", "expected = expectations.get(key, frozenset())"),
            ("expected_binding = digest_expectations.get(key)", "expected_binding = digest_expectations.get(key, True)"),
        ],
        "plant_stowaway",
        "Law (court-499 M15): an undeclared fixture file must keep verify.py "
        "at exit 2 (a stowaway fixture is planted in the copy).",
    ),
    (
        "V_M16_swallow_parse_error",
        [
            (
                'raise MalformedInput(f"REFUSED:MALFORMED_INPUT:{label}: {type(error).__name__}: {error}") from error',
                "continue",
            )
        ],
        "plant_truncated_fixture",
        "Law (court-499 M16): a parse-erroring declared fixture must keep "
        "verify.py at exit 2 (positive.ttl is truncated in the copy).",
    ),
]

BENCH_MUTANTS: list[tuple[str, list[tuple[str, str]], str]] = [
    (
        "B_M17_drop_defect_check",
        [("if set(poisoned) != set(expected_refusal):", "if False:")],
        "Law (court-499 M17): bench.measure with a defect the gates do not "
        "catch must raise AssertionError.",
    ),
    (
        "B_M13_disable_scaling_slack",
        [("SCALING_SLACK = 2.0", "SCALING_SLACK = 1000000.0")],
        "Law (court-499 M13): judge() must refuse a quadratic time pair even "
        "when every absolute figure is under the bound.",
    ),
]


def _observed_refusing(graph, stem: str, mutant_text: str) -> frozenset[str]:
    out: set[str] = set()
    for gate in verify.gates():
        gate_text = mutant_text if gate.stem == stem else gate.read_text(encoding="utf-8")
        if list(graph.query(gate_text)):
            out.add(gate.stem)
    return frozenset(out)


def gate_corpus() -> list[tuple[str, object, frozenset[str]]]:
    """(label, graph, declared refusing-gate set) for probes+ witness pair+ fixtures."""
    cases: list[tuple[str, object, frozenset[str]]] = []
    for probe_id, turtle, expected in PROBES:
        cases.append((f"probe/{probe_id}", verify.load_graph(turtle), expected))
    for path in sorted(verify.FIXTURES.glob("*.ttl")) + [verify.CONSUMER]:
        key = path.relative_to(verify.QUALIFICATION).as_posix()
        cases.append((f"fixture/{key}", verify.load_graph(path), verify.FIXTURE_EXPECTATIONS.get(key, frozenset())))
    return cases


def run_gate_mutants(cases: list[tuple[str, object, frozenset[str]]]) -> list[dict[str, str]]:
    report: list[dict[str, str]] = []
    for mutant_id, stem, old, new, expected, note in GATE_MUTANTS:
        gate_path = verify.GATES / f"{stem}.rq"
        pristine = gate_path.read_text(encoding="utf-8")
        if old not in pristine:
            raise AssertionError(f"{mutant_id}: mutation site not found in gates/{stem}.rq")
        mutant_text = pristine.replace(old, new)
        cases_with_witnesses = list(cases)
        for polarity, witness_dir in (("pass", verify.PASS), ("fail", verify.FAIL)):
            witness = witness_dir / f"{stem}.ttl"
            # A witness file is meaningful only for its own gate: the verdict
            # compared is the mutated stem's row count alone.
            witness_expected = frozenset() if polarity == "pass" else frozenset({stem})
            witness_graph = verify.load_graph(witness)
            witness_observed = (
                frozenset({stem})
                if list(witness_graph.query(mutant_text))
                else frozenset()
            )
            if witness_observed != witness_expected:
                cases_with_witnesses.append((f"witness/{polarity}/{stem}", witness_graph, witness_expected))
        changed = sorted(
            label
            for label, graph, declared in cases_with_witnesses
            if _observed_refusing(graph, stem, mutant_text) != declared
        )
        observed = "killed" if changed else "equivalent"
        report.append(
            {
                "id": mutant_id,
                "target": f"gates/{stem}.rq",
                "expected": expected,
                "observed": observed,
                "standing": "CONFIRMED" if observed == expected else "SURVIVED",
                "killed_by": ",".join(changed) or "-",
                "note": note,
            }
        )
    return report


def _copy_pack(tmp: str) -> Path:
    target = Path(tmp) / "pack"
    shutil.copytree(PACK, target, ignore=shutil.ignore_patterns("__pycache__"))
    return target


def run_verify_mutants() -> list[dict[str, str]]:
    report: list[dict[str, str]] = []
    for mutant_id, sites, plant, note in VERIFY_MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            copy = _copy_pack(tmp)
            qual = copy / "qualification"
            source = (qual / "verify.py").read_text(encoding="utf-8")
            for old, new in sites:
                if old not in source:
                    raise AssertionError(f"{mutant_id}: mutation site not found: {old[:60]}")
                source = source.replace(old, new)
            (qual / "verify.py").write_text(source, encoding="utf-8")
            if plant == "plant_stowaway":
                shutil.copy(qual / "fixtures" / "positive.ttl", qual / "fixtures" / "stowaway.ttl")
            elif plant == "plant_truncated_fixture":
                fixture = qual / "fixtures" / "positive.ttl"
                fixture.write_text(fixture.read_text(encoding="utf-8")[:200], encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(qual / "verify.py")],
                capture_output=True,
                text=True,
                timeout=120,
                check=False,
            )
            observed = "killed" if completed.returncode == 0 else "equivalent"
            report.append(
                {
                    "id": mutant_id,
                    "target": "qualification/verify.py",
                    "expected": "killed",
                    "observed": observed,
                    "standing": "CONFIRMED" if observed == "killed" else "SURVIVED",
                    "killed_by": (
                        "mutant exited 0 on a corpus the law refuses" if observed == "killed" else "-"
                    ),
                    "note": note,
                }
            )
    return report


def _load_bench(path: Path):
    spec = importlib.util.spec_from_file_location("ecap_mutant_bench", path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


def run_bench_mutants() -> list[dict[str, str]]:
    report: list[dict[str, str]] = []
    for mutant_id, sites, note in BENCH_MUTANTS:
        with tempfile.TemporaryDirectory() as tmp:
            bench_path = _copy_pack(tmp) / "qualification" / "bench.py"
            source = bench_path.read_text(encoding="utf-8")
            for old, new in sites:
                if old not in source:
                    raise AssertionError(f"{mutant_id}: mutation site not found: {old[:60]}")
                source = source.replace(old, new)
            bench_path.write_text(source, encoding="utf-8")
            sys.modules.pop("ecap_mutant_bench", None)
            mutated = _load_bench(bench_path)
            if mutant_id == "B_M17_drop_defect_check":
                harmless = mutated.PREFIXES + "<urn:bench:note> a <urn:bench:Note> .\n"
                try:
                    mutated.measure(10, 1, defect_text=harmless)
                    # The law requires the raise; the mutant silently admits
                    # the harmless defect, so the law violation is witnessed.
                    observed = "killed"
                except AssertionError:
                    observed = "equivalent"
            else:  # B_M13_disable_scaling_slack
                verdict = mutated.judge(
                    [
                        {"generations": 100, "median_seconds": 0.001, "seconds_per_generation": 0.00001},
                        {"generations": 400, "median_seconds": 0.016, "seconds_per_generation": 0.00004},
                    ]
                )
                # Law: quadratic scaling must be REFUSED; a mutant that admits
                # it violates the law and is killed.
                observed = "killed" if verdict["standing"] != "REFUSED" else "equivalent"
            report.append(
                {
                    "id": mutant_id,
                    "target": "qualification/bench.py",
                    "expected": "killed",
                    "observed": observed,
                    "standing": "CONFIRMED" if observed == "killed" else "SURVIVED",
                    "killed_by": "law check failed under mutant" if observed == "killed" else "-",
                    "note": note,
                }
            )
    return report


def main() -> int:
    cases = gate_corpus()
    mutants = run_gate_mutants(cases) + run_verify_mutants() + run_bench_mutants()
    survivors = [m["id"] for m in mutants if m["standing"] == "SURVIVED"]
    payload = {
        "schema": "ggen.evolvable-capability-pack.mutation-court/1",
        "pack": PACK.name,
        "corpus_cases": len(cases),
        "mutant_count": len(mutants),
        "mutants": mutants,
        "survivors": survivors,
        "standing": "REFUSED" if survivors else "ALIVE",
    }
    print(json.dumps(payload, sort_keys=True, indent=2))
    return 2 if survivors else 0


if __name__ == "__main__":
    raise SystemExit(main())
