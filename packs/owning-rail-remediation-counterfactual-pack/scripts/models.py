from dataclasses import dataclass
import re

SHA=re.compile(r"^[0-9a-f]{40}$")
class Refused(ValueError): pass

@dataclass(frozen=True)
class Outcome:
    remediation_id: str
    subject_sha: str
    pre_blockers: int
    post_blockers: int
    propensity: float
    rollback_cost: float

    def __post_init__(self):
        if not self.remediation_id or not SHA.fullmatch(self.subject_sha): raise Refused("REFUSED_INEXACT_REMEDIATION_SUBJECT")
        if min(self.pre_blockers,self.post_blockers) < 0: raise Refused("REFUSED_NEGATIVE_BLOCKER_COUNT")
        if not (0 < self.propensity <= 1): raise Refused("REFUSED_INVALID_PROPENSITY")
        if self.rollback_cost < 0: raise Refused("REFUSED_NEGATIVE_ROLLBACK_COST")

    @property
    def relief(self): return self.pre_blockers-self.post_blockers
