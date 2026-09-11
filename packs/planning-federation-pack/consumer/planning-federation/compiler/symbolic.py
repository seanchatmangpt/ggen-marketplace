"""Generated symbolic (classical) planner backend.

Builds a precondition/effect closure over the admitted action catalog and
answers reachability queries with a real breadth-first search over the
generated state graph -- no external solver dependency.

Source: ggen-marketplace planning-federation-pack (queries/model.rq).
Do not edit by hand -- regenerate via `ggen sync run`.
"""

from collections import deque

ACTIONS = [
    {"id": "admit-observation", "precondition": "observed", "effect": "admitted"},
    {"id": "verify-goal", "precondition": "admitted", "effect": "verified"},
]


def plan(initial: str, goal: str):
    """Breadth-first search over admitted actions. Returns a list of action
    ids from initial to goal, or None if unreachable."""
    frontier = deque([(initial, [])])
    seen = {initial}
    while frontier:
        state, path = frontier.popleft()
        if state == goal:
            return path
        for action in ACTIONS:
            if action["precondition"] == state and action["effect"] not in seen:
                seen.add(action["effect"])
                frontier.append((action["effect"], path + [action["id"]]))
    return None
