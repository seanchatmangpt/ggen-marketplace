from dataclasses import dataclass
from fractions import Fraction
@dataclass(frozen=True)
class Calibration:support:int;false_independent:Fraction;state:str
def calibrate(predicted,truth,min_support=5,max_error=Fraction(1,5)):
 p=list(zip(predicted,truth));n=len(p)
 if not n:return Calibration(0,Fraction(0),"INSUFFICIENT")
 e=sum(a=="INDEPENDENT" and b!="INDEPENDENT" for a,b in p)
 return Calibration(n,Fraction(e,n),"INSUFFICIENT" if n<min_support else ("CALIBRATED" if Fraction(e,n)<=max_error else "UNRELIABLE"))
