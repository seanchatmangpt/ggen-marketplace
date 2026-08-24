from dataclasses import dataclass
from .types import Refused
@dataclass(frozen=True)
class ControlModel: strategy:str; generation:int; digest:str; state:str
def current_frontier(models):
 by={}
 for m in models:
  if m.generation<0 or len(m.digest)!=64: raise Refused('REFUSED[INVALID_CONTROL_MODEL]')
  old=by.get(m.strategy)
  if old is None or m.generation>old.generation: by[m.strategy]=m
  elif m.generation==old.generation and m.digest!=old.digest: raise Refused('REFUSED[DIVERGENT_CONTROL_FRONTIER]')
 return tuple(by[k] for k in sorted(by))
