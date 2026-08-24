from dataclasses import dataclass

@dataclass(frozen=True)
class EvidenceOption:
    name: str
    expected_blocker_reduction: float
    confidence_gain: float
    cost: float

    @property
    def net_value(self):
        return self.expected_blocker_reduction + self.confidence_gain - self.cost


def select(options):
    values=tuple(options)
    if not values:
        raise ValueError("REFUSED[EMPTY_EVIDENCE_OPTIONS]")
    ranked=tuple(sorted(values,key=lambda x:(-x.net_value,x.cost,x.name)))
    if ranked[0].net_value <= 0:
        raise ValueError("REFUSED[NONPOSITIVE_REMEDIATION_INFORMATION_VALUE]")
    return ranked
