import unittest
from scripts.dependence import jaccard,phi
class T(unittest.TestCase):
 def test_overlap_and_phi(self):
  self.assertEqual(jaccard({"a"},{"a"}),1);self.assertAlmostEqual(phi([(0,0),(0,0),(1,1),(1,1)]),1)
