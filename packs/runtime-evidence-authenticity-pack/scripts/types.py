from dataclasses import dataclass
from datetime import datetime
import re
class Refused(ValueError): pass
@dataclass(frozen=True)
class Subject:
    repo:str; sha:str; semantic_digest:str; generation:int
    def __post_init__(self):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",self.repo): raise Refused("REFUSED[INVALID_REPO]")
        if not re.fullmatch(r"[0-9a-f]{40}",self.sha): raise Refused("REFUSED[INEXACT_SUBJECT]")
        if not re.fullmatch(r"[0-9a-f]{64}",self.semantic_digest): raise Refused("REFUSED[INVALID_SEMANTIC_DIGEST]")
        if self.generation<0: raise Refused("REFUSED[INVALID_GENERATION]")
@dataclass(frozen=True)
class Evidence:
    subject:Subject; evidence_id:str; origin:str; source_digest:str; observed_value:str; ground_truth_value:str
    dynamic:bool; hardcoded:bool; cross_surface_match:bool; ground_truth_match:bool; current:bool; observed_at:datetime
