from dataclasses import dataclass

@dataclass(frozen=True)
class Policy:
    name: str
    realized_gain: float
    false_capital_rate: float
    root_concentration: float
    gamma: float
    support: int
    owner_standing: str = "PARTIAL_ALIVE"

HARD={"BUILD_BROKEN","BLOCKED"}

def admitted(p: Policy) -> bool:
    return p.support >= 5 and p.false_capital_rate <= .20 and p.realized_gain >= 0 and p.owner_standing not in HARD

def max_gain(policies):
    ps=[p for p in policies if admitted(p)]
    return max(ps,key=lambda p:(p.realized_gain,-p.false_capital_rate,-p.root_concentration,p.name))

def min_false_capital(policies):
    ps=[p for p in policies if admitted(p)]
    return min(ps,key=lambda p:(p.false_capital_rate,p.root_concentration,-p.realized_gain,p.name))

def min_concentration(policies):
    ps=[p for p in policies if admitted(p)]
    return min(ps,key=lambda p:(p.root_concentration,p.false_capital_rate,-p.realized_gain,p.name))
