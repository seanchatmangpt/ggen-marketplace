import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class GenerationContractCourt(unittest.TestCase):
    def test_two_generation_rules_present(self):
        text = (ROOT / "ggen.toml").read_text(encoding="utf-8")
        self.assertEqual(text.count("[[generation.rules]]"), 2)
        self.assertIn("11-total-leverage.rq", text)
        self.assertIn("12-qualified-compositions.rq", text)

if __name__ == "__main__": unittest.main()
