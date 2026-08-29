import hashlib
import json

class Refused(ValueError):
    pass

def replay(receipt):
    body = receipt.get("body", {})
    if body.get("authority") != "OBSERVE|VERIFY":
        raise Refused("REFUSED[AUTHORITY_DRIFT]")
    if body.get("actuation_performed") is not False:
        raise Refused("REFUSED[ACTUATION_DRIFT]")
    raw = json.dumps(body, sort_keys=True, separators=(",", ":"))
    if hashlib.sha256(raw.encode()).hexdigest() != receipt.get("sha256"):
        raise Refused("REFUSED[RECEIPT_MISMATCH]")
    return "REPLAY_MATCH"
