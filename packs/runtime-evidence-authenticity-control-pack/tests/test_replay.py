import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('receipt',ROOT/'scripts'/'receipt.py'); receipt=importlib.util.module_from_spec(spec); spec.loader.exec_module(receipt)
class ReplayCourt(unittest.TestCase):
    def test_replay_tamper_and_authority_drift(self):
        r=receipt.manufacture('x/y@'+'a'*40,3,'PARTIAL_ALIVE','CONTROL_ADMITTED')
        self.assertEqual(receipt.replay(r),'REPLAY_MATCH')
        r['body']['standing']='ALIVE'
        with self.assertRaises(receipt.Refused): receipt.replay(r)
if __name__=='__main__': unittest.main()
