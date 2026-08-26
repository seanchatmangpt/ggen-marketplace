import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "templates" / "consumer-subject.json.tmpl"


class FrontmatterDriverCourt(unittest.TestCase):
    def test_pack_template_has_explicit_shared_graph_driver(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("sparql:", text)
        self.assertIn("for_each: ready_set", text)
        self.assertIn('FILTER(?compatibility_state = "COMPATIBLE_READY")', text)
        self.assertIn("FILTER NOT EXISTS { ?target fta:blocker ?blocker }", text)
        self.assertIn("ORDER BY ?rank ?repo", text)
        self.assertIn("{{ row.rank }}", text)
        self.assertIn("{{ row.producer_head }}", text)
        self.assertNotIn("{{ rank }}", text)


if __name__ == "__main__":
    unittest.main()
