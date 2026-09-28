"""Semantic diff for exact-subject capability versions."""
from __future__ import annotations
from .model import Capability

def semantic_diff(before:Capability,after:Capability)->dict:
    return {
      "repository_changed":before.subject.repository!=after.subject.repository,
      "commit_changed":before.subject.commit!=after.subject.commit,
      "artifact_changed":before.subject.artifact_digest!=after.subject.artifact_digest,
      "state_changed":before.state!=after.state,
      "authority_changed":before.authority.digest!=after.authority.digest,
      "delegation_delta":after.authority.delegation_depth-before.authority.delegation_depth,
      "qualification_changed":before.qualification_digest!=after.qualification_digest,
      "replay_changed":before.replay_digest!=after.replay_digest,
    }
