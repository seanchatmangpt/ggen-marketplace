import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Trial,Refused
from scripts.root_influence import root_influence,require_not_concentrated

class T(unittest.TestCase):
    def test_one_root_cannot_own_realized_value(self):
        s=Subject("o/r","a"*40,"b"*64,1); now=datetime.now(timezone.utc)
        rows=[]
        for i in range(5):
            root="c"*64 if i<4 else "d"*64
            augmented=0.1 if i<4 else 0.99
            rows.append(Trial(s,str(i),"e"*64,root,2,0.8,1,1,augmented,0.1,now))
        summary=root_influence(rows)
        self.assertGreater(summary["max_gain_share"],0.8)
        with self.assertRaises(Refused): require_not_concentrated(summary)
