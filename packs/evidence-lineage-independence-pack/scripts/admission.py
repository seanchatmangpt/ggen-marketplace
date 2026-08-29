from .types import Refused
def admit(subject,rows,now):
 seen=set();out=[]
 for r in rows:
  if r.subject!=subject:raise Refused("REFUSED[FOREIGN_SUBJECT]")
  if r.observed_at.tzinfo is None or r.observed_at>now:raise Refused("REFUSED[INVALID_EVIDENCE_TIME]")
  if not r.evidence_id or r.evidence_id in seen:raise Refused("REFUSED[DUPLICATE_EVIDENCE]")
  if any(len(x)!=64 for x in (r.source_digest,r.model_digest,r.implementation_digest)) or not r.failure_domain or not r.ancestors:raise Refused("REFUSED[INCOMPLETE_LINEAGE]")
  seen.add(r.evidence_id);out.append(r)
 return tuple(out)
