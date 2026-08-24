import unittest
from fractions import Fraction
from scripts.calibration import CapitalCalibration
from scripts.standing import standing

class T(unittest.TestCase):
    def test_owner_red_dominates_green_measurement(self):
        calibration=CapitalCalibration(20,Fraction(0),0.2,"CALIBRATED")
        worst={"mean_loss_reduction":0.5}
        self.assertEqual(standing(calibration,True,False,worst,"FAIL"),"BUILD_BROKEN")
        self.assertEqual(standing(calibration,True,False,worst,"BLOCKED"),"BLOCKED")
