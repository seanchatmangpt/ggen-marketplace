from dataclasses import dataclass

@dataclass(frozen=True)
class Sensitivity:
    gamma: float
    observed_gain: float

    def lower_gain(self) -> float:
        if self.gamma < 1:
            raise ValueError("REFUSED[INVALID_GAMMA]")
        return self.observed_gain / self.gamma

    def admitted(self, minimum_gain: float = 0.0) -> bool:
        return self.lower_gain() >= minimum_gain
