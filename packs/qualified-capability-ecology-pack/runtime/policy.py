"""Pure selection policy: candidate != authority != DO."""
from __future__ import annotations
from dataclasses import dataclass
from .model import Capability, CapabilityState, Substitution, Retirement, execution_closure

@dataclass(frozen=True)
class Refusal:
    code: str
    subject: str
    detail: str=""

def select_executable(capabilities):
    return execution_closure(capabilities)

def admit_runtime(cap: Capability):
    if cap.state is not CapabilityState.FROZEN:
        return Refusal("RUNTIME_REQUIRES_FROZEN",cap.iri)
    if not cap.qualification_digest:
        return Refusal("QUALIFICATION_REQUIRED",cap.iri)
    if not cap.replay_digest:
        return Refusal("REPLAY_REQUIRED",cap.iri)
    return cap

def admit_substitution(s: Substitution):
    if s.original.subject.repository != s.replacement.subject.repository:
        return Refusal("SUBJECT_REPOSITORY_DIVERGENCE",s.replacement.iri)
    if not s.consequence_preserved:
        return Refusal("CONSEQUENCE_NOT_PRESERVED",s.replacement.iri)
    if s.replacement.authority.delegation_depth > s.original.authority.delegation_depth:
        return Refusal("AUTHORITY_INCREASE",s.replacement.iri)
    if not s.replay_digest:
        return Refusal("REPLAY_REQUIRED",s.replacement.iri)
    return s

def admit_retirement(r: Retirement):
    if r.delta >= 0:
        return Refusal("HUMAN_WORK_NOT_RETIRED",r.capability.iri,str(r.delta))
    if not r.replay_digest:
        return Refusal("REPLAY_REQUIRED",r.capability.iri)
    return r
