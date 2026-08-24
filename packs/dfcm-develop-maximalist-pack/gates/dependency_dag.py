def topo(graph: dict[str, list[str]]) -> tuple[str, ...]:
    visiting, done, order = set(), set(), []
    def visit(node: str):
        if node in visiting:
            raise ValueError(f"REFUSED[DEPENDENCY_CYCLE]:{node}")
        if node in done:
            return
        visiting.add(node)
        for dep in sorted(graph.get(node, [])):
            if dep not in graph:
                raise ValueError(f"REFUSED[MISSING_DEPENDENCY]:{dep}")
            visit(dep)
        visiting.remove(node); done.add(node); order.append(node)
    for node in sorted(graph): visit(node)
    return tuple(order)
