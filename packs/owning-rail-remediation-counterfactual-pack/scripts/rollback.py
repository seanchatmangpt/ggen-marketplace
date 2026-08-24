from .models import Refused

def rollback_safe(outcome, max_cost, require_nonnegative_relief=True):
    if outcome.rollback_cost > max_cost:
        raise Refused("REFUSED_ROLLBACK_BUDGET_EXCEEDED")
    if require_nonnegative_relief and outcome.relief < 0:
        raise Refused("REFUSED_REGRESSIVE_REMEDIATION")
    return True
