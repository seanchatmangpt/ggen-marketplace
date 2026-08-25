import unittest
from pathlib import Path
ROOT = Path(__file__).parents[1]
class Contract(unittest.TestCase):
    def test_identity(self): self.assertIn('name = "github-controloutcome-observation-pack"', (ROOT/'pack.toml').read_text())
    def test_zero_do(self): self.assertNotIn('gco:actuationPerformed true', (ROOT/'ontology.ttl').read_text())
if __name__ == '__main__': unittest.main()
