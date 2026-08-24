from dataclasses import dataclass
from datetime import datetime
import re
class Refused(ValueError):pass
@dataclass(frozen=True)
class Subject:
 repo:str;sha:str;semantic_digest:str;generation:int
 def __post_init__(self):
  if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+",self.repo):raise Refused("REFUSED[INVALID_REPO]")
  if not re.fullmatch(r"[0-9a-f]{40}",self.sha):raise Refused("REFUSED[INEXACT_SUBJECT]")
  if not re.fullmatch(r"[0-9a-f]{64}",self.semantic_digest):raise Refused("REFUSED[INVALID_SEMANTIC_DIGEST]")
@dataclass(frozen=True)
class Source:
 subject:Subject;evidence_id:str;source_digest:str;model_digest:str;implementation_digest:str;failure_domain:str;ancestors:frozenset[str];observed_at:datetime
