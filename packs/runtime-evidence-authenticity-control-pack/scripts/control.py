from dataclasses import dataclass
class Refused(ValueError): pass
@dataclass(frozen=True)
class Policy:
    min_authenticity: float=.90; max_false_authentic_upper: float=.10; min_independent_roots: int=2
@dataclass(frozen=True)
class Measurement:
    authenticity_rate: float; false_authentic_upper: float; independent_roots: int; current: bool; owner_state: str
def decide(p,m):
    if m.owner_state in {'FAIL','BUILD_BROKEN','BLOCKED'}: return ('BUILD_BROKEN','OWNER_FAILURE_DOMINATES')
    if m.owner_state=='PENDING': return ('UNKNOWN','OWNER_PENDING')
    if not m.current: return ('UNKNOWN','STALE_MEASUREMENT')
    if m.independent_roots<p.min_independent_roots: return ('REFUSED','PSEUDO_INDEPENDENT_EVIDENCE')
    if m.authenticity_rate<p.min_authenticity: return ('UNKNOWN','AUTHENTICITY_BELOW_FLOOR')
    if m.false_authentic_upper>p.max_false_authentic_upper: return ('UNKNOWN','FALSE_AUTHENTIC_RISK_TOO_HIGH')
    return ('PARTIAL_ALIVE','CONTROL_ADMITTED')
