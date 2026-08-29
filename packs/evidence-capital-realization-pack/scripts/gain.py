from dataclasses import dataclass
from fractions import Fraction

@dataclass(frozen=True)
class GainSummary:
    support: int
    mean_loss_reduction: float
    useful_rate: Fraction
    false_capital_rate: Fraction

def summarize(trials):
    rows=tuple(trials); n=len(rows)
    if not n: return GainSummary(0,0.0,Fraction(0),Fraction(0))
    reductions=[t.baseline_loss-t.augmented_loss for t in rows]
    useful=sum(r>0 for r in reductions)
    false=sum(t.claimed_capital>1 and r<=0 for t,r in zip(rows,reductions))
    return GainSummary(n,sum(reductions)/n,Fraction(useful,n),Fraction(false,n))
