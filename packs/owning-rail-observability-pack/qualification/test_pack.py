import unittest, pathlib, importlib.util
ROOT=pathlib.Path(__file__).parents[1]
def load(name):
    p=ROOT/'scripts'/name; spec=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
class T(unittest.TestCase):
    def test_owner_red_dominates(self): self.assertEqual(load('standing.py').rail_standing('PASS',['FAIL']),'BUILD_BROKEN')
    def test_cycle_refused(self):
        with self.assertRaises(Exception): load('topology.py').admit_dag(['a','b'],[('a','b'),('b','a')])
    def test_reliability_bounded(self):
        lo,hi=load('reliability.py').wilson(9,10); self.assertTrue(0<=lo<=hi<=1)
    def test_receipt_replay(self):
        m=load('receipt.py'); r=m.make('o/r@'+'a'*40,'PARTIAL_ALIVE',()); self.assertTrue(m.replay(r)); r['body']['standing']='ALIVE'; self.assertFalse(m.replay(r))
