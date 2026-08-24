import unittest
from scripts.receipt import make, replay

class ReceiptCourt(unittest.TestCase):
    def test_replay(self):
        r=make("repo@"+"a"*40,2.5,0.1)
        self.assertEqual(replay(r),"REPLAY_MATCH")
    def test_tamper_refuses(self):
        r=make("repo@"+"a"*40,2.5,0.1)
        r["body"]["effective"]=99
        with self.assertRaises(ValueError): replay(r)

if __name__ == "__main__": unittest.main()
