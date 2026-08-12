#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("audit_vacuity.py")
SPEC = importlib.util.spec_from_file_location("audit_vacuity", MODULE_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)

class VacuityAuditTests(unittest.TestCase):
    def rules(self, path: str, text: str) -> set[str]:
        return {f.rule for f in audit.scan_content("test", path, text.encode())}

    def test_python_pass_function_refused(self):
        self.assertIn("PYTHON_EMPTY_FUNCTION", self.rules("gates/check.py", "def verify(x):\n    pass\n"))

    def test_python_constant_verifier_refused(self):
        self.assertIn("PYTHON_CONSTANT_SUCCESS", self.rules("gates/check.py", "def verify(x):\n    return True\n"))

    def test_python_swallowed_exception_refused(self):
        self.assertIn("PYTHON_SWALLOWED_EXCEPTION", self.rules("x.py", "try:\n    work()\nexcept Exception:\n    pass\n"))

    def test_real_python_verifier_admitted(self):
        self.assertFalse(self.rules("gates/check.py", "def verify(x):\n    if not x:\n        raise ValueError('x')\n    return x.digest()\n"))

    def test_rust_todo_refused(self):
        self.assertIn("RUST_TODO_MACRO", self.rules("templates/lib.rs.tmpl", "fn run() { todo!() }\n"))

    def test_reference_todo_is_warning_not_error(self):
        findings = audit.scan_content("test", "reference/old.rs", b"fn old() { todo!() }\n")
        self.assertTrue(findings)
        self.assertTrue(all(f.severity == "warning" for f in findings))

    def test_zero_byte_source_refused(self):
        self.assertIn("EMPTY_SOURCE_FILE", {f.rule for f in audit.scan_content("test", "gates/x.py", b"")})

    def test_data_file_is_still_examined_but_not_source(self):
        report = audit.audit_subject("test", [("data.bin", b"\x00\x01"), ("README.md", b"ok")])
        self.assertEqual(report.total_files, 2)
        self.assertEqual(report.source_files, 0)

if __name__ == "__main__":
    unittest.main()
