import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Trial
from scripts.information import binary_entropy,information_value

class T(unittest.TestCase):
    def test_information_is_bounded(self):
        self.assertEqual(binary_entropy(0),0.0); self.assertEqual(binary_entropy(1),0.0)
        self.assertAlmostEqual(binary_entropy(0.5),1.0)
        s=Subject("o/r","a"*40,"b"*64,1); now=datetime.now(timezone.utc)
        rows=[Trial(s,"x","c"*64,"d"*64,2,0.9,1,1,0.4,0.3,now)]
        value=information_value(rows)
        self.assertGreater(value["mean_predictive_information"],0)
        self.assertEqual(value["mean_reported_gain"],0.3)
