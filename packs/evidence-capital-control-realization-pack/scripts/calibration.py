from dataclasses import dataclass
from math import sqrt
from .gain import realized_gain
@dataclass(frozen=True)
class Calibration: support:int; mae:float; bias:float; false_positive_rate:float; wilson_upper:float; state:str
def wilson_upper(errors,n,z=1.96):
 if n<=0:return 1.0
 p=errors/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*sqrt((p*(1-p)+z*z/(4*n))/n)/d
 return min(1.0,c+h)
def calibrate(rows,min_support=5,max_mae=.25,max_fp=.2):
 rows=tuple(rows);n=len(rows)
 if not n:return Calibration(0,0,0,0,1,'INSUFFICIENT')
 actual=[realized_gain(r) for r in rows];errors=[abs(r.decision.predicted_gain-a) for r,a in zip(rows,actual)];signed=[r.decision.predicted_gain-a for r,a in zip(rows,actual)];fp=sum(r.decision.predicted_gain>0 and a<=0 for r,a in zip(rows,actual))
 mae=sum(errors)/n;fpr=fp/n;state='INSUFFICIENT' if n<min_support else ('CALIBRATED' if mae<=max_mae and fpr<=max_fp else 'UNRELIABLE')
 return Calibration(n,mae,sum(signed)/n,fpr,wilson_upper(fp,n),state)
