from dataclasses import dataclass

@dataclass(frozen=True)
class Interval:
    lower: float
    upper: float
    def __post_init__(self):
        if self.lower > self.upper:
            raise ValueError("REFUSED[REVERSED_INTERVAL]")
    @property
    def width(self):
        return self.upper - self.lower


def require_decidable(interval: Interval, maximum_width: float):
    if interval.width > maximum_width:
        raise ValueError("REFUSED[INSUFFICIENT_SELECTION_EVIDENCE]")
    return interval
