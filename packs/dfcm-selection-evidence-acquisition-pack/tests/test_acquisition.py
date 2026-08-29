import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod); return mod
acq=load('acquisition'); score=load('scoring'); receipt=load('receipt')
class AcquisitionCourt(unittest.TestCase):
    def test_selects_high_information_bounded_experiment(self):
        xs=[acq.Experiment('cheap',.3,.1,.1),acq.Experiment('strong',.8,.2,.1)]
        self.assertEqual(acq.select(xs,.5,.5).name,'strong')
    def test_information_gain_and_replay(self):
        gain=score.information_gain([.5,.5],[[.9,.1],[.1,.9]],[.5,.5]); self.assertGreater(gain,0)
        r=receipt.manufacture('x/y@'+'a'*40,'strong'); self.assertEqual(receipt.replay(r),'REPLAY_MATCH')
    def test_no_decisive_experiment_refuses(self):
        with self.assertRaises(acq.Refused): acq.select([acq.Experiment('bad',0,.1,.1)],.5,.5)
if __name__=='__main__': unittest.main()
