from dataclasses import dataclass
from fractions import Fraction
@dataclass(frozen=True)
class Calibration:
    support:int; false_authentic:Fraction; false_inauthentic:Fraction; state:str
def calibrate(predicted,truth,min_support=5,max_error=Fraction(1,5)):
    pairs=list(zip(predicted,truth));n=len(pairs)
    if not n:return Calibration(0,Fraction(0),Fraction(0),"INSUFFICIENT")
    fa=sum(bool(p) and not bool(t) for p,t in pairs);fi=sum((not bool(p)) and bool(t) for p,t in pairs)
    state="INSUFFICIENT" if n<min_support else ("CALIBRATED" if Fraction(max(fa,fi),n)<=max_error else "UNRELIABLE")
    return Calibration(n,Fraction(fa,n),Fraction(fi,n),state)
