from .types import Refused
ALLOWED_ORIGINS={"runtime","rpc","dom","ocel","telemetry","provider"}
def admit(subject,rows,now):
    seen=set();out=[]
    for r in rows:
        if r.subject!=subject: raise Refused("REFUSED[FOREIGN_SUBJECT]")
        if r.origin not in ALLOWED_ORIGINS: raise Refused("REFUSED[UNSUPPORTED_EVIDENCE_ORIGIN]")
        if len(r.source_digest)!=64: raise Refused("REFUSED[INVALID_SOURCE_DIGEST]")
        if r.observed_at.tzinfo is None: raise Refused("REFUSED[NAIVE_TIME]")
        if r.observed_at>now: raise Refused("REFUSED[FUTURE_EVIDENCE]")
        if r.evidence_id in seen: raise Refused("REFUSED[DUPLICATE_EVIDENCE]")
        seen.add(r.evidence_id);out.append(r)
    return tuple(out)
