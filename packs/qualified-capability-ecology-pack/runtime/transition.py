"""Lifecycle transitions for QCE runtime consumers."""
from __future__ import annotations
from dataclasses import replace
from .model import Capability, CapabilityState

def qualify(capability: Capability, qualification_digest: str, replay_digest: str) -> Capability:
    return replace(capability,state=CapabilityState.QUALIFIED,qualification_digest=qualification_digest,replay_digest=replay_digest)

def freeze(capability: Capability) -> Capability:
    if capability.state is not CapabilityState.QUALIFIED:
        raise ValueError("qualification required before freeze")
    return replace(capability,state=CapabilityState.FROZEN)

def retire(capability: Capability) -> Capability:
    return replace(capability,state=CapabilityState.RETIRED)
