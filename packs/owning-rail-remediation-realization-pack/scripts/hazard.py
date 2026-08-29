from dataclasses import dataclass

@dataclass(frozen=True)
class Hazard:
    regressions: int
    observations: int
    @property
    def rate(self):
        return self.regressions / self.observations if self.observations else 1.0


def estimate(pre_post_pairs):
    pairs=tuple(pre_post_pairs)
    regressions=sum(post > pre for pre,post in pairs)
    return Hazard(regressions,len(pairs))


def require_bounded(hazard: Hazard, maximum=0.2):
    if hazard.rate > maximum:
        raise ValueError("REFUSED[REMEDIATION_REGRESSION_HAZARD]")
    return hazard
