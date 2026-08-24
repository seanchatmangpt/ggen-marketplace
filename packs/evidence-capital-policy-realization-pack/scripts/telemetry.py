def project(rows, status):
    return tuple({
        "activity": "evidence_capital_policy_realization",
        "decision_id": decision.decision_id,
        "strategy": decision.strategy,
        "realized_utility": outcome.realized_utility,
        "false_capital": outcome.false_capital,
        "root_concentration": outcome.root_concentration,
        "stratum": outcome.stratum,
        "standing": status,
    } for decision, outcome in rows)
