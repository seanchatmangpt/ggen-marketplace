import unittest
from scripts.admission import Capital, Refused, admit

class AdmissionCourt(unittest.TestCase):
    def test_distinct_capital_admits(self):
        self.assertEqual(admit(Capital(4,3,2.5,0.1)).effective,2.5)
    def test_nominal_quorum_collapses(self):
        with self.assertRaises(Refused): admit(Capital(4,1,1.0,0.1))
    def test_false_independence_refuses(self):
        with self.assertRaises(Refused): admit(Capital(4,3,2.5,0.4))

if __name__ == "__main__": unittest.main()
