from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class Calibration:
    support: int
    mae: float
    false_safe_rate: float
    wilson_upper: float
    state: str

def _wilson_upper(k: int, n: int, z: float = 1.96) -> float:
    if n <= 0: return 1.0
    p = k / n
    d = 1 + z*z/n
    c = p + z*z/(2*n)
    r = z*sqrt((p*(1-p)+z*z/(4*n))/n)
    return min(1.0,(c+r)/d)

def calibrate(rows, min_support=5, max_false_safe=0.2, max_mae=0.25):
    rows=tuple(rows); n=len(rows)
    if not n: return Calibration(0,0.0,0.0,1.0,"INSUFFICIENT")
    mae=sum(r.error for r in rows)/n
    fs=sum(1 for r in rows if r.false_safe)
    upper=_wilson_upper(fs,n)
    state="INSUFFICIENT" if n<min_support else ("CALIBRATED" if fs/n<=max_false_safe and mae<=max_mae else "UNRELIABLE")
    return Calibration(n,mae,fs/n,upper,state)
