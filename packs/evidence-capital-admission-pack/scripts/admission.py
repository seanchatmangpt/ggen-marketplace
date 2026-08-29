from dataclasses import dataclass

class Refused(ValueError): pass

@dataclass(frozen=True)
class Capital:
    nominal: int
    structural_units: int
    correlation_adjusted: float
    false_independent_rate: float

    @property
    def effective(self) -> float:
        return min(float(self.nominal), float(self.structural_units), self.correlation_adjusted)

def admit(capital: Capital, min_effective: float = 2.0, max_false_independent: float = 0.20) -> Capital:
    if capital.nominal < 1 or capital.structural_units < 1 or capital.correlation_adjusted <= 0:
        raise Refused("INVALID_EVIDENCE_CAPITAL")
    if capital.effective < min_effective:
        raise Refused("PSEUDO_QUORUM")
    if capital.false_independent_rate > max_false_independent:
        raise Refused("FALSE_INDEPENDENCE_UNCALIBRATED")
    return capital
