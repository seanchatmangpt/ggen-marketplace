from dataclasses import dataclass

@dataclass(frozen=True)
class Realization:
    predicted_relief: float
    realized_relief: float
    rollback_cost: float

    @property
    def error(self) -> float:
        return abs(self.predicted_relief - self.realized_relief)

    @property
    def false_safe(self) -> bool:
        return self.predicted_relief > 0 and self.realized_relief <= 0

    @property
    def signed_regret(self) -> float:
        return self.predicted_relief - self.realized_relief

    @property
    def state(self) -> str:
        if self.realized_relief < 0:
            return "REGRESSED"
        if self.realized_relief == 0:
            return "UNREALIZED"
        return "REALIZED"
