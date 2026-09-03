from collections import defaultdict

def normalize(edges):
    graph=defaultdict(set)
    for left,right in edges:
        if left==right: continue
        graph[left].add(right); graph[right].add(left)
    return {k:frozenset(v) for k,v in sorted(graph.items())}

def compatible(graph, members):
    members=tuple(sorted(set(members)))
    return all(b in graph.get(a,frozenset()) for i,a in enumerate(members) for b in members[i+1:])
