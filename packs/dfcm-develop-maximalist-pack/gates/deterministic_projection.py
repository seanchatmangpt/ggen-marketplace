import hashlib, json
def fingerprint(value) -> str:
    payload=json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
    return hashlib.sha256(payload).hexdigest()
def require_same(left,right):
    a,b=fingerprint(left),fingerprint(right)
    if a != b:
        raise ValueError("REFUSED[NONDETERMINISTIC_PROJECTION]")
    return a
