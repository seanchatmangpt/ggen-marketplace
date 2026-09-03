import unittest
from scripts.compatibility import normalize,compatible
class T(unittest.TestCase):
 def test_symmetric(self):
  g=normalize([('a','b'),('b','c')]); self.assertTrue(compatible(g,['a','b'])); self.assertFalse(compatible(g,['a','c']))
if __name__=='__main__': unittest.main()
