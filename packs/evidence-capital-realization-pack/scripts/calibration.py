from dataclasses import dataclass
from fractions import Fraction
from math import sqrt

@dataclass(frozen=True)
class CapitalCalibration:
    support: int
    false_capital_rate: Fraction
    wilson_upper: float
    state: str

def wilson_upper(errors, n, z=1.96):
    if n <= 0: return 1.0
    p=errors/n; d=1+(z*z)/n
    center=(p+(z*z)/(2*n))/d
    radius=z*sqrt((p*(1-p)+(z*z)/(4*n))/n)/d
    return min(1.0, center+radius)

def calibrate(trials, min_support=5, max_false_rate=Fraction(1,5)):
    rows=tuple(trials); n=len(rows)
    if not n: return CapitalCalibration(0,Fraction(0),1.0,"INSUFFICIENT")
    errors=sum(t.claimed_capital>1 and t.augmented_loss>=t.baseline_loss for t in rows)
    rate=Fraction(errors,n)
    state="INSUFFICIENT" if n<min_support else ("CALIBRATED" if rate<=max_false_rate else "UNRELIABLE")
    return CapitalCalibration(n,rate,wilson_upper(errors,n),state)
