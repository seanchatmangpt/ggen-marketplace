from dataclasses import dataclass
@dataclass(frozen=True)
class Verdict:state:str;overlap:float;max_abs_phi:float;capital:float
def classify(overlap,max_abs_phi,capital,min_capital=2.0):
 return Verdict("INDEPENDENT" if overlap==0 and max_abs_phi<=.2 and capital>=min_capital else "DEPENDENT",overlap,max_abs_phi,capital)
