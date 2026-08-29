import unittest
from datetime import datetime,timezone
from scripts.types import Subject,Decision,Realization
from scripts.qualify import qualify
from scripts.replay import replay
class T(unittest.TestCase):
 def test_clean_realization_caps_positive(self):
  now=datetime.now(timezone.utc);s=Subject('seanchatmangpt/ggen-marketplace','a'*40,'b'*64,7);rows=[]
  for i,strategy in enumerate(['RETAIN','REJECT','ACQUIRE','DEFER','RETAIN']):
   d=Decision(str(i),strategy,.2,'c'*64,chr(100+i)*64);rows.append(Realization(s,d,str(i),1,.8,0,0,False,None,'m','engine','region',now))
  q=qualify(s,rows,now);self.assertEqual(q['standing'],'PARTIAL_ALIVE');self.assertFalse(q['actuation_performed']);self.assertEqual(replay(q['receipt']),'REPLAY_MATCH')
