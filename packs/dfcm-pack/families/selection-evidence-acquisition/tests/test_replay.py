import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('receipt',ROOT/'scripts'/'receipt.py'); receipt=importlib.util.module_from_spec(spec); spec.loader.exec_module(receipt)
class ReplayCourt(unittest.TestCase):
    def test_acquisition_receipt_tamper_refuses(self):
        r=receipt.manufacture('x/y@'+'a'*40,'experiment')
        self.assertEqual(receipt.replay(r),'REPLAY_MATCH')
        r['body']['actuation_performed']=True
        with self.assertRaises(receipt.Refused): receipt.replay(r)
if __name__=='__main__': unittest.main()
