from .types import Refused

def gain_curve(trials):
    buckets={}
    for t in trials:
        buckets.setdefault(t.claimed_capital,[]).append(t.baseline_loss-t.augmented_loss)
    return tuple((capital,sum(values)/len(values)) for capital,values in sorted(buckets.items()))

def require_monotone_realization(trials, tolerance=0.05):
    curve=gain_curve(trials)
    for (_,a),(_,b) in zip(curve,curve[1:]):
        if b + tolerance < a:
            raise Refused("REFUSED[NON_MONOTONE_CAPITAL_REALIZATION]")
    return curve
