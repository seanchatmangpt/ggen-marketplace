from dataclasses import dataclass

class Refused(ValueError): pass

@dataclass(frozen=True)
class Candidate:
    name: str
    evidence: int
    uncertainty: float
    rollback_cost: float
    dependency_relief: float
    reuse: float

def admit(c):
    if c.evidence < 2: raise Refused("INSUFFICIENT_EVIDENCE")
    if c.uncertainty > 0.25: raise Refused("UNCERTAINTY_TOO_WIDE")
    if c.rollback_cost > 5.0: raise Refused("ROLLBACK_TOO_EXPENSIVE")
    return c

def dominates(a,b):
    av=(-a.dependency_relief,-a.reuse,a.uncertainty,a.rollback_cost)
    bv=(-b.dependency_relief,-b.reuse,b.uncertainty,b.rollback_cost)
    return all(x<=y for x,y in zip(av,bv)) and any(x<y for x,y in zip(av,bv))

def frontier(candidates):
    cs=tuple(admit(c) for c in candidates)
    return tuple(sorted((c for c in cs if not any(dominates(o,c) for o in cs if o!=c)), key=lambda c:c.name))
