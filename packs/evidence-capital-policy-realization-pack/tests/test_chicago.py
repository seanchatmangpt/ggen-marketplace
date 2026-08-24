import unittest
from datetime import datetime, timezone
from scripts.types import Subject, PolicyDecision, PolicyOutcome
from scripts.qualify import qualify
from scripts.replay import replay

class T(unittest.TestCase):
    def test_policy_realization_caps_positive_and_owner_red_dominates(self):
        now = datetime.now(timezone.utc)
        subject = Subject("seanchatmangpt/ggen-marketplace", "a"*40, "b"*64, 7)
        strategies = ["MAX_GAIN","MIN_FALSE_CAPITAL","MIN_ROOT_CONCENTRATION","GAMMA_ROBUST"]
        decisions=[]; outcomes=[]
        for i in range(8):
            strategy = strategies[i % 4]
            gamma = 1.0 + (i // 4 if strategy == "GAMMA_ROBUST" else 0)
            decisions.append(PolicyDecision(subject,str(i),strategy,.4,gamma,chr(99+i)*64))
            outcomes.append(PolicyOutcome(subject,str(i),.45,.05,.2,now,True,f"s{i%2}"))
        qualified = qualify(subject, decisions, outcomes, now)
        self.assertEqual(qualified["standing"], "PARTIAL_ALIVE")
        self.assertFalse(qualified["actuation_performed"])
        self.assertEqual(replay(qualified["receipt"]), "REPLAY_MATCH")
        self.assertEqual(qualify(subject, decisions, outcomes, now, owner_state="FAIL")["standing"], "BUILD_BROKEN")
