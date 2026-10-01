import unittest
from scripts.compatibility import normalize
from scripts.portfolio import maximal_portfolios
from scripts.selection import select
class T(unittest.TestCase):
 def test_maximal(self):
  g=normalize([('a','b'),('a','c'),('b','c'),('c','d')]); ps=maximal_portfolios(['a','b','c','d'],g); self.assertIn(('a','b','c'),ps); self.assertIn(('c','d'),ps)
 def test_select(self):
  ps=(('a','b'),('c',)); s={'a':{'evidence':2,'dependency_relief':1,'rollback':.1},'b':{'evidence':2,'dependency_relief':2,'rollback':.1},'c':{'evidence':1,'dependency_relief':9,'rollback':0}}; self.assertEqual(select(ps,s),('a','b'))
if __name__=='__main__': unittest.main()
