from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.check_gate_witness_courts import CourtError, qualify


CONFIG = """[court]
schema = "ggen.semantic-gate-witness-court/1"
case_key = "exact-stem"
gate_dir = "gates"
pass_dir = "witnesses/pass"
fail_dir = "witnesses/fail"
require_pass = true
require_fail = true
"""


class GateWitnessCourtTests(unittest.TestCase):
    def make_pack(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        pack = Path(temp.name) / "pack"
        (pack / "gates").mkdir(parents=True)
        (pack / "witnesses" / "pass").mkdir(parents=True)
        (pack / "witnesses" / "fail").mkdir(parents=True)
        (pack / "gate-court.toml").write_text(CONFIG, encoding="utf-8")
        (pack / "gates" / "01-case.rq").write_text("SELECT * WHERE {}\n", encoding="utf-8")
        (pack / "witnesses" / "pass" / "01-case.ttl").write_text("@prefix ex: <urn:ex:> .\n", encoding="utf-8")
        (pack / "witnesses" / "fail" / "01-case.ttl").write_text("@prefix ex: <urn:ex:> .\n", encoding="utf-8")
        return temp, pack

    def test_complete_matrix_is_alive(self) -> None:
        temp, pack = self.make_pack()
        self.addCleanup(temp.cleanup)
        record = qualify(pack)
        self.assertEqual(record["standing"], "ALIVE")
        self.assertEqual(record["case_count"], 1)

    def test_missing_negative_witness_refuses(self) -> None:
        temp, pack = self.make_pack()
        self.addCleanup(temp.cleanup)
        (pack / "witnesses" / "fail" / "01-case.ttl").unlink()
        with self.assertRaisesRegex(CourtError, "missing_fail"):
            qualify(pack)

    def test_orphan_positive_witness_refuses(self) -> None:
        temp, pack = self.make_pack()
        self.addCleanup(temp.cleanup)
        (pack / "witnesses" / "pass" / "99-orphan.ttl").write_text("@prefix ex: <urn:ex:> .\n", encoding="utf-8")
        with self.assertRaisesRegex(CourtError, "orphan_pass"):
            qualify(pack)

    def test_duplicate_gate_case_refuses(self) -> None:
        temp, pack = self.make_pack()
        self.addCleanup(temp.cleanup)
        (pack / "gates" / "01-case.sparql").write_text("SELECT * WHERE {}\n", encoding="utf-8")
        with self.assertRaisesRegex(CourtError, "duplicate case stems"):
            qualify(pack)

    def test_path_escape_refuses(self) -> None:
        temp, pack = self.make_pack()
        self.addCleanup(temp.cleanup)
        config = CONFIG.replace('gate_dir = "gates"', 'gate_dir = "../outside"')
        (pack / "gate-court.toml").write_text(config, encoding="utf-8")
        with self.assertRaisesRegex(CourtError, "unsafe path"):
            qualify(pack)


if __name__ == "__main__":
    unittest.main()
