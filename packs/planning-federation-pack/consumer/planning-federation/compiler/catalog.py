"""Generated planner action catalog for domain 'admitted-demo'.

Source: ggen-marketplace planning-federation-pack (queries/model.rq).
Do not edit by hand -- regenerate via `ggen sync run`.
"""

ACTIONS = [
    {
        "id": "admit-observation",
        "precondition": "observed",
        "effect": "admitted",
        "cost": 1,
        "duration": 1,
        "probability": 1,
        "authority_ref": "urn:authority:observe",
    },
    {
        "id": "verify-goal",
        "precondition": "admitted",
        "effect": "verified",
        "cost": 1,
        "duration": 1,
        "probability": 1,
        "authority_ref": "urn:authority:verify",
    },
]


def by_id(action_id: str):
    for action in ACTIONS:
        if action["id"] == action_id:
            return action
    return None
