import unittest
from scripts.control import classify
class T(unittest.TestCase):
 def test_positive_ceiling(self): self.assertEqual(classify(.2,.1,.4),'PARTIAL_ALIVE')
 def test_owner_red_dominates(self): self.assertEqual(classify(.2,.0,.2,'BUILD_BROKEN'),'BUILD_BROKEN')
 def test_negative_gain_refuses(self): self.assertTrue(classify(-.1,.0,.2).startswith('REFUSED'))
if __name__=='__main__': unittest.main()
