from .types import Refused

def gamma_robustness(rows, max_gamma=3.0, min_utility=0.0):
    grouped = {}
    for d, o in rows:
        if d.gamma > max_gamma:
            raise Refused("REFUSED[GAMMA_OUT_OF_BOUND]")
        grouped.setdefault(d.strategy, []).append((d.gamma, o.realized_utility))
    result = {}
    for strategy, values in grouped.items():
        values = sorted(values)
        if any(next_value > value + 1e-12 for (_, value), (_, next_value) in zip(values, values[1:])):
            raise Refused("REFUSED[NON_MONOTONE_GAMMA_REALIZATION]")
        result[strategy] = min(value for _, value in values) >= min_utility
    return result
