import pathlib,sys,unittest
S=pathlib.Path(__file__).parents[1]/'scripts'; sys.path.insert(0,str(S))
from selector import selector_vector
from value_of_information import EvidenceOption,select
class Court(unittest.TestCase):
    def test_selector_noncollapse(self):
        c=[{'name':'a','realized_relief':5,'regret':4,'hazard':.2,'cost':2},{'name':'b','realized_relief':4,'regret':1,'hazard':.1,'cost':1}]
        v=selector_vector(c)
        self.assertEqual(v['max_relief'],'a'); self.assertEqual(v['min_regret'],'b')
    def test_positive_voi(self):
        ranked=select([EvidenceOption('cheap',1,.5,.2),EvidenceOption('bad',0,0,1)])
        self.assertEqual(ranked[0].name,'cheap')
if __name__=='__main__': unittest.main()
