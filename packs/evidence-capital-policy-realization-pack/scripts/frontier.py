from .types import Refused

def current_frontier(decisions):
    by = {}
    for decision in decisions:
        old = by.get(decision.strategy)
        if old is None or decision.subject.generation > old.subject.generation:
            by[decision.strategy] = decision
        elif decision.subject.generation == old.subject.generation and decision.model_digest != old.model_digest:
            raise Refused("REFUSED[SPLIT_CURRENT_POLICY_MODEL]")
    return tuple(by[key] for key in sorted(by))
