"""Generated interchange (PDDL-like) backend for the admitted planner IR.

Projects the admitted action catalog into a minimal, real PDDL domain/problem
text pair, for interoperability with external classical planners.

Source: ggen-marketplace planning-federation-pack (queries/model.rq).
Do not edit by hand -- regenerate via `ggen sync run`.
"""

ACTIONS = [
    {"id": "admit-observation", "precondition": "observed", "effect": "admitted"},
    {"id": "verify-goal", "precondition": "admitted", "effect": "verified"},
]


def to_pddl_domain(domain_name: str = "admitted-demo") -> str:
    lines = [f"(define (domain {domain_name})", "  (:requirements :strips)"]
    for action in ACTIONS:
        lines.append(f"  (:action {action['id']}")
        lines.append(f"    :precondition ({action['precondition']})")
        lines.append(f"    :effect ({action['effect']}))")
    lines.append(")")
    return "\n".join(lines)


def to_pddl_problem(problem_name: str, domain_name: str, initial: str, goal: str) -> str:
    return (
        f"(define (problem {problem_name})\n"
        f"  (:domain {domain_name})\n"
        f"  (:init ({initial}))\n"
        f"  (:goal ({goal})))"
    )
