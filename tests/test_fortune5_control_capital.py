import pathlib
import re
import tomllib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKS = (
    "counterfactual-frontier-replay-pack",
    "runtime-evidence-authenticity-pack",
    "runtime-evidence-authenticity-control-pack",
    "owning-rail-observability-pack",
    "owning-rail-remediation-pack",
)


class Fortune5ControlCapitalCourt(unittest.TestCase):
    def test_required_reusable_packs_are_canonical_marketplace_source(self):
        for name in PACKS:
            pack = ROOT / "packs" / name
            self.assertTrue((pack / "pack.toml").is_file(), name)
            self.assertTrue((pack / "ontology.ttl").is_file(), name)

    def test_generation_manifests_use_current_rules_schema(self):
        for name in PACKS:
            manifest = ROOT / "packs" / name / "ggen.toml"
            if not manifest.exists():
                continue
            text = manifest.read_text()
            self.assertNotIn("[[generation]]", text, name)
            parsed = tomllib.loads(text)
            generation = parsed.get("generation", {})
            self.assertIsInstance(generation, dict, name)
            self.assertTrue(generation.get("rules"), name)

    def test_generation_templates_use_canonical_tera_identity(self):
        for name in PACKS:
            pack = ROOT / "packs" / name
            manifest = pack / "ggen.toml"
            if manifest.exists():
                self.assertNotIn(".tmpl", manifest.read_text(), name)
            templates = pack / "templates"
            if templates.exists():
                legacy = sorted(path.name for path in templates.glob("*.tmpl"))
                self.assertEqual(legacy, [], f"{name}: legacy template aliases {legacy}")

    def test_exact_subject_and_zero_ambient_do_laws_remain_source_visible(self):
        corpus = "\n".join((ROOT / "packs" / name / "ontology.ttl").read_text() for name in PACKS)
        self.assertRegex(corpus, re.compile(r"requiresExactSubject\s+true", re.I))
        self.assertIn("BRCE_ONLY", corpus)

    def test_enterprise_controls_cover_evidence_owner_and_counterfactual_boundaries(self):
        paths = {
            p.name
            for name in PACKS
            for p in (ROOT / "packs" / name / "queries").glob("*")
            if p.is_file()
        }
        self.assertTrue(any("frontier" in p for p in paths))
        self.assertTrue(any("failure" in p or "owner" in p for p in paths))
        self.assertTrue(any("authentic" in p or "evidence" in p or "falsifier" in p for p in paths))


if __name__ == "__main__":
    unittest.main()
