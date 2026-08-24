from .models import Refused

def observed_regret(selected_relief, alternatives):
    values=tuple(alternatives)
    if not values: raise Refused("REFUSED_NO_OBSERVED_ALTERNATIVES")
    best=max(values)
    return max(0.0,best-selected_relief)

def conservative_regret(selected_relief, alternative_upper_bounds):
    bounds=tuple(alternative_upper_bounds)
    if not bounds: raise Refused("REFUSED_NO_COUNTERFACTUAL_BOUNDS")
    return max(0.0,max(bounds)-selected_relief)
