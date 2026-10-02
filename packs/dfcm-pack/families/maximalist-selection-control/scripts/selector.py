from dataclasses import dataclass
from math import log2

@dataclass(frozen=True)
class Candidate:
    name: str
    evidence: float
    uncertainty: float
    rollback: float
    dependency_relief: float
    reuse_capital: float


def dominates(a: Candidate, b: Candidate) -> bool:
    av=(a.evidence,-a.uncertainty,-a.rollback,a.dependency_relief,a.reuse_capital)
    bv=(b.evidence,-b.uncertainty,-b.rollback,b.dependency_relief,b.reuse_capital)
    return all(x>=y for x,y in zip(av,bv)) and any(x>y for x,y in zip(av,bv))


def pareto(candidates):
    cs=tuple(candidates)
    return tuple(sorted((c for c in cs if not any(dominates(o,c) for o in cs if o!=c)),key=lambda c:c.name))


def maximin(candidates):
    cs=tuple(candidates)
    return max(cs,key=lambda c:(min(c.evidence,c.dependency_relief,c.reuse_capital)-c.uncertainty-c.rollback,c.name))


def information_gain(prior: float, posterior: float) -> float:
    def h(p):
        if p in (0.0,1.0): return 0.0
        return -p*log2(p)-(1-p)*log2(1-p)
    return h(prior)-h(posterior)
