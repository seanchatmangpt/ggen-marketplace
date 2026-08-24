import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Trial,Refused
from scripts.monotonicity import require_monotone_realization

class T(unittest.TestCase):
    def test_more_claimed_capital_cannot_realize_less_value(self):
        s=Subject("o/r","a"*40,"b"*64,1); now=datetime.now(timezone.utc)
        rows=[
          Trial(s,"a","c"*64,"d"*64,1,0.7,1,1,0.4,0.1,now),
          Trial(s,"b","c"*64,"e"*64,2,0.7,1,1,0.9,0.1,now),
        ]
        with self.assertRaises(Refused): require_monotone_realization(rows,tolerance=0.01)
