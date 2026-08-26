import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CANONICAL = "https://ggen.dev/ontology/revenue-structural-option-factory#"
LEGACY = "https://ggen.dev/ontology/revenue-option-factory#"


class NamespaceCorrespondenceCourt(unittest.TestCase):
    def test_queries_and_gates_use_canonical_pack_namespace(self):
        surfaces = list((ROOT / "queries").glob("*.rq")) + list((ROOT / "gates").glob("*.rq"))
        self.assertGreater(len(surfaces), 0)
        for path in surfaces:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(LEGACY, text, path.name)
            if "CandidateStructure" in text or "rsof:" in text:
                self.assertIn(CANONICAL, text, path.name)


if __name__ == "__main__":
    unittest.main()
