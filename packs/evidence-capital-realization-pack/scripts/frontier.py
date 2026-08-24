from dataclasses import dataclass
from .types import Refused

@dataclass(frozen=True)
class CapitalModel:
    generation: int
    digest: str
    state: str
    def __post_init__(self):
        if self.generation < 0 or len(self.digest) != 64: raise Refused("REFUSED[INVALID_CAPITAL_MODEL]")
        if self.state not in {"CALIBRATED","UNRELIABLE","INSUFFICIENT"}: raise Refused("REFUSED[INVALID_MODEL_STATE]")

def current_frontier(models):
    rows=tuple(models)
    if not rows: raise Refused("REFUSED[EMPTY_CAPITAL_FRONTIER]")
    generation=max(m.generation for m in rows)
    current=[m for m in rows if m.generation==generation]
    if len({m.digest for m in current}) != 1: raise Refused("REFUSED[SPLIT_CURRENT_CAPITAL_MODEL]")
    return current[0]
