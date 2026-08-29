from math import sqrt

def wilson(successes: int, total: int, z: float = 1.96):
    if total <= 0:
        return (0.0, 1.0)
    p = successes / total
    denom = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denom
    half = z * sqrt((p * (1 - p) + z * z / (4 * total)) / total) / denom
    return (max(0.0, center - half), min(1.0, center + half))

def realized_rate(states):
    if not states:
        return 0.0
    return sum(state == "REALIZED" for state in states) / len(states)
