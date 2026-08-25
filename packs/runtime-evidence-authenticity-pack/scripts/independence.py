from .types import Refused
def require_independent_roots(rows,minimum=2):
    roots={(r.origin,r.source_digest) for r in rows}
    if len(roots)<minimum: raise Refused("REFUSED[PSEUDO_INDEPENDENT_EVIDENCE]")
    return roots
