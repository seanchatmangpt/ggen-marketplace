from dataclasses import dataclass
from controller import Outcome, standing
from hazard import require_bounded, estimate

@dataclass(frozen=True)
class Qualification:
    standing: str
    realized_relief: int
    regret: int
    hazard_rate: float


def qualify(outcome: Outcome, history, dependency_standing='ALIVE'):
    if dependency_standing in {'BUILD_BROKEN','BLOCKED'}:
        return Qualification(dependency_standing,0,outcome.regret,1.0)
    hz=require_bounded(estimate(history))
    return Qualification(standing(outcome),outcome.realized_relief,outcome.regret,hz.rate)
