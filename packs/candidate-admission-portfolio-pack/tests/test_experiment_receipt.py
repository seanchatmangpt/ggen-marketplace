import unittest
from scripts.experiment import value_of_information, select
from scripts.receipt import make,replay

class ExperimentReceiptCourt(unittest.TestCase):
    def test_positive_voi_selects(self):
        voi=value_of_information(.5,.9,.1,.01)
        self.assertGreater(voi,0)
        self.assertEqual(select([("slow",.1),("fast",voi)])[0],"fast")
    def test_receipt_tamper_refuses(self):
        r=make("repo@"+"a"*40,["a","b"],"PARETO")
        self.assertEqual(replay(r),"REPLAY_MATCH")
        r["body"]["strategy"]="DO"
        with self.assertRaises(ValueError): replay(r)

if __name__=="__main__": unittest.main()
