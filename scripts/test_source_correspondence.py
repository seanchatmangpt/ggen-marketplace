#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check_source_correspondence.py")
spec = importlib.util.spec_from_file_location("source_correspondence", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SourceCorrespondenceTests(unittest.TestCase):
    def test_clap_command_projection_matches_source_pairs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src/nouns").mkdir(parents=True)
            (root / "src/nouns/git.rs").write_text(
                '#[verb("status")]\nfn status() {}\n#[verb("close")]\nfn close() {}\n',
                encoding="utf-8",
            )
            ontology = root / "ontology.ttl"
            ontology.write_text(
                'cc:a a cnv:Command ; cnv:noun "git" ; cnv:verb "status" .\n'
                'cc:b a cnv:Command ; cnv:noun "git" ; cnv:verb "close" .\n',
                encoding="utf-8",
            )
            self.assertEqual(module.clap_commands(root, "src/nouns"), {("git", "status"), ("git", "close")})
            self.assertEqual(module.ontology_commands(ontology, "cnv:Command", "cnv:noun", "cnv:verb"), {("git", "status"), ("git", "close")})

    def test_cargo_workspace_uses_package_name_not_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "crates/miniml-core").mkdir(parents=True)
            (root / "Cargo.toml").write_text('[workspace]\nmembers = ["crates/miniml-core"]\n', encoding="utf-8")
            (root / "crates/miniml-core/Cargo.toml").write_text('[package]\nname = "miniml"\nversion = "1.0.0"\n', encoding="utf-8")
            self.assertEqual(module.cargo_workspace_subjects(root), {"miniml"})


if __name__ == "__main__":
    unittest.main()
