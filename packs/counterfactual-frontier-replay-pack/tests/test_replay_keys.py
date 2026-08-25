import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ReplayKeyCourt(unittest.TestCase):
    def test_every_composition_has_replay_key(self):
        ontology = (ROOT / "ontology.ttl").read_text(encoding="utf-8")
        compositions = len(re.findall(r"a cfr:Composition", ontology))
        keys = len(re.findall(r"cfr:replayKey", ontology))
        self.assertEqual(compositions, keys)

if __name__ == "__main__":
    unittest.main()
