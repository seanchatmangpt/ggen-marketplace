def realization_errors(rows):
    return tuple((d.decision_id, o.realized_utility - d.predicted_utility) for d, o in rows)

def mean_realized_utility(rows):
    return sum(o.realized_utility for _, o in rows) / len(rows) if rows else 0.0
