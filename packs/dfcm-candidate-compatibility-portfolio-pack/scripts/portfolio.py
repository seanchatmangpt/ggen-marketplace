from itertools import combinations
from .compatibility import compatible

def maximal_portfolios(candidates, graph):
    items=tuple(sorted(set(candidates)))
    feasible=[]
    for size in range(1,len(items)+1):
        for subset in combinations(items,size):
            if compatible(graph,subset): feasible.append(subset)
    return tuple(p for p in feasible if not any(set(p)<set(q) for q in feasible))
