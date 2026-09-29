"""Scaffolder tests: real files, real subprocesses, real ggen qualification. No mocks."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEW = ROOT / "scripts" / "new_pack.py"
MP = ROOT / "scripts" / "marketplace.py"
HAVE_GGEN = shutil.which("ggen") is not None


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, timeout=600)


class NewPackTests(unittest.TestCase):
    created: list[Path]

    def setUp(self) -> None:
        self.created = []

    def tearDown(self) -> None:
        for path in self.created:
            shutil.rmtree(path, ignore_errors=True)

    def scaffold(self, name: str, profile: str) -> subprocess.CompletedProcess[str]:
        self.created.append(ROOT / "packs" / name)
        return run(str(NEW), name, "--profile", profile)

    def check_profile(self, profile: str) -> None:
        name = f"zz-scaffold-test-{profile}"
        try:
            made = self.scaffold(name, profile)
            self.assertEqual(made.returncode, 0, made.stderr)
            args = [str(MP), "check", name] + ([] if HAVE_GGEN else ["--no-qualify"])
            result = run(*args)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("check ok", result.stdout)
            self.assertEqual(run(str(MP), "validate").returncode, 0)
            court = run(str(ROOT / "scripts" / "check_gate_witness_courts.py"))
            self.assertEqual(court.returncode, 0, court.stderr + court.stdout)
        finally:
            shutil.rmtree(ROOT / "packs" / name, ignore_errors=True)

    def test_semantic(self) -> None:
        self.check_profile("semantic")

    def test_projection(self) -> None:
        self.check_profile("projection")

    def test_project(self) -> None:
        self.check_profile("project")

    def test_profile_shapes(self) -> None:
        for profile in ("semantic", "projection", "project"):
            name = f"zz-scaffold-shape-{profile}"
            self.scaffold(name, profile)
        try:
            for profile in ("semantic", "projection", "project"):
                pack = ROOT / "packs" / f"zz-scaffold-shape-{profile}"
                self.assertEqual((pack / "ggen.toml").is_file(), profile == "project")
                self.assertEqual(any((pack / "templates").glob("*.tmpl")) if (pack / "templates").is_dir() else False, profile == "projection")
                self.assertEqual(
                    sorted(tomllib.loads((pack / "pack.toml").read_text())["pack"]),
                    ["description", "name", "version"],
                )
                self.assertTrue((pack / "README.md").is_file())
        finally:
            for profile in ("semantic", "projection", "project"):
                shutil.rmtree(ROOT / "packs" / f"zz-scaffold-shape-{profile}", ignore_errors=True)

    def test_refuses_existing(self) -> None:
        name = "zz-scaffold-dup"
        first = self.scaffold(name, "semantic")
        self.assertEqual(first.returncode, 0, first.stderr)
        second = run(str(NEW), name, "--profile", "semantic")
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("PACK_EXISTS", second.stderr + second.stdout)

    def test_refuses_invalid_names(self) -> None:
        for bad in ("Bad_Name", "-lead", "trail-", "a--b", "1abc", "../evil", "x/y"):
            result = run(str(NEW), bad, "--profile", "semantic")
            self.assertNotEqual(result.returncode, 0, bad)
            self.assertFalse((ROOT / "packs" / bad).exists() if "/" not in bad else False)

    def test_refuses_unknown_profile(self) -> None:
        result = run(str(NEW), "zz-scaffold-x", "--profile", "bogus")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((ROOT / "packs" / "zz-scaffold-x").exists())


if __name__ == "__main__":
    unittest.main()
