from .types import Refused

def admit(subject, trials, now):
    seen=set(); admitted=[]
    for trial in trials:
        if trial.subject != subject: raise Refused("REFUSED[FOREIGN_SUBJECT]")
        if trial.observed_at > now: raise Refused("REFUSED[FUTURE_EVIDENCE]")
        if not trial.current: raise Refused("REFUSED[STALE_REALIZATION_TRIAL]")
        if trial.trial_id in seen: raise Refused("REFUSED[DUPLICATE_REALIZATION_TRIAL]")
        seen.add(trial.trial_id); admitted.append(trial)
    return tuple(admitted)
