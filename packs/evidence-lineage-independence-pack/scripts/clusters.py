def clusters(rows):
 rows=list(rows);parent={r.evidence_id:r.evidence_id for r in rows}
 def f(x):
  while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
  return x
 def u(a,b):
  a=f(a);b=f(b)
  if a!=b:parent[b]=a
 for i,a in enumerate(rows):
  for b in rows[i+1:]:
   if a.failure_domain==b.failure_domain or a.ancestors&b.ancestors or a.model_digest==b.model_digest or a.implementation_digest==b.implementation_digest:u(a.evidence_id,b.evidence_id)
 g={}
 for r in rows:g.setdefault(f(r.evidence_id),set()).add(r.evidence_id)
 return tuple(frozenset(v) for v in g.values())
