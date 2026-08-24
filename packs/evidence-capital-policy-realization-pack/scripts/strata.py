def worst_stratum(rows):
    grouped = {}
    for _, outcome in rows:
        grouped.setdefault(outcome.stratum, []).append(outcome.realized_utility)
    if not grouped:
        return None
    means = {key: sum(values) / len(values) for key, values in grouped.items()}
    return min(means.items(), key=lambda item: (item[1], item[0]))
