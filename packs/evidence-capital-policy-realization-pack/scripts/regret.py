from .types import Refused

def observed_regret(rows, alternatives):
    out = {}
    for d, o in rows:
        vals = [value for key, value in alternatives.get(d.decision_id, ()) if key.startswith("observed:")]
        if not vals:
            raise Refused("REFUSED[UNOBSERVED_COUNTERFACTUAL]")
        out[d.decision_id] = max(vals) - o.realized_utility
    return out
