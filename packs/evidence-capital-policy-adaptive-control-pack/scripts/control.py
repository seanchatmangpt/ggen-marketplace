from __future__ import annotations
from dataclasses import dataclass
import hashlib, json

@dataclass(frozen=True)
class PolicyOutcome:
    name: str
    gain: float
    false_capital: float
    concentration: float
    regret: float
    drift: float
    support: int

    @property
    def admitted(self) -> bool:
        return self.support >= 5 and self.false_capital <= 0.20 and self.concentration <= 0.80

def select(outcomes, strategy="MAX_GAIN"):
    admitted=[o for o in outcomes if o.admitted]
    if not admitted:
        return None
    if strategy == "MAX_GAIN":
        return max(admitted,key=lambda o:(o.gain,-o.regret,-o.false_capital,o.name))
    if strategy == "MIN_FALSE_CAPITAL":
        return min(admitted,key=lambda o:(o.false_capital,o.regret,-o.gain,o.name))
    if strategy == "MIN_CONCENTRATION":
        return min(admitted,key=lambda o:(o.concentration,o.false_capital,-o.gain,o.name))
    raise ValueError("REFUSED[UNKNOWN_CONTROL_STRATEGY]")

def acquire(outcomes):
    return tuple(sorted(o.name for o in outcomes if o.drift >= 1.0 or o.regret > 0.20))

def receipt(subject,generation,selected):
    body={"schema":"evidence-capital-policy-adaptive-control/1","subject":subject,"generation":generation,"selected":selected,"authority":"SELECT","actuation_performed":False}
    raw=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
    return body | {"digest":hashlib.sha256(raw).hexdigest()}
