import unittest
from datetime import datetime,timezone
from scripts.frontier import CapitalModel,current_frontier
from scripts.types import Subject,Trial,Refused
from scripts.drift import cusum

class T(unittest.TestCase):
    def test_frontier_and_drift(self):
        with self.assertRaises(Refused): current_frontier([CapitalModel(2,"a"*64,"CALIBRATED"),CapitalModel(2,"b"*64,"CALIBRATED")])
        s=Subject("o/r","a"*40,"c"*64,1); now=datetime.now(timezone.utc)
        rows=[Trial(s,str(i),"d"*64,"e"*64,2,0.0,1,1,0.5,0.1,now) for i in range(3)]
        self.assertTrue(cusum(rows,target_error=0.1,allowance=0,threshold=1)["drifted"])
