from pathlib import Path
import unittest

from scripts.control import Candidate, frontier, decisive_experiments, receipt


class SelectionControlCourt(unittest.TestCase):
    def test_dominated_candidate_is_not_selected(self):
        strong = Candidate("strong", .9, .1, .1, .9, .9, 3, 3)
        weak = Candidate("weak", .7, .2, .2, .5, .5, 3, 3)
        self.assertEqual([c.name for c in frontier([weak, strong])], ["strong"])

    def test_unclosed_candidate_manufactures_experiment(self):
        unresolved = Candidate("u", .8, .3, .1, .7, .8, 4, 2)
        self.assertEqual(decisive_experiments([unresolved])[0][0], "u")

    def test_receipt_has_no_do_authority(self):
        c = Candidate("c", .9, .1, .1, .9, .9, 2, 2)
        r = receipt("repo/name@" + "a" * 40, [c])
        self.assertEqual(r["authority"], "SELECT")
        self.assertFalse(r["actuation_performed"])
        self.assertEqual(len(r["digest"]), 64)

    def test_ggen_manifest_uses_current_rule_schema(self):
        manifest = (Path(__file__).resolve().parents[1] / "ggen.toml").read_text()
        self.assertIn("[[generation.rules]]", manifest)
        self.assertNotIn("\n[[generation]]\n", manifest)
        self.assertIn("[ontology]", manifest)
        self.assertIn('version = "0.1.0"', manifest)


if __name__ == "__main__":
    unittest.main()
