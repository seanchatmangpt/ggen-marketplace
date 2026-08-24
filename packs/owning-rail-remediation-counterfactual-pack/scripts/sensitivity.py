from .models import Refused

def gamma_interval(effect, gamma):
    if gamma < 1: raise Refused("REFUSED_INVALID_SENSITIVITY_GAMMA")
    magnitude=abs(float(effect))
    radius=magnitude*(gamma-1)/gamma
    return (effect-radius,effect+radius)

def robust_positive(effect,gamma):
    lower,_=gamma_interval(effect,gamma)
    return lower > 0
