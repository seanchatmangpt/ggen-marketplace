from dataclasses import dataclass
from fractions import Fraction
import math

@dataclass(frozen=True)
class Calibration:
    support: int
    mae: float
    bias: float
    false_positive: Fraction
    wilson_upper: float
    state: str

def wilson_upper(errors, n, z=1.96):
    if n <= 0:
        return 1.0
    p = errors / n
    den = 1 + z*z/n
    center = p + z*z/(2*n)
    margin = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return min(1.0, (center + margin) / den)

def calibrate(rows, false_threshold=0.2, min_support=5, max_mae=0.25, max_false_upper=0.6):
    if not rows:
        return Calibration(0, 0.0, 0.0, Fraction(0), 1.0, "INSUFFICIENT")
    errors = [o.realized_utility - d.predicted_utility for d, o in rows]
    n = len(errors)
    false_count = sum(1 for _, o in rows if o.false_capital > false_threshold)
    mae = sum(abs(e) for e in errors) / n
    bias = sum(errors) / n
    upper = wilson_upper(false_count, n)
    state = "INSUFFICIENT" if n < min_support else ("CALIBRATED" if mae <= max_mae and upper <= max_false_upper else "UNRELIABLE")
    return Calibration(n, mae, bias, Fraction(false_count, n), upper, state)
