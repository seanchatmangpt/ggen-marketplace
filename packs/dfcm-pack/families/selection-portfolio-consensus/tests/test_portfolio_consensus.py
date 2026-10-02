import unittest, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.models import Candidate, Refused
from scripts.compatibility import compatible_pairs
from scripts.portfolio import maximal_portfolios
from scripts.consensus import consensus
from scripts.receipt import issue
from scripts.replay import replay

class Court(unittest.TestCase):
    def candidates(self):
        return [
            Candidate("search","a"*40,0.8,0.1,0.1,"1"*64),
            Candidate("semantic","a"*40,0.7,0.1,0.1,"2"*64),
            Candidate("distributed","a"*40,0.6,0.2,0.2,"3"*64),
        ]
    def test_maximal_compatible_portfolio_and_receipt(self):
        cs=self.candidates(); pairs=compatible_pairs(cs,{("search","semantic"),("semantic","distributed")})
        ps=maximal_portfolios(cs,pairs)
        self.assertIn(frozenset({"search","semantic"}),ps)
        r=issue("a"*40,ps[0],[c.evidence_digest for c in cs])
        self.assertEqual(replay(r),"REPLAY_MATCH")
    def test_tie_refuses(self):
        with self.assertRaises(Refused): consensus(["a","b"])

if __name__ == "__main__": unittest.main()
