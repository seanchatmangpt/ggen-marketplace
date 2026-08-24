import unittest
from scripts.control import PolicyOutcome, select, acquire, receipt

class AdaptiveControlCourt(unittest.TestCase):
    def test_noncollapsed_strategies(self):
        a=PolicyOutcome("gain",.9,.10,.70,.10,.1,10)
        b=PolicyOutcome("safe",.7,.02,.30,.05,.1,10)
        self.assertEqual(select([a,b],"MAX_GAIN").name,"gain")
        self.assertEqual(select([a,b],"MIN_FALSE_CAPITAL").name,"safe")
        self.assertEqual(select([a,b],"MIN_CONCENTRATION").name,"safe")

    def test_drift_manufactures_acquisition(self):
        drifted=PolicyOutcome("drifted",.8,.10,.50,.25,1.2,10)
        self.assertEqual(acquire([drifted]),("drifted",))

    def test_receipt_cannot_report_do(self):
        r=receipt("repo/name@"+"a"*40,7,"safe")
        self.assertEqual(r["authority"],"SELECT")
        self.assertFalse(r["actuation_performed"])
        self.assertEqual(len(r["digest"]),64)

if __name__ == "__main__":
    unittest.main()
