from math import log2

def binary_entropy(p):
    if p <= 0 or p >= 1: return 0.0
    return -(p*log2(p)+(1-p)*log2(1-p))

def information_value(trials):
    rows=tuple(trials)
    if not rows: return {"support":0,"mean_reported_gain":0.0,"mean_predictive_information":0.0}
    predictive=[1.0-binary_entropy(t.prediction) for t in rows]
    return {"support":len(rows),"mean_reported_gain":sum(t.information_gain for t in rows)/len(rows),"mean_predictive_information":sum(predictive)/len(rows)}
