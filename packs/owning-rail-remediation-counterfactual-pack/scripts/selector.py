from .models import Refused

def select(candidates,strategy):
    values=tuple(candidates)
    if not values: raise Refused("REFUSED_EMPTY_REMEDIATION_FRONTIER")
    if strategy=="MAX_RELIEF": return sorted(values,key=lambda o:(-o.relief,o.rollback_cost,o.remediation_id))[0]
    if strategy=="MIN_ROLLBACK": return sorted(values,key=lambda o:(o.rollback_cost,-o.relief,o.remediation_id))[0]
    if strategy=="MAX_RELIEF_PER_COST": return sorted(values,key=lambda o:(-(o.relief/(o.rollback_cost+1e-12)),o.remediation_id))[0]
    raise Refused("REFUSED_UNKNOWN_REMEDIATION_SELECTOR")
