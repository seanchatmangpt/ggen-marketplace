"""Ontology-backed runtime model for qualified capability ecology."""
from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable

class CapabilityState(str, Enum):
    CANDIDATE="candidate"; QUALIFIED="qualified"; FROZEN="frozen"; RETIRED="retired"

@dataclass(frozen=True)
class ExactSubject:
    repository: str
    commit: str
    artifact_digest: str
    def key(self)->str: return f"{self.repository}@{self.commit}#{self.artifact_digest}"

@dataclass(frozen=True)
class AuthorityEnvelope:
    digest: str
    delegation_depth: int = 0
    scopes: tuple[str,...] = ()

@dataclass(frozen=True)
class Capability:
    iri: str
    subject: ExactSubject
    state: CapabilityState
    authority: AuthorityEnvelope
    qualification_digest: str|None=None
    replay_digest: str|None=None

@dataclass(frozen=True)
class Substitution:
    original: Capability
    replacement: Capability
    consequence_preserved: bool
    replay_digest: str

@dataclass(frozen=True)
class Retirement:
    capability: Capability
    human_work_before: Decimal
    human_work_after: Decimal
    replay_digest: str
    @property
    def delta(self)->Decimal: return self.human_work_after-self.human_work_before

def stable_digest(value: object)->str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),default=str).encode()
    return sha256(payload).hexdigest()

def execution_closure(capabilities: Iterable[Capability])->tuple[Capability,...]:
    return tuple(sorted((c for c in capabilities if c.state is CapabilityState.FROZEN),key=lambda c:c.subject.key()))
