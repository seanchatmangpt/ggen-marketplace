from .types import Refused
def admit(subject,rows,now):
 seen=set();out=[]
 for r in rows:
  if r.subject!=subject: raise Refused('REFUSED[FOREIGN_SUBJECT]')
  if r.observed_at.tzinfo is None: raise Refused('REFUSED[NAIVE_TIME]')
  if r.observed_at>now: raise Refused('REFUSED[FUTURE_EVIDENCE]')
  if not r.observation_id or r.observation_id in seen: raise Refused('REFUSED[DUPLICATE_OR_EMPTY_EVIDENCE]')
  if min(r.baseline_loss,r.realized_loss,r.acquisition_cost,r.latency_ms)<0: raise Refused('REFUSED[INVALID_REALIZATION]')
  if r.alternative_observed and (r.counterfactual_loss is None or r.counterfactual_loss<0): raise Refused('REFUSED[MISSING_OBSERVED_ALTERNATIVE]')
  if not r.alternative_observed and r.counterfactual_loss is not None: raise Refused('REFUSED[FABRICATED_COUNTERFACTUAL]')
  seen.add(r.observation_id);out.append(r)
 return tuple(out)
