from __future__ import annotations
from dataclasses import dataclass
import hashlib, json

@dataclass(frozen=True)
class Candidate:
    name: str
    evidence: float
    uncertainty: float
    rollback: float
    relief: float
    reuse: float
    required: int
    passed: int

    @property
    def closed(self) -> bool:
        return self.required > 0 and self.passed >= self.required

    @property
    def admitted(self) -> bool:
        return self.closed and self.uncertainty <= 0.35 and self.rollback <= 0.50

def dominates(a: Candidate, b: Candidate) -> bool:
    av=(a.evidence,-a.uncertainty,-a.rollback,a.relief,a.reuse)
    bv=(b.evidence,-b.uncertainty,-b.rollback,b.relief,b.reuse)
    return all(x>=y for x,y in zip(av,bv)) and any(x>y for x,y in zip(av,bv))

def frontier(candidates):
    cs=tuple(c for c in candidates if c.admitted)
    return tuple(sorted((c for c in cs if not any(dominates(o,c) for o in cs if o!=c)),key=lambda c:c.name))

def decisive_experiments(candidates):
    return tuple(sorted((c.name,c.required-c.passed,c.uncertainty) for c in candidates if not c.closed or c.uncertainty>0.20))

def receipt(subject, selected):
    body={"schema":"dfcm-selection-falsifier-closure/1","subject":subject,"selected":sorted(c.name for c in selected),"authority":"SELECT","actuation_performed":False}
    encoded=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
    return body | {"digest":hashlib.sha256(encoded).hexdigest()}
