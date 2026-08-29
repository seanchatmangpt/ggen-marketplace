from dataclasses import dataclass
class Refused(ValueError): pass
@dataclass(frozen=True)
class Experiment:
    name:str; information_gain:float; cost:float; rollback:float; authority:str='SELECT'
def select(experiments,max_cost,max_rollback):
    xs=[e for e in experiments if e.information_gain>0 and e.cost<=max_cost and e.rollback<=max_rollback]
    if not xs: raise Refused('REFUSED[NO_DECISIVE_EXPERIMENT]')
    return sorted(xs,key=lambda e:(-(e.information_gain/(1+e.cost)),e.rollback,e.name))[0]
