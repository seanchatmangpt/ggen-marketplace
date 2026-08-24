from dataclasses import dataclass
from datetime import datetime
import re

class Refused(ValueError):
    pass

STRATEGIES = {"MAX_GAIN", "MIN_FALSE_CAPITAL", "MIN_ROOT_CONCENTRATION", "GAMMA_ROBUST"}

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
class PolicyDecision:
    subject: Subject
    decision_id: str
    strategy: str
    predicted_utility: float
    gamma: float
    model_digest: str
    def __post_init__(self):
        if not self.decision_id or self.strategy not in STRATEGIES: raise Refused("REFUSED[INVALID_POLICY_DECISION]")
        if self.gamma < 1 or len(self.model_digest) != 64: raise Refused("REFUSED[INVALID_POLICY_MODEL]")

@dataclass(frozen=True)
class PolicyOutcome:
    subject: Subject
    decision_id: str
    realized_utility: float
    false_capital: float
    root_concentration: float
    observed_at: datetime
    current: bool
    stratum: str
    def __post_init__(self):
        if not self.decision_id or not self.stratum: raise Refused("REFUSED[INVALID_POLICY_OUTCOME]")
        if not 0 <= self.false_capital <= 1 or not 0 <= self.root_concentration <= 1: raise Refused("REFUSED[INVALID_REALIZATION_RATE]")
        if self.observed_at.tzinfo is None: raise Refused("REFUSED[NAIVE_TIME]")
