import importlib.util, pathlib, unittest
ROOT=pathlib.Path(__file__).parents[1]
def load(name):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/f'{name}.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
selector=load('selector'); uncertainty=load('uncertainty')
class Court(unittest.TestCase):
    def test_primary_ctq_dominates(self):
        a=selector.Candidate('a',30,1,1,1,0,1); b=selector.Candidate('b',29,99,99,99,0,99)
        self.assertEqual(selector.select([b,a])[0].name,'a')
    def test_uncertainty_refuses(self):
        with self.assertRaisesRegex(ValueError,'INSUFFICIENT_SELECTION_EVIDENCE'):
            uncertainty.require_decidable(uncertainty.Interval(0,1),.2)
if __name__=='__main__': unittest.main()
