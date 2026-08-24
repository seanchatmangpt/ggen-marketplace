import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Trial
from scripts.strata import worst_stratum

class T(unittest.TestCase):
    def test_aggregate_gain_cannot_hide_negative_root(self):
        s=Subject("o/r","a"*40,"b"*64,1); now=datetime.now(timezone.utc)
        rows=[
          Trial(s,"a","c"*64,"d"*64,2,0.8,1,2,0.2,0.1,now),
          Trial(s,"b","c"*64,"e"*64,2,0.8,1,1,1.2,0.1,now),
        ]
        worst=worst_stratum(rows)
        self.assertEqual(worst["stratum"],"e"*64)
        self.assertLess(worst["mean_loss_reduction"],0)
