"""RDF projection from the canonical QCE ontology into runtime objects."""
from __future__ import annotations
from pathlib import Path
from rdflib import Graph, Namespace, RDF
from .model import ExactSubject, AuthorityEnvelope, Capability, CapabilityState

QCE=Namespace("https://ggen.dev/ontology/qualified-capability-ecology#")

def _one(g,s,p,default=None):
    v=g.value(s,p); return default if v is None else v.toPython()

def load_capabilities(path: str|Path)->list[Capability]:
    g=Graph(); g.parse(path,format="turtle")
    out=[]
    state_types=((QCE.FrozenCapability,CapabilityState.FROZEN),(QCE.QualifiedCapability,CapabilityState.QUALIFIED),(QCE.CapabilityCandidate,CapabilityState.CANDIDATE),(QCE.RetiredCapability,CapabilityState.RETIRED))
    for s in sorted(set(g.subjects(RDF.type,QCE.CapabilityVersion))|set(g.subjects(RDF.type,QCE.CapabilityCandidate))|set(g.subjects(RDF.type,QCE.QualifiedCapability))|set(g.subjects(RDF.type,QCE.FrozenCapability)),key=str):
        state=next((st for typ,st in state_types if (s,RDF.type,typ) in g),CapabilityState.CANDIDATE)
        auth=g.value(s,QCE.authorityEnvelope)
        env=AuthorityEnvelope(str(_one(g,auth,QCE.authorityDigest,"")) if auth else "",int(_one(g,auth,QCE.delegationDepth,0)) if auth else 0)
        out.append(Capability(str(s),ExactSubject(str(_one(g,s,QCE.subjectRepository,"")),str(_one(g,s,QCE.subjectCommit,"")),str(_one(g,s,QCE.artifactDigest,""))),state,env,str(_one(g,s,QCE.qualificationDigest,"")) or None,str(_one(g,s,QCE.replayDigest,"")) or None))
    return out
