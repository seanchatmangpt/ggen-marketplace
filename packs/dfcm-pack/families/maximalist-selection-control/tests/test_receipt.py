import unittest
from scripts.receipt import issue,replay
class ReceiptCourt(unittest.TestCase):
    def test_replay(self):
        r=issue("repo@"+"a"*40,"PARETO",["a"],["b"])
        self.assertEqual(replay(r),"REPLAY_MATCH")
        bad=dict(r); bad["authority"]="DO"
        with self.assertRaises(ValueError): replay(bad)
        bad=dict(r); bad["selected"]=["x"]
        with self.assertRaises(ValueError): replay(bad)
if __name__=="__main__": unittest.main()
