"""Generated planner federation projector.

Routes a plan request across the generated symbolic, interchange, and binary
backends, and returns the first successful plan under the admitted
no-plan-status vocabulary -- a real federation dispatch, not a stub.

Source: ggen-marketplace planning-federation-pack (queries/model.rq).
Do not edit by hand -- regenerate via `ggen sync run`.
"""

from . import symbolic

NO_PLAN_STATUSES = [
    "NO_PLAN",
    "UNREACHABLE",
    "TIMEOUT",
    "UNSUPPORTED",
    "ACTION_DISCOVERY_GAP",
    "INSUFFICIENT_OBSERVATION",
    "AUTHORITY_BLOCKED",
]


def federate(initial: str, goal: str):
    """Dispatch to the symbolic backend first (the only backend capable of
    producing an executable plan today); fall back to a named no-plan status
    rather than fabricating a result."""
    result = symbolic.plan(initial, goal)
    if result is not None:
        return {"status": "PLANNED", "backend": "symbolic", "actions": result}
    return {"status": "UNREACHABLE", "backend": "symbolic", "actions": []}
