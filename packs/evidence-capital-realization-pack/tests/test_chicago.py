import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Trial
from scripts.qualify import qualify
from scripts.replay import replay

class T(unittest.TestCase):
    def test_clean_realization_caps_at_partial_alive(self):
        s=Subject("seanchatmangpt/ex4pm","a"*40,"b"*64,7); now=datetime.now(timezone.utc)
        rows=[]
        for i in range(10):
            capital=1 if i<5 else 2
            root=("c"*64) if i%2==0 else ("d"*64)
            augmented=0.65 if capital==1 else 0.45
            prediction=0.95 if i%2==0 else 0.05
            truth=1 if i%2==0 else 0
            rows.append(Trial(s,str(i),"e"*64,root,capital,prediction,truth,1.0,augmented,0.25,now))
        q=qualify(s,rows,now)
        self.assertEqual(q["standing"],"PARTIAL_ALIVE")
        self.assertGreater(q["gain"].mean_loss_reduction,0)
        self.assertEqual(q["root_influence"]["roots"],2)
        self.assertFalse(q["drift"]["drifted"])
        self.assertFalse(q["actuation_performed"])
        self.assertEqual(replay(q["receipt"]),"REPLAY_MATCH")
