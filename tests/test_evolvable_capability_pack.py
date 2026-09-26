"""Adversarial court for packs/evolvable-capability-pack (Chicago style).

Every test runs the pack's real gates through a real SPARQL engine (rdflib)
or the real ggen runtime over real Turtle; nothing is stubbed. Mutations are
applied to the conforming fixture and each must be refused by exactly the
gate that owns the violated law, so a gate that goes vacuous, or a gate that
starts over-refusing, both fail here.

The ggen runtime cases need a ggen binary (GGEN_BIN or ``ggen`` on PATH); on
a machine without one they are skipped with a named reason rather than
replaced by a fake.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from rdflib import RDF, Graph, Literal, URIRef
from rdflib.namespace import XSD

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "evolvable-capability-pack"
QUALIFICATION = PACK / "qualification"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"ecap_{name}", QUALIFICATION / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(QUALIFICATION))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(QUALIFICATION))
    return module


verify = _load("verify")
bench = _load("bench")

ECAP = "https://seanchatmangpt.github.io/packs/evolvable-capability#"
POSITIVE = QUALIFICATION / "fixtures" / "positive.ttl"
PREFIX = f"@prefix ecap: <{ECAP}> .\n@prefix dcterms: <http://purl.org/dc/terms/> .\n"
HEX = "f" * 64


def ecap(term: str) -> URIRef:
    return URIRef(ECAP + term)


def urn(term: str) -> URIRef:
    return URIRef(f"urn:test:{term}")


def positive_graph() -> Graph:
    return verify.load_graph(POSITIVE)


def replace(graph: Graph, subject: URIRef, predicate: URIRef, value) -> Graph:
    graph.remove((subject, predicate, None))
    graph.add((subject, predicate, value))
    return graph


class WitnessAndFixtureCourtTests(unittest.TestCase):
    def test_every_gate_has_a_passing_and_refusing_witness(self) -> None:
        cases, refused = verify.witness_matrix()
        self.assertFalse(refused, cases)
        self.assertEqual(len(cases), len(verify.gates()))
        self.assertGreaterEqual(len(cases), 14)
        for case in cases:
            self.assertEqual(case["pass_rows"], 0, case)
            self.assertGreater(case["fail_rows"], 0, case)

    def test_every_fixture_is_refused_by_exactly_its_declared_gates(self) -> None:
        fixtures, refused = verify.fixture_matrix()
        self.assertFalse(refused, fixtures)
        self.assertEqual({f["fixture"] for f in fixtures}, set(verify.FIXTURE_EXPECTATIONS))

    def test_court_process_exits_zero_and_reports_alive(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(QUALIFICATION / "verify.py")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(payload["standing"], "ALIVE")
        self.assertEqual(payload["case_count"], len(verify.gates()))


class AdversarialMutationTests(unittest.TestCase):
    """Each mutation of the conforming fixture must hit exactly one law."""

    def assert_refused_by(self, graph: Graph, *stems: str) -> None:
        self.assertEqual(set(verify.refusing_gates(graph)), set(stems))

    def test_conforming_fixture_is_admitted(self) -> None:
        self.assert_refused_by(positive_graph())

    def test_truncated_digest_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("closure"), ecap("closureDigest"), Literal("sha256:e"))
        self.assert_refused_by(graph, "110_digest_format")

    def test_wrong_algorithm_digest_is_refused(self) -> None:
        graph = replace(
            positive_graph(), urn("pair"), ecap("cohortDigest"), Literal("md5:d41d8cd98f00b204e9800998ecf8427e")
        )
        self.assert_refused_by(graph, "110_digest_format")

    def test_uppercase_hex_digest_is_refused(self) -> None:
        graph = replace(
            positive_graph(), urn("candidate"), ecap("implementationDigest"), Literal("sha256:" + "A" * 64)
        )
        self.assert_refused_by(graph, "110_digest_format")

    def test_iri_digest_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("pair"), ecap("evidenceDigest"), urn("not-a-literal"))
        self.assert_refused_by(graph, "110_digest_format")

    def test_json_breakout_digest_is_refused(self) -> None:
        graph = replace(
            positive_graph(),
            urn("candidate"),
            ecap("implementationDigest"),
            Literal('sha256:a", "authority": "DO'),
        )
        self.assert_refused_by(graph, "110_digest_format")

    def test_second_implementation_digest_is_refused(self) -> None:
        graph = positive_graph()
        graph.add((urn("candidate"), ecap("implementationDigest"), Literal("sha256:" + HEX)))
        self.assert_refused_by(graph, "100_single_digest_identity")

    def test_second_closure_digest_is_refused(self) -> None:
        graph = positive_graph()
        graph.add((urn("closure"), ecap("closureDigest"), Literal("sha256:" + HEX)))
        self.assert_refused_by(graph, "100_single_digest_identity")

    def test_second_cohort_digest_is_refused(self) -> None:
        graph = positive_graph()
        graph.add((urn("pair"), ecap("cohortDigest"), Literal("sha256:" + HEX)))
        self.assert_refused_by(graph, "140_single_evidence_identity")

    def test_closure_member_without_version_is_refused(self) -> None:
        graph = positive_graph()
        graph.remove((urn("candidate"), URIRef("http://purl.org/dc/terms/hasVersion"), None))
        self.assert_refused_by(graph, "090_closure_member_version_required")

    def test_stale_retired_member_in_closure_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("candidate"), ecap("lifecycleState"), ecap("Retired"))
        self.assert_refused_by(graph, "030_closure_released_only")

    def test_released_and_retired_at_once_is_refused(self) -> None:
        graph = positive_graph()
        graph.add((urn("candidate"), ecap("lifecycleState"), ecap("Retired")))
        self.assert_refused_by(graph, "080_single_lifecycle_state")

    def test_undeclared_state_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("champion"), ecap("lifecycleState"), ecap("Deployed"))
        # An undeclared state is not Released, so the champion also stops
        # being a lawful incumbent for the paired evidence.
        self.assert_refused_by(graph, "130_declared_lifecycle_state", "120_promotion_evidence_bound")

    def test_evidence_for_a_different_candidate_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("pair"), ecap("candidate"), urn("champion"))
        # candidate slot now names the champion: self-pair and mismatch both hold.
        self.assert_refused_by(graph, "050_distinct_champion_candidate", "070_promotion_target_matches_pair")

    def test_promotion_of_unpaired_capability_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("promotion"), ecap("promotes"), urn("champion"))
        self.assert_refused_by(graph, "070_promotion_target_matches_pair")

    def test_unreleased_champion_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("champion"), ecap("lifecycleState"), ecap("Admitted"))
        self.assert_refused_by(graph, "120_promotion_evidence_bound")

    def test_evidence_without_cohort_is_refused(self) -> None:
        graph = positive_graph()
        graph.remove((urn("pair"), ecap("cohortDigest"), None))
        self.assert_refused_by(graph, "060_paired_evidence_complete")

    def test_untyped_evidence_is_refused(self) -> None:
        graph = positive_graph()
        graph.remove((urn("pair"), None, None))
        self.assert_refused_by(graph, "120_promotion_evidence_bound")

    def test_released_without_release_evidence_is_refused(self) -> None:
        graph = positive_graph()
        graph.remove((urn("champion"), ecap("releaseEvidence"), None))
        self.assert_refused_by(graph, "020_released_requires_evidence")

    def test_member_without_digest_is_refused(self) -> None:
        graph = positive_graph()
        graph.remove((urn("candidate"), ecap("implementationDigest"), None))
        self.assert_refused_by(graph, "040_frozen_identity_required")

    # --- digest carriers: well-formed hex in a non-plain literal (110) -------

    def test_iri_carrying_wellformed_hex_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("candidate"), ecap("implementationDigest"), URIRef("sha256:" + HEX))
        self.assert_refused_by(graph, "110_digest_format")

    def test_trailing_junk_after_hex_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("closure"), ecap("closureDigest"), Literal("sha256:" + HEX + "zz"))
        self.assert_refused_by(graph, "110_digest_format")

    def test_trailing_newline_after_hex_is_refused(self) -> None:
        # Python re lets `$` match before a final newline; ggen refuses this.
        graph = replace(positive_graph(), urn("closure"), ecap("closureDigest"), Literal("sha256:" + HEX + "\n"))
        self.assert_refused_by(graph, "110_digest_format")

    def test_typed_digest_literal_is_refused(self) -> None:
        graph = replace(
            positive_graph(), urn("pair"), ecap("cohortDigest"), Literal("sha256:" + HEX, datatype=XSD.anyURI)
        )
        self.assert_refused_by(graph, "110_digest_format")

    def test_language_tagged_digest_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("pair"), ecap("evidenceDigest"), Literal("sha256:" + HEX, lang="en"))
        self.assert_refused_by(graph, "110_digest_format")

    def test_explicit_xsd_string_digest_is_admitted(self) -> None:
        # "sha256:<hex>"^^xsd:string is the same RDF 1.1 term as the plain form.
        graph = replace(
            positive_graph(), urn("candidate"), ecap("implementationDigest"),
            Literal("sha256:" + "b" * 64, datatype=XSD.string),
        )
        self.assert_refused_by(graph)

    # --- untyped capabilities: rdfs:domain/range are not entailed -----------

    def test_untyped_member_released_and_candidate_is_refused(self) -> None:
        # Adversarial A5: the type triple is dropped and a Candidate state is
        # smuggled beside Released, with no evidence at all.
        graph = positive_graph()
        graph.remove((urn("candidate"), RDF.type, None))
        graph.remove((urn("candidate"), ecap("admissionEvidence"), None))
        graph.remove((urn("candidate"), ecap("releaseEvidence"), None))
        graph.add((urn("candidate"), ecap("lifecycleState"), ecap("Candidate")))
        self.assert_refused_by(
            graph,
            "020_released_requires_evidence",
            "080_single_lifecycle_state",
            "130_declared_lifecycle_state",
        )

    def test_untyped_released_member_without_evidence_is_refused(self) -> None:
        # Adversarial A4.
        graph = positive_graph()
        graph.remove((urn("candidate"), RDF.type, None))
        graph.remove((urn("candidate"), ecap("admissionEvidence"), None))
        graph.remove((urn("candidate"), ecap("releaseEvidence"), None))
        self.assert_refused_by(graph, "020_released_requires_evidence", "130_declared_lifecycle_state")

    def test_untyped_but_otherwise_lawful_member_is_refused_as_untyped(self) -> None:
        graph = positive_graph()
        graph.remove((urn("candidate"), RDF.type, None))
        refused = verify.refusing_gates(graph)
        self.assertEqual(set(refused), {"130_declared_lifecycle_state"})
        rows = verify.rows(verify.GATES / "130_declared_lifecycle_state.rq", graph)
        self.assertEqual({(str(r[0]), str(r[1])) for r in rows}, {("urn:test:candidate", "untypedCapability")})

    def test_untyped_stateless_closure_member_is_refused(self) -> None:
        graph = positive_graph()
        graph.add((urn("closure"), ecap("closureMember"), urn("ghost")))
        refused = verify.refusing_gates(graph)
        self.assertIn("130_declared_lifecycle_state", refused)
        self.assertIn("030_closure_released_only", refused)
        rows = verify.rows(verify.GATES / "130_declared_lifecycle_state.rq", graph)
        self.assertEqual(
            {(str(r[0]), str(r[1])) for r in rows},
            {("urn:test:ghost", "missingState"), ("urn:test:ghost", "untypedCapability")},
        )

    def test_second_digest_on_non_member_capability_is_refused(self) -> None:
        graph = positive_graph()
        graph.add((urn("champion"), ecap("implementationDigest"), Literal("sha256:" + HEX)))
        self.assert_refused_by(graph, "100_single_digest_identity")

    # --- evidence must be a prov:Entity (020) --------------------------------

    def test_literal_admission_evidence_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("champion"), ecap("admissionEvidence"), Literal("trust me"))
        self.assert_refused_by(graph, "020_released_requires_evidence")

    def test_untyped_release_evidence_is_refused(self) -> None:
        graph = replace(positive_graph(), urn("candidate"), ecap("releaseEvidence"), urn("nowhere"))
        self.assert_refused_by(graph, "020_released_requires_evidence")

    def test_evidence_typed_by_prov_subclass_is_admitted(self) -> None:
        # ecap:Capability rdfs:subClassOf prov:Entity: subclass typing counts.
        graph = positive_graph()
        graph.remove((urn("champion-release"), RDF.type, None))
        graph.add((urn("champion-release"), RDF.type, ecap("Capability")))
        graph.add((urn("champion-release"), ecap("lifecycleState"), ecap("Candidate")))
        self.assert_refused_by(graph)

    def test_duplicate_delivery_is_idempotent(self) -> None:
        graph = verify.load_graph(POSITIVE, POSITIVE, POSITIVE)
        self.assertEqual(len(graph), len(positive_graph()))
        self.assert_refused_by(graph)

    def test_statement_reordering_does_not_change_verdicts(self) -> None:
        neg = QUALIFICATION / "fixtures" / "neg-candidate-in-closure.ttl"
        for source in (POSITIVE, neg):
            lines = Graph().parse(source, format="turtle").serialize(format="nt").splitlines()
            forward = verify.load_graph("\n".join(sorted(lines)) + "\n", data_format="nt")
            backward = verify.load_graph("\n".join(sorted(lines, reverse=True)) + "\n", data_format="nt")
            for gate in verify.gates():
                self.assertEqual(
                    sorted(verify.rows(gate, forward)), sorted(verify.rows(gate, backward)), (source, gate)
                )

    def test_malformed_turtle_is_refused_not_admitted(self) -> None:
        for broken in (
            PREFIX + '<urn:x> a ecap:Capability ; ecap:implementationDigest "sha256:',
            PREFIX + "<urn:x> a ecap:Capability ; ecap:lifecycleState",
            PREFIX + "<urn:x> undeclared:predicate <urn:y> .",
            "\x00\xff not turtle at all",
        ):
            with self.subTest(broken=broken[-40:]):
                with self.assertRaisesRegex(verify.MalformedInput, "REFUSED:MALFORMED_INPUT"):
                    verify.load_graph(broken)


class FixtureMatrixRefusalTests(unittest.TestCase):
    """The fixture matrix over a real on-disk copy of qualification/."""

    def copy(self) -> Path:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "qualification"
        shutil.copytree(QUALIFICATION, target, ignore=shutil.ignore_patterns("__pycache__"))
        return target

    def test_pristine_copy_is_alive(self) -> None:
        fixtures, refused = verify.fixture_matrix(self.copy())
        self.assertFalse(refused, fixtures)

    def test_undeclared_fixture_is_refused(self) -> None:
        target = self.copy()
        shutil.copy(target / "fixtures" / "positive.ttl", target / "fixtures" / "stowaway.ttl")
        fixtures, refused = verify.fixture_matrix(target)
        self.assertTrue(refused)
        self.assertNotIn("fixtures/stowaway.ttl", {f["fixture"] for f in fixtures})

    def test_missing_declared_fixture_is_refused(self) -> None:
        target = self.copy()
        (target / "fixtures" / "neg-candidate-in-closure.ttl").unlink()
        _, refused = verify.fixture_matrix(target)
        self.assertTrue(refused)

    def test_fixture_refused_by_wrong_gate_set_is_refused(self) -> None:
        target = self.copy()
        shutil.copy(
            target / "fixtures" / "neg-released-without-evidence.ttl", target / "fixtures" / "positive.ttl"
        )
        fixtures, refused = verify.fixture_matrix(target)
        self.assertTrue(refused)
        positive = next(f for f in fixtures if f["fixture"] == "fixtures/positive.ttl")
        self.assertEqual(positive["standing"], "REFUSED")
        self.assertEqual(positive["observed_refusals"], ["020_released_requires_evidence"])


def ggen_binary() -> str | None:
    return os.environ.get("GGEN_BIN") or shutil.which("ggen")


@unittest.skipIf(ggen_binary() is None, "ggen runtime not installed (set GGEN_BIN); rdflib court still ran")
class GgenRuntimeTests(unittest.TestCase):
    """The pack as a real ggen consumer sees it: gates run on the union graph."""

    def sync(self, ontology: str) -> tuple[subprocess.CompletedProcess[str], Path]:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        capsule = Path(temp.name)
        (capsule / "templates").mkdir()
        (capsule / "ontology.ttl").write_text(ontology, encoding="utf-8")
        (capsule / "ggen.toml").write_text(
            "\n".join(
                (
                    "[project]",
                    'name = "ecap-court"',
                    "[ontology]",
                    'source = "ontology.ttl"',
                    "[packs]",
                    f'"evolvable-capability-pack" = {{ path = {json.dumps(PACK.as_posix())} }}',
                    "[templates]",
                    'dir = "templates"',
                    "",
                )
            ),
            encoding="utf-8",
        )
        completed = subprocess.run(
            [ggen_binary(), "sync", "run"],
            cwd=capsule,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        return completed, capsule / "generated" / "evolvable-capability-closure.json"

    def test_conforming_consumer_projects_valid_authority_free_json(self) -> None:
        completed, output = self.sync((QUALIFICATION / "consumer.ttl").read_text(encoding="utf-8"))
        self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["authority"], "none")
        self.assertEqual(
            payload["members"],
            [
                {
                    "closure": "urn:test:closure",
                    "capability": "urn:test:candidate",
                    "version": "2",
                    "implementation_digest": "sha256:" + "b" * 64,
                }
            ],
        )

    def test_json_breakout_digest_is_refused_before_projection(self) -> None:
        ontology = POSITIVE.read_text(encoding="utf-8").replace(
            '"sha256:' + "b" * 64 + '"', '"sha256:b\\", \\"authority\\": \\"DO"'
        )
        completed, output = self.sync(ontology)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("110_digest_format", completed.stdout + completed.stderr)
        self.assertFalse(output.exists())

    def test_untyped_candidate_member_is_refused_before_projection(self) -> None:
        # Adversarial A5 against the runtime: before the 020/080/130 rescope,
        # ggen admitted this and projected urn:test:candidate into the closure.
        text = (QUALIFICATION / "consumer.ttl").read_text(encoding="utf-8")
        block_start = text.index("<urn:test:candidate> a ecap:Capability ;")
        block_end = text.index(".\n", block_start) + 2
        untyped = (
            "<urn:test:candidate> ecap:lifecycleState ecap:Released ;\n"
            "  ecap:lifecycleState ecap:Candidate ;\n"
            '  dcterms:hasVersion "2" ;\n'
            '  ecap:implementationDigest "sha256:' + "b" * 64 + '" .\n'
        )
        completed, output = self.sync(text[:block_start] + untyped + text[block_end:])
        self.assertNotEqual(completed.returncode, 0)
        # ggen stops at the first refusing gate (lexical order); the rdflib
        # court names the full set in the mutation tests above.
        self.assertIn("020_released_requires_evidence", completed.stdout + completed.stderr)
        self.assertFalse(output.exists())

    def test_trailing_newline_digest_is_refused_by_runtime_and_court_alike(self) -> None:
        ontology = (QUALIFICATION / "consumer.ttl").read_text(encoding="utf-8").replace(
            '"sha256:' + "e" * 64 + '"', '"sha256:' + "e" * 64 + '\\n"'
        )
        completed, output = self.sync(ontology)
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("110_digest_format", completed.stdout + completed.stderr)
        self.assertFalse(output.exists())
        with tempfile.NamedTemporaryFile("w", suffix=".ttl", delete=False) as handle:
            handle.write(ontology)
        self.addCleanup(os.unlink, handle.name)
        self.assertIn("110_digest_format", verify.refusing_gates(verify.load_graph(Path(handle.name))))

    def test_ungated_literal_with_quotes_is_escaped_in_projection(self) -> None:
        hostile = 'v2", "authority": "DO'
        ontology = POSITIVE.read_text(encoding="utf-8").replace(
            'dcterms:hasVersion "2"', "dcterms:hasVersion " + json.dumps(hostile)
        )
        completed, output = self.sync(ontology)
        self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["authority"], "none")
        self.assertEqual(payload["members"][0]["version"], hostile)
        self.assertNotIn("authority", payload["members"][0])

    def test_projection_replays_byte_identically(self) -> None:
        text = (QUALIFICATION / "consumer.ttl").read_text(encoding="utf-8")
        first, first_output = self.sync(text)
        second, second_output = self.sync(text)
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        self.assertEqual(first_output.read_bytes(), second_output.read_bytes())

    def test_scaled_history_syncs_within_qualification_bound(self) -> None:
        generations = 800
        start = time.perf_counter()
        completed, output = self.sync(bench.history(generations))
        elapsed = time.perf_counter() - start
        self.assertEqual(completed.returncode, 0, completed.stderr[-2000:])
        self.assertEqual(len(json.loads(output.read_text(encoding="utf-8"))["members"]), 2 * generations)
        # Measured 0.64 s on 2026-09-25 (ggen 26.9.18, Apple silicon); CI's
        # per-pack qualification ceiling is 15 s.
        self.assertLess(elapsed, 10.0)


class BenchmarkRegressionTests(unittest.TestCase):
    def test_gate_set_stays_within_recorded_bounds(self) -> None:
        report = bench.run([100, 400], repeats=1)
        self.assertEqual(report["standing"], "ALIVE", report)
        self.assertTrue(report["scaling"]["checked"])

    def test_history_generator_is_deterministic_and_conforming(self) -> None:
        self.assertEqual(bench.history(25), bench.history(25))
        self.assertEqual(verify.refusing_gates(verify.load_graph(bench.history(25))), {})
        poisoned = verify.load_graph(bench.history(25), bench.defect())
        self.assertEqual(set(verify.refusing_gates(poisoned)), {"030_closure_released_only"})

    @staticmethod
    def result(generations: int, seconds: float) -> dict[str, object]:
        return {
            "generations": generations,
            "median_seconds": seconds,
            "seconds_per_generation": seconds / generations,
        }

    def test_linear_scaling_is_admitted(self) -> None:
        verdict = bench.judge([self.result(100, 0.2), self.result(400, 0.8)])
        self.assertEqual(verdict["standing"], "ALIVE", verdict)

    def test_quadratic_scaling_is_refused_even_when_fast(self) -> None:
        # 4x the size, 16x the time: quadratic, although every absolute
        # per-generation figure is far below the bound.
        verdict = bench.judge([self.result(100, 0.001), self.result(400, 0.016)])
        self.assertTrue(verdict["per_generation_ok"])
        self.assertEqual(verdict["standing"], "REFUSED", verdict)

    def test_superlinear_step_between_smaller_sizes_is_refused(self) -> None:
        # The blow-up sits between the two smallest sizes; the largest pair is
        # linear. Comparing only the largest pair would miss it.
        verdict = bench.judge(
            [self.result(50, 0.01), self.result(200, 0.5), self.result(800, 2.0)]
        )
        self.assertEqual([p["standing"] for p in verdict["scaling"]["pairs"]], ["REFUSED", "ALIVE"])
        self.assertEqual(verdict["standing"], "REFUSED")

    def test_absolute_bound_is_enforced_on_largest_size(self) -> None:
        slow = bench.MAX_SECONDS_PER_GENERATION * 2
        verdict = bench.judge([self.result(10, 10 * slow)])
        self.assertFalse(verdict["per_generation_ok"])
        self.assertEqual(verdict["standing"], "REFUSED")

    def test_benchmark_refuses_a_defect_the_gates_do_not_catch(self) -> None:
        # A "defect" that violates nothing: the anti-vacuity check must raise.
        harmless = bench.PREFIXES + "<urn:bench:note> a <urn:bench:Note> .\n"
        with self.assertRaisesRegex(AssertionError, "injected defect not isolated"):
            bench.measure(10, 1, defect_text=harmless)

    def test_benchmark_refuses_a_defect_caught_by_the_wrong_gate(self) -> None:
        with self.assertRaisesRegex(AssertionError, "injected defect not isolated"):
            bench.measure(10, 1, expected_refusal=frozenset({"020_released_requires_evidence"}))

    def test_committed_receipt_satisfies_its_own_bounds(self) -> None:
        receipt = json.loads((QUALIFICATION / "bench-receipt.json").read_text(encoding="utf-8"))
        self.assertEqual(receipt["standing"], "ALIVE")
        self.assertEqual(receipt["bound_seconds_per_generation"], bench.MAX_SECONDS_PER_GENERATION)
        largest = max(receipt["results"], key=lambda r: r["generations"])
        self.assertLessEqual(largest["seconds_per_generation"], bench.MAX_SECONDS_PER_GENERATION)
        self.assertEqual(largest["input_sha256"], __import__("hashlib").sha256(
            bench.history(largest["generations"]).encode("utf-8")
        ).hexdigest())


if __name__ == "__main__":
    unittest.main()
