from dataclasses import dataclass
from datetime import datetime
import re
class Refused(ValueError): pass
@dataclass(frozen=True)
class Subject:
 repo:str; sha:str; semantic_digest:str; generation:int
 def __post_init__(self):
  if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',self.repo): raise Refused('REFUSED[INVALID_REPO]')
  if not re.fullmatch(r'[0-9a-f]{40}',self.sha): raise Refused('REFUSED[INEXACT_SUBJECT]')
  if not re.fullmatch(r'[0-9a-f]{64}',self.semantic_digest): raise Refused('REFUSED[INVALID_SEMANTIC_DIGEST]')
  if self.generation<0: raise Refused('REFUSED[INVALID_GENERATION]')
@dataclass(frozen=True)
class Decision:
 decision_id:str; strategy:str; predicted_gain:float; model_digest:str; evidence_root:str
 def __post_init__(self):
  if not self.decision_id or self.strategy not in {'RETAIN','REJECT','ACQUIRE','DEFER'}: raise Refused('REFUSED[INVALID_DECISION]')
  if self.predicted_gain<0 or len(self.model_digest)!=64 or len(self.evidence_root)!=64: raise Refused('REFUSED[INVALID_DECISION_PROVENANCE]')
@dataclass(frozen=True)
class Realization:
 subject:Subject; decision:Decision; observation_id:str; baseline_loss:float; realized_loss:float; acquisition_cost:float; latency_ms:float; alternative_observed:bool; counterfactual_loss:float|None; methodology:str; engine:str; region:str; observed_at:datetime
