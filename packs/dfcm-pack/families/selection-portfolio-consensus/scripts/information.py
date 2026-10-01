from math import log2

def entropy(probabilities):
    ps = tuple(float(p) for p in probabilities if p > 0)
    total = sum(ps)
    if total <= 0:
        return 0.0
    norm = [p / total for p in ps]
    return -sum(p * log2(p) for p in norm)

def information_gain(prior, posterior):
    return entropy(prior) - entropy(posterior)
