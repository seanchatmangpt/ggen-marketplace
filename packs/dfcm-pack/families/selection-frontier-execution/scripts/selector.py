from dataclasses import dataclass

@dataclass(frozen=True)
class Candidate:
    name: str
    meaningful_commits: int
    merge_yield: int
    dependency_relief: float
    evidence: float
    uncertainty: float
    rollback: float


def order_key(c: Candidate):
    return (-c.meaningful_commits, -c.merge_yield, -c.dependency_relief, -c.evidence, c.uncertainty, -c.rollback, c.name)


def select(candidates):
    values = tuple(candidates)
    if not values:
        raise ValueError("REFUSED[EMPTY_CANDIDATE_FRONTIER]")
    return tuple(sorted(values, key=order_key))
