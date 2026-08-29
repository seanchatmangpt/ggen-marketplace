import unittest
from scripts.receipt import issue,replay

class ReceiptCourt(unittest.TestCase):
    def test_replay_and_tamper(self):
        r=issue("repo@"+"a"*40,7,"MAX_GAIN","PARTIAL_ALIVE")
        self.assertEqual(replay(r),"REPLAY_MATCH")
        bad=dict(r); bad["strategy"]="DO"
        with self.assertRaises(ValueError): replay(bad)
        bad=dict(r); bad["authority"]="DO"
        with self.assertRaises(ValueError): replay(bad)

if __name__=="__main__": unittest.main()
