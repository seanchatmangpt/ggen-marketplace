"""HANDWRITTEN_IRREDUCIBLE_REASON: DAG cycle detection and blocker propagation require runtime graph traversal."""
class TopologyError(ValueError): pass
def admit_dag(nodes,edges):
    g={n:[] for n in nodes}
    for c,p in edges:
        if c not in g or p not in g: raise TopologyError("UNKNOWN_RAIL")
        g[c].append(p)
    active=set(); done=set()
    def visit(n):
        if n in active: raise TopologyError("CYCLE")
        if n in done: return
        active.add(n)
        for p in g[n]: visit(p)
        active.remove(n); done.add(n)
    for n in sorted(g): visit(n)
    return g
def blocker_cut(states,g):
    return tuple(sorted({p for c,ps in g.items() if states.get(c)=="PASS" for p in ps if states.get(p) in {"FAIL","REFUSED","UNKNOWN","PENDING"}}))
