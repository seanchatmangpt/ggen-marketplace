def horvitz_thompson(rows):
    rows=tuple(rows)
    if not rows: return 0.0
    total=0.0
    for propensity, relief in rows:
        if propensity <= 0 or propensity > 1:
            raise ValueError("REFUSED[PROPENSITY_SUPPORT]")
        total += relief / propensity
    return total / len(rows)

def self_normalized(rows):
    rows=tuple(rows)
    if not rows: return 0.0
    weights=[]
    for propensity, relief in rows:
        if propensity <= 0 or propensity > 1:
            raise ValueError("REFUSED[PROPENSITY_SUPPORT]")
        weights.append((1.0/propensity, relief))
    denom=sum(w for w,_ in weights)
    return sum(w*y for w,y in weights)/denom
