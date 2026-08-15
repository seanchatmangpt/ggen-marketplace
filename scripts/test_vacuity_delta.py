#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("check_vacuity_delta.py")
SPEC = importlib.util.spec_from_file_location("check_vacuity_delta", MODULE_PATH)
assert SPEC and SPEC.loader
delta = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = delta
SPEC.loader.exec_module(delta)
audit = sys.modules["audit_vacuity"]


class VacuityDeltaTests(unittest.TestCase):
    def report(self, subject: str, findings: tuple[object, ...]):
        return audit.SubjectReport(subject, 1, 1, 1, findings)

    def finding(self, subject: str, *, severity: str = "error", line: int = 1):
        return audit.Finding(subject, "x.py", line, "PYTHON_EMPTY_FUNCTION", severity, "verify")

    def test_inherited_error_is_not_regression(self):
        base = self.report("base", (self.finding("base"),))
        head = self.report("head", (self.finding("head"),))
        self.assertEqual(delta.blocking_findings(base, head), ())

    def test_new_error_is_regression(self):
        base = self.report("base", ())
        finding = self.finding("head")
        head = self.report("head", (finding,))
        self.assertEqual(delta.blocking_findings(base, head), (finding,))

    def test_new_warning_is_nonblocking_by_default(self):
        base = self.report("base", ())
        head = self.report("head", (self.finding("head", severity="warning"),))
        self.assertEqual(delta.blocking_findings(base, head), ())

    def test_warning_can_be_promoted_explicitly(self):
        base = self.report("base", ())
        finding = self.finding("head", severity="warning")
        head = self.report("head", (finding,))
        self.assertEqual(delta.blocking_findings(base, head, warnings_as_errors=True), (finding,))

    def test_resolved_error_is_not_regression(self):
        base = self.report("base", (self.finding("base"),))
        head = self.report("head", ())
        self.assertEqual(delta.blocking_findings(base, head), ())


if __name__ == "__main__":
    unittest.main()
