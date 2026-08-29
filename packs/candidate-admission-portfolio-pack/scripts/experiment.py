from math import log2
from .portfolio import Refused

def entropy(p):
    if not 0 <= p <= 1: raise Refused("INVALID_PROBABILITY")
    if p in (0,1): return 0.0
    return -p*log2(p)-(1-p)*log2(1-p)

def value_of_information(prior, posterior_if_true, posterior_if_false, cost):
    if cost < 0: raise Refused("NEGATIVE_EXPERIMENT_COST")
    expected=prior*entropy(posterior_if_true)+(1-prior)*entropy(posterior_if_false)
    return entropy(prior)-expected-cost

def select(experiments):
    viable=[e for e in experiments if e[1] > 0]
    if not viable: raise Refused("NO_DECISIVE_EXPERIMENT")
    return sorted(viable,key=lambda e:(-e[1],e[0]))[0]
