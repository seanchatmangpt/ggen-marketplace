from math import log2
class Refused(ValueError): pass
def entropy(probabilities):
    ps=tuple(probabilities)
    if not ps or any(p<0 or p>1 for p in ps) or abs(sum(ps)-1.0)>1e-9: raise Refused('REFUSED[INVALID_PROBABILITY_SIMPLEX]')
    return -sum(p*log2(p) for p in ps if p>0)
def information_gain(prior,posteriors,weights):
    if len(posteriors)!=len(weights) or abs(sum(weights)-1.0)>1e-9: raise Refused('REFUSED[INVALID_EXPERIMENT_MASS]')
    return entropy(prior)-sum(w*entropy(p) for w,p in zip(weights,posteriors))
def net_value(gain,cost,rollback_penalty=0.0): return gain-cost-rollback_penalty
