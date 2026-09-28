"""Manifest composition for downstream QCE consumers."""
from __future__ import annotations
from .model import Capability
from .policy import admit_runtime

def manifest(capabilities):
    rows=[]
    for cap in sorted(capabilities,key=lambda c:c.subject.key()):
        verdict=admit_runtime(cap)
        rows.append({
            "iri":cap.iri,
            "subject":cap.subject.key(),
            "state":cap.state.value,
            "authority_digest":cap.authority.digest,
            "executable":isinstance(verdict,Capability),
            "refusal":None if isinstance(verdict,Capability) else verdict.code,
        })
    return {"schema":"ggen.qce.runtime-manifest/1","capabilities":rows}
