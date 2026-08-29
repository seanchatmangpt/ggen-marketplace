def gamma_interval(effect: float, gamma: float) -> tuple[float,float]:
    if gamma < 1:
        raise ValueError("REFUSED[INVALID_GAMMA]")
    if effect >= 0:
        return effect/gamma, effect*gamma
    return effect*gamma, effect/gamma

def robust_positive(effect: float, gamma: float) -> bool:
    lower,_=gamma_interval(effect,gamma)
    return lower > 0
