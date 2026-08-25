"""HANDWRITTEN_IRREDUCIBLE_REASON: timestamp freshness/invalidation is runtime comparison, not structural generation."""
def classify(observed_at,now,ttl_seconds):
    if ttl_seconds<0: raise ValueError("INVALID_TTL")
    age=(now-observed_at).total_seconds()
    if age<0: raise ValueError("FUTURE_EVIDENCE")
    return "FRESH" if age<=ttl_seconds else "STALE"
