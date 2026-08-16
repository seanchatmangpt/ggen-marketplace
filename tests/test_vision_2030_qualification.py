from __future__ import annotations

import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "packages" / "vision-2030-capability-generator"
VERIFY_PATH = PACKAGE / "scripts" / "verify.py"
SPEC = importlib.util.spec_from_file_location("vision2030_verify", VERIFY_PATH)
assert SPEC and SPEC.loader
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
FIXED_SHA = "a" * 40


class Vision2030QualificationTests(unittest.TestCase):
    def test_current_package_is_bounded_candidate(self) -> None:
        receipt = VERIFY.verify_package(PACKAGE, FIXED_SHA)
        self.assertEqual(receipt["schema"], "ggen-marketplace.vision2030-qualification/2")
        self.assertEqual(receipt["subject_sha"], FIXED_SHA)
        self.assertEqual(receipt["qualification"], "PASS")
        self.assertEqual(receipt["standing"], "CANDIDATE")
        self.assertEqual(receipt["authority_ceiling"], "CONSTRUCT_ONLY")
        self.assertFalse(receipt["do_authority"])
        self.assertFalse(receipt["self_certifying"])
        self.assertTrue(receipt["external_execution_required"])
        self.assertGreaterEqual(receipt["capabilities"], 50)
        self.assertGreaterEqual(receipt["families"], 10)
        self.assertEqual(len(receipt["top_capabilities"]), 5)

    def test_mutable_subject_is_refused(self) -> None:
        with self.assertRaises(VERIFY.QualificationRefusal):
            VERIFY.validate_subject_sha("main")

    def test_mutating_query_is_refused(self) -> None:
        with self.assertRaises(VERIFY.QualificationRefusal):
            VERIFY.validate_query_text("SELECT * WHERE {} ; DELETE WHERE {}", "bad.rq")

    def test_remote_query_is_refused(self) -> None:
        with self.assertRaises(VERIFY.QualificationRefusal):
            VERIFY.validate_query_text(
                "SELECT * WHERE { SERVICE <https://example.invalid/> { ?s ?p ?o } }",
                "remote.rq",
            )

    def test_output_escape_is_refused(self) -> None:
        with self.assertRaises(VERIFY.QualificationRefusal):
            VERIFY.validate_output_path("../outside.json")

    def test_authority_elevation_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "package"
            shutil.copytree(PACKAGE, target)
            contract = target / "qualification" / "contract.ttl"
            text = contract.read_text(encoding="utf-8")
            contract.write_text(text.replace("q:doAuthority false", "q:doAuthority true"), encoding="utf-8")
            with self.assertRaises(VERIFY.QualificationRefusal):
                VERIFY.verify_package(target, FIXED_SHA)

    def test_committed_projection_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "package"
            shutil.copytree(PACKAGE, target)
            generated = target / "generated"
            generated.mkdir()
            (generated / "artifact.json").write_text("{}\n", encoding="utf-8")
            with self.assertRaises(VERIFY.QualificationRefusal):
                VERIFY.verify_package(target, FIXED_SHA)

    def test_source_digest_is_deterministic(self) -> None:
        first = VERIFY.source_digest(PACKAGE)
        second = VERIFY.source_digest(PACKAGE)
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)


if __name__ == "__main__":
    unittest.main()
