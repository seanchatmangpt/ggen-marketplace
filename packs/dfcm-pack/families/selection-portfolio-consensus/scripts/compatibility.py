from .models import Refused

def compatible_pairs(candidates, edges):
    ids = {c.candidate_id for c in candidates}
    pairs = {tuple(sorted(edge)) for edge in edges}
    if any(len(edge) != 2 or edge[0] == edge[1] for edge in pairs):
        raise Refused("REFUSED_INVALID_COMPATIBILITY_EDGE")
    if any(a not in ids or b not in ids for a, b in pairs):
        raise Refused("REFUSED_FOREIGN_COMPATIBILITY_EDGE")
    return frozenset(pairs)

def is_clique(candidate_ids, pairs):
    ids = tuple(sorted(candidate_ids))
    return all((a, b) in pairs for i, a in enumerate(ids) for b in ids[i+1:])
