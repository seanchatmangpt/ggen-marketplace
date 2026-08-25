"""HANDWRITTEN_IRREDUCIBLE_REASON: Wilson/Beta estimators require numerical runtime arithmetic and are canonical reusable measurement substrate."""
from math import sqrt
def wilson(success,total,z=1.959963984540054):
    if total<=0: return (0.0,1.0)
    p=success/total; d=1+z*z/total; c=(p+z*z/(2*total))/d; h=z*sqrt((p*(1-p)+z*z/(4*total))/total)/d
    return (max(0,c-h),min(1,c+h))
def beta_mean(success,failure,alpha=1,beta=1): return (success+alpha)/(success+failure+alpha+beta)
