from dataclasses import dataclass
from datetime import datetime
import re

class Refused(ValueError):
    pass

@dataclass(frozen=True)
class Subject:
    repo: str
    sha: str
    semantic_digest: str
    generation: int
    def __post_init__(self):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.repo): raise Refused("REFUSED[INVALID_REPO]")
        if not re.fullmatch(r"[0-9a-f]{40}", self.sha): raise Refused("REFUSED[INEXACT_SUBJECT]")
        if not re.fullmatch(r"[0-9a-f]{64}", self.semantic_digest): raise Refused("REFUSED[INVALID_SEMANTIC_DIGEST]")
        if self.generation < 0: raise Refused("REFUSED[INVALID_GENERATION]")

@dataclass(frozen=True)
class Trial:
    subject: Subject
    trial_id: str
    model_digest: str
    evidence_root: str
    claimed_capital: float
    prediction: float
    truth: float
    baseline_loss: float
    augmented_loss: float
    information_gain: float
    observed_at: datetime
    current: bool = True
    def __post_init__(self):
        if not self.trial_id: raise Refused("REFUSED[EMPTY_TRIAL_ID]")
        if len(self.model_digest) != 64 or len(self.evidence_root) != 64: raise Refused("REFUSED[INVALID_TRIAL_DIGEST]")
        if self.observed_at.tzinfo is None: raise Refused("REFUSED[NAIVE_TIME]")
        if self.claimed_capital < 0 or not 0 <= self.prediction <= 1 or not 0 <= self.truth <= 1: raise Refused("REFUSED[INVALID_TRIAL_VALUE]")
        if min(self.baseline_loss, self.augmented_loss, self.information_gain) < 0: raise Refused("REFUSED[NEGATIVE_REALIZATION_VALUE]")
