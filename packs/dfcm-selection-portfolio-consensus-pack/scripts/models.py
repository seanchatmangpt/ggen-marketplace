from dataclasses import dataclass
import re

SHA = re.compile(r"^[0-9a-f]{40}$")

class Refused(ValueError):
    pass

@dataclass(frozen=True, order=True)
class Candidate:
    candidate_id: str
    subject_sha: str
    utility_lower: float
    rollback_cost: float
    uncertainty_width: float
    evidence_digest: str

    def __post_init__(self):
        if not self.candidate_id or not SHA.fullmatch(self.subject_sha):
            raise Refused("REFUSED_INEXACT_CANDIDATE_SUBJECT")
        if self.rollback_cost < 0 or self.uncertainty_width < 0:
            raise Refused("REFUSED_NEGATIVE_SELECTION_METRIC")
        if len(self.evidence_digest) != 64:
            raise Refused("REFUSED_INVALID_EVIDENCE_DIGEST")
