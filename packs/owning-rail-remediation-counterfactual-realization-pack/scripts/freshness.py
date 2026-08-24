from datetime import datetime

def freshness(observed_at: datetime, now: datetime, ttl_seconds: float) -> str:
    if observed_at.tzinfo is None or now.tzinfo is None:
        raise ValueError("REFUSED[NAIVE_TIME]")
    age=(now-observed_at).total_seconds()
    if age < 0: raise ValueError("REFUSED[FUTURE_EVIDENCE]")
    if ttl_seconds < 0: raise ValueError("REFUSED[INVALID_TTL]")
    return "FRESH" if age <= ttl_seconds else "STALE"
