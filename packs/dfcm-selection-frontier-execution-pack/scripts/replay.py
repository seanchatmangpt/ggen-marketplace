import hashlib, json

def replay(receipt):
    expected=receipt["sha256"]
    body={k:v for k,v in receipt.items() if k!="sha256"}
    actual=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if actual != expected:
        raise ValueError("REFUSED[SELECTION_RECEIPT_TAMPER]")
    if body.get("actuation_performed") is not False or body.get("authority") != "SELECT":
        raise ValueError("REFUSED[SELECTION_AUTHORITY_DRIFT]")
    return "REPLAY_MATCH"
