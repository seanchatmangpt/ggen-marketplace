import hashlib, json

def replay(receipt):
    body=receipt.get("body",{})
    if body.get("authority") != "OBSERVE|VERIFY": raise ValueError("REFUSED[AUTHORITY_DRIFT]")
    if body.get("actuation_performed") is not False: raise ValueError("REFUSED[ACTUATION_IN_MEASURE_RECEIPT]")
    raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    if hashlib.sha256(raw.encode()).hexdigest()!=receipt.get("sha256"):
        raise ValueError("REFUSED[RECEIPT_MISMATCH]")
    return "REPLAY_MATCH"
