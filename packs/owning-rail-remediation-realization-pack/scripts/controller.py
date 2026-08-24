from dataclasses import dataclass

@dataclass(frozen=True)
class Outcome:
    pre_blockers: int
    post_blockers: int
    expected_relief: int

    @property
    def realized_relief(self):
        return self.pre_blockers - self.post_blockers

    @property
    def regret(self):
        return max(0, self.expected_relief - self.realized_relief)


def standing(outcome: Outcome):
    if outcome.post_blockers < 0 or outcome.pre_blockers < 0:
        raise ValueError("REFUSED[INVALID_BLOCKER_COUNT]")
    if outcome.post_blockers > outcome.pre_blockers:
        return "REGRESSED"
    if outcome.post_blockers == 0:
        return "PARTIAL_ALIVE"
    if outcome.realized_relief > 0:
        return "REALIZED"
    return "UNREALIZED"
