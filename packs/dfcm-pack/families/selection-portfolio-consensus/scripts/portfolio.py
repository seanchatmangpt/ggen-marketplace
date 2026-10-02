from itertools import combinations
from .compatibility import is_clique
from .models import Refused

def maximal_portfolios(candidates, pairs, minimum_utility=0.0):
    eligible = tuple(c for c in candidates if c.utility_lower >= minimum_utility)
    if not eligible:
        raise Refused("REFUSED_EMPTY_ELIGIBLE_FRONTIER")
    ids = [c.candidate_id for c in eligible]
    feasible = []
    for size in range(1, len(ids)+1):
        for combo in combinations(ids, size):
            if is_clique(combo, pairs):
                feasible.append(frozenset(combo))
    maximal = [p for p in feasible if not any(p < q for q in feasible)]
    return tuple(sorted(maximal, key=lambda p: (-len(p), tuple(sorted(p)))))
