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

MODULE_PATH = Path(__file__).with_name("audit_vacuity.py")
SPEC = importlib.util.spec_from_file_location("audit_vacuity", MODULE_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = audit
SPEC.loader.exec_module(audit)


class VacuityAuditTests(unittest.TestCase):
    def findings(self, path: str, text: str):
        return audit.scan_content("test", path, text.encode())

    def rules(self, path: str, text: str) -> set[str]:
        return {f.rule for f in self.findings(path, text)}

    def test_python_pass_function_refused(self):
        self.assertIn("PYTHON_EMPTY_FUNCTION", self.rules("gates/check.py", "def verify(x):\n    pass\n"))

    def test_python_constant_verifier_refused(self):
        self.assertIn("PYTHON_CONSTANT_SUCCESS", self.rules("gates/check.py", "def verify(x):\n    return True\n"))

    def test_python_swallowed_broad_exception_refused(self):
        self.assertIn("PYTHON_SWALLOWED_EXCEPTION", self.rules("x.py", "try:\n    work()\nexcept Exception:\n    pass\n"))

    def test_python_typed_cleanup_exception_is_not_swallowing(self):
        self.assertNotIn(
            "PYTHON_SWALLOWED_EXCEPTION",
            self.rules("x.py", "try:\n    work()\nexcept ProcessLookupError:\n    pass\n"),
        )

    def test_real_python_verifier_admitted(self):
        self.assertFalse(self.rules("gates/check.py", "def verify(x):\n    if not x:\n        raise ValueError('x')\n    return x.digest()\n"))

    def test_rust_todo_refused(self):
        self.assertIn("RUST_TODO_MACRO", self.rules("templates/lib.rs.tmpl", "fn run() { todo!() }\n"))

    def test_reference_todo_is_warning_not_error(self):
        findings = self.findings("reference/old.rs", "fn old() { todo!() }\n")
        self.assertTrue(findings)
        self.assertTrue(all(f.severity == "warning" for f in findings))

    def test_marker_in_test_fixture_is_warning(self):
        findings = self.findings("tests/test_fixture.py", "PAYLOAD = 'TODO: fixture'\n")
        self.assertTrue(findings)
        self.assertTrue(all(f.severity == "warning" for f in findings))

    def test_zero_byte_source_refused(self):
        self.assertIn("EMPTY_SOURCE_FILE", {f.rule for f in audit.scan_content("test", "gates/x.py", b"")})

    def test_data_file_is_still_examined_but_not_source(self):
        report = audit.audit_subject("test", [("data.bin", b"\x00\x01"), ("README.md", b"ok")])
        self.assertEqual(report.total_files, 2)
        self.assertEqual(report.source_files, 0)


class VacuityAuditMainTests(unittest.TestCase):
    """End-to-end coverage of main() against a real, disposable git repo.

    A real repository is genuinely cheap to construct in-process (a few
    `git` subprocess calls to a scratch dir), so this exercises the real
    git object / archive / filesystem-walk paths that main() drives rather
    than faking SubjectReport objects, per Chicago-style testing discipline.
    """

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.repo = Path(self.tmpdir.name)
        self._git("init", "-q", "-b", "main")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        # audit_vacuity's git-backed helpers shell out with no -C, using the
        # current process cwd, so main() must run inside the scratch repo.
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
        path = self.repo / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self._git("add", filename)
        self._git("commit", "-q", "-m", message)
        return self._git("rev-parse", "HEAD").stdout.strip()

    def test_main_admits_clean_filesystem_tree(self):
        self._commit("a.py", "print('hi')\n", "initial")
        exit_code = audit.main(["--root", str(self.repo)])
        self.assertEqual(exit_code, 0)

    def test_main_refuses_and_writes_report_on_filesystem_error(self):
        self._commit("a.py", "def f():\n    pass\n", "empty function")
        report_path = self.repo / "vacuity-report.json"
        exit_code = audit.main(
            ["--root", str(self.repo), "--report", str(report_path)]
        )
        self.assertEqual(exit_code, 2)
        self.assertTrue(report_path.is_file())
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["standing"], "REFUSED")
        self.assertEqual(len(payload["subjects"]), 1)
        self.assertEqual(payload["subjects"][0]["subject"], "filesystem")
        rules = {f["rule"] for f in payload["subjects"][0]["findings"]}
        self.assertIn("PYTHON_EMPTY_FUNCTION", rules)

    def test_main_audits_explicit_git_ref(self):
        head = self._commit("a.py", "print('hi')\n", "initial")
        exit_code = audit.main(["--git-ref", head])
        self.assertEqual(exit_code, 0)

    def test_main_promotes_warning_with_warnings_as_errors(self):
        # A TODO in a reference/doc-ish path is a warning, not an error
        # (test_reference_todo_is_warning_not_error above) -- confirm
        # --warnings-as-errors actually flips main()'s exit code on it.
        self._commit("docs/notes.md", "TODO: finish this\n", "todo note")
        exit_code_default = audit.main(["--root", str(self.repo)])
        self.assertEqual(exit_code_default, 0)
        exit_code_strict = audit.main(
            ["--root", str(self.repo), "--warnings-as-errors"]
        )
        self.assertEqual(exit_code_strict, 2)

    def test_main_all_remote_branches_enumerates_and_admits_with_no_remote(self):
        self._commit("a.py", "print('hi')\n", "initial")
        # No remote refs exist, so --all-remote-branches falls through to the
        # filesystem subject rather than inventing an empty audit.
        exit_code = audit.main(["--all-remote-branches"])
        self.assertEqual(exit_code, 0)

    def test_all_remote_branches_preserves_each_ref_when_content_is_shared(self):
        head = self._commit("a.py", "print('shared')\n", "initial")
        self._git("update-ref", "refs/remotes/origin/alpha", head)
        self._git("update-ref", "refs/remotes/origin/beta", head)
        report_path = self.repo / "vacuity-branches.json"

        exit_code = audit.main(
            ["--all-remote-branches", "--report", str(report_path)]
        )

        self.assertEqual(exit_code, 0)
        payload = json.loads(report_path.read_text(encoding="utf-8"))
        subjects = [subject["subject"] for subject in payload["subjects"]]
        self.assertEqual(subjects, ["origin/alpha", "origin/beta"])
        self.assertEqual(
            [subject["total_files"] for subject in payload["subjects"]],
            [1, 1],
        )


if __name__ == "__main__":
    unittest.main()
