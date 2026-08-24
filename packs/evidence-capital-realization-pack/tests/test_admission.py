import unittest
from datetime import datetime,timezone,timedelta
from scripts.types import Subject,Trial,Refused
from scripts.admission import admit

class T(unittest.TestCase):
    def trial(self, subject, trial_id, when, current=True):
        return Trial(subject,trial_id,"c"*64,"d"*64,2,0.8,1,1,0.5,0.2,when,current)
    def test_admission_fences(self):
        now=datetime.now(timezone.utc); s=Subject("o/r","a"*40,"b"*64,1); other=Subject("o/r","e"*40,"b"*64,1)
        with self.assertRaises(Refused): admit(s,[self.trial(other,"x",now)],now)
        with self.assertRaises(Refused): admit(s,[self.trial(s,"x",now+timedelta(seconds=1))],now)
        with self.assertRaises(Refused): admit(s,[self.trial(s,"x",now,False)],now)
        row=self.trial(s,"x",now)
        with self.assertRaises(Refused): admit(s,[row,row],now)
