"""HANDWRITTEN_IRREDUCIBLE_REASON: failure-dominant hierarchical standing is runtime algebra; templates would obscure executable semantics."""
def rail_standing(local, owners=()):
    states=[local,*owners]
    if "FAIL" in states: return "BUILD_BROKEN"
    if "REFUSED" in states: return "REFUSED"
    if any(s in {"UNKNOWN","PENDING"} for s in states): return "UNKNOWN"
    if states and all(s=="UNSUPPORTED" for s in states): return "UNSUPPORTED"
    return "PARTIAL_ALIVE"
