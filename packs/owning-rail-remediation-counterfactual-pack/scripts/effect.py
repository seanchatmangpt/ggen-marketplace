from .models import Refused

def horvitz_thompson(outcomes):
    values=tuple(outcomes)
    if not values: raise Refused("REFUSED_EMPTY_REMEDIATION_SAMPLE")
    return sum(o.relief/o.propensity for o in values)/len(values)

def self_normalized(outcomes):
    values=tuple(outcomes)
    if not values: raise Refused("REFUSED_EMPTY_REMEDIATION_SAMPLE")
    weights=[1/o.propensity for o in values]
    return sum(w*o.relief for w,o in zip(weights,values))/sum(weights)
