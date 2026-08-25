from dataclasses import dataclass
from fractions import Fraction
@dataclass(frozen=True)
class Authenticity:
    support:int; dynamic_rate:Fraction; cross_surface_rate:Fraction; truth_rate:Fraction; current_rate:Fraction; state:str
def measure(rows,min_support=4):
    rows=tuple(rows);n=len(rows)
    if n<min_support:return Authenticity(n,Fraction(0),Fraction(0),Fraction(0),Fraction(0),"INSUFFICIENT")
    state="UNAUTHENTIC" if any(r.hardcoded or not r.dynamic for r in rows) else ("DIVERGED" if any(not r.cross_surface_match or not r.ground_truth_match or not r.current for r in rows) else "AUTHENTIC")
    return Authenticity(n,Fraction(sum(r.dynamic and not r.hardcoded for r in rows),n),Fraction(sum(r.cross_surface_match for r in rows),n),Fraction(sum(r.ground_truth_match for r in rows),n),Fraction(sum(r.current for r in rows),n),state)
