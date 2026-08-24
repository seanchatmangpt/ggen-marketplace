import unittest
from scripts.selection import select
class T(unittest.TestCase):
 def test_strategies_remain_distinct(self):
  c=[{'id':'gain','gain':.9,'false_rate':.2,'root_concentration':.7},{'id':'safe','gain':.4,'false_rate':.01,'root_concentration':.5},{'id':'spread','gain':.3,'false_rate':.05,'root_concentration':.1}]
  self.assertEqual(select(c,'MAX_GAIN')['id'],'gain')
  self.assertEqual(select(c,'MIN_FALSE_CAPITAL')['id'],'safe')
  self.assertEqual(select(c,'MIN_CONCENTRATION')['id'],'spread')
if __name__=='__main__': unittest.main()
