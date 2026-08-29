from .types import Refused
def observed_regret(row):
 if not row.alternative_observed or row.counterfactual_loss is None: raise Refused('REFUSED[UNOBSERVED_COUNTERFACTUAL]')
 return max(0.0,row.realized_loss-row.counterfactual_loss)
