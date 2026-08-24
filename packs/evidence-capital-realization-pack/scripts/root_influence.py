from .types import Refused

def root_influence(trials):
    rows=tuple(trials)
    roots=sorted({t.evidence_root for t in rows})
    if not roots: return {"roots":0,"max_gain_share":0.0,"leave_one_root_out":{}}
    total=sum(max(0.0,t.baseline_loss-t.augmented_loss) for t in rows)
    removed={}
    for root in roots:
        removed[root]=sum(max(0.0,t.baseline_loss-t.augmented_loss) for t in rows if t.evidence_root==root)
    max_share=0.0 if total<=0 else max(removed.values())/total
    return {"roots":len(roots),"max_gain_share":max_share,"leave_one_root_out":removed}

def require_not_concentrated(summary, max_share=0.8):
    if summary["roots"] < 2: raise Refused("REFUSED[INSUFFICIENT_REALIZATION_ROOTS]")
    if summary["max_gain_share"] > max_share: raise Refused("REFUSED[REALIZED_VALUE_ROOT_CONCENTRATION]")
    return True
