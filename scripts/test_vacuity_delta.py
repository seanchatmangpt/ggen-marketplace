#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
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


class VacuityDeltaMainTests(unittest.TestCase):
    """End-to-end coverage of main() against a real, disposable git repo.

    A real repository is genuinely cheap to construct in-process (a few `git`
    subprocess calls to a scratch dir), so this exercises the real
    `git archive` / audit_subject path rather than faking SubjectReport
    objects, per Chicago-style testing discipline.
    """

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.repo = Path(self.tmpdir.name)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        # audit_vacuity._git_ref_files shells out to `git archive` using the
        # current process cwd (no -C), so main() must run with cwd inside
        # the scratch repo for this end-to-end test to exercise it for real.
        self._orig_cwd = Path.cwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, self._orig_cwd)

    def _git(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def _commit(self, filename: str, content: str, message: str) -> str:
        (self.repo / filename).write_text(content, encoding="utf-8")
        self._git("add", filename)
        self._git("commit", "-q", "-m", message)
        return self._git("rev-parse", "HEAD").stdout.strip()

    def test_main_admits_when_no_regression_between_identical_refs(self):
        head = self._commit("a.py", "print('hi')\n", "initial")
        exit_code = delta.main(["--baseline-ref", head, "--subject-ref", head])
        self.assertEqual(exit_code, 0)

    def test_main_refuses_and_writes_report_on_new_error(self):
        base = self._commit("a.py", "print('hi')\n", "initial")
        head = self._commit("b.py", "def f():\n    pass\n", "introduce empty function")
        report_path = self.repo / "delta-report.json"
        exit_code = delta.main(
            [
                "--baseline-ref",
                base,
                "--subject-ref",
                head,
                "--report",
                str(report_path),
            ]
        )
        self.assertEqual(exit_code, 2)
        self.assertTrue(report_path.is_file())
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["standing"], "REFUSED")
        self.assertEqual(payload["baseline_ref"], base)
        self.assertEqual(payload["subject_ref"], head)
        self.assertGreaterEqual(len(payload["blocking_regressions"]), 1)
        self.assertEqual(
            payload["blocking_regressions"][0]["rule"], "PYTHON_EMPTY_FUNCTION"
        )


if __name__ == "__main__":
    unittest.main()
