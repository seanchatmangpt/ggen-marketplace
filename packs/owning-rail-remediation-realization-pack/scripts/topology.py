class Refused(ValueError):
    pass

def blocker_cut(edges, red):
    graph = {}
    for child, parent in edges:
        graph.setdefault(child, set()).add(parent)
    out = set(red)
    changed = True
    while changed:
        changed = False
        for child, parents in graph.items():
            if any(parent in out for parent in parents) and child not in out:
                out.add(child)
                changed = True
    return tuple(sorted(out))

def admit_acyclic(nodes, edges):
    graph = {node: [] for node in nodes}
    for child, parent in edges:
        if child not in graph or parent not in graph:
            raise Refused("REFUSED[UNKNOWN_RAIL]")
        graph[child].append(parent)
    active, done = set(), set()
    def visit(node):
        if node in active:
            raise Refused("REFUSED[RAIL_CYCLE]")
        if node in done:
            return
        active.add(node)
        for parent in graph[node]:
            visit(parent)
        active.remove(node)
        done.add(node)
    for node in sorted(graph):
        visit(node)
    return True
