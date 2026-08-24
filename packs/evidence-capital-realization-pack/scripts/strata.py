from .types import Refused

def worst_stratum(trials, key=lambda t: t.evidence_root):
    buckets={}
    for t in trials:
        buckets.setdefault(key(t),[]).append(t)
    if not buckets: raise Refused("REFUSED[EMPTY_REALIZATION_STRATA]")
    scored=[]
    for name,rows in buckets.items():
        mean=sum(t.baseline_loss-t.augmented_loss for t in rows)/len(rows)
        scored.append((mean,name,len(rows)))
    mean,name,support=min(scored)
    return {"stratum":name,"mean_loss_reduction":mean,"support":support}
