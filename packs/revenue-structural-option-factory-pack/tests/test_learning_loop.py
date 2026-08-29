import pathlib, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
class LearningLoopCourt(unittest.TestCase):
 def test_learning_and_regeneration_are_modeled(self):
  t=(ROOT/'ontology.ttl').read_text(); self.assertIn('GeneralizableKnowledge',t); self.assertIn('regener',t.lower())
if __name__=='__main__': unittest.main()
