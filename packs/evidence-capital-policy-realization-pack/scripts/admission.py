from .types import Refused

def admit(subject, decisions, outcomes, now):
    dmap = {d.decision_id: d for d in decisions}
    if len(dmap) != len(tuple(decisions)):
        raise Refused("REFUSED[DUPLICATE_DECISION]")
    seen = set()
    rows = []
    for d in decisions:
        if d.subject != subject:
            raise Refused("REFUSED[FOREIGN_DECISION_SUBJECT]")
    for o in outcomes:
        if o.subject != subject:
            raise Refused("REFUSED[FOREIGN_OUTCOME_SUBJECT]")
        if o.observed_at > now:
            raise Refused("REFUSED[FUTURE_OUTCOME]")
        if not o.current:
            raise Refused("REFUSED[STALE_POLICY_OUTCOME]")
        if o.decision_id not in dmap:
            raise Refused("REFUSED[ORPHAN_OUTCOME]")
        if o.decision_id in seen:
            raise Refused("REFUSED[DUPLICATE_OUTCOME]")
        seen.add(o.decision_id)
        rows.append((dmap[o.decision_id], o))
    return tuple(rows)
