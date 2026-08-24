def max_relief(candidates):
    return max(candidates,key=lambda c:(c['realized_relief'],-c['cost'],c['name']))

def min_regret(candidates):
    return min(candidates,key=lambda c:(c['regret'],c['cost'],c['name']))

def min_hazard(candidates):
    return min(candidates,key=lambda c:(c['hazard'],c['cost'],c['name']))

def selector_vector(candidates):
    return {f.__name__:f(candidates)['name'] for f in (max_relief,min_regret,min_hazard)}
