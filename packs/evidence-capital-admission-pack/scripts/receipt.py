import hashlib, json

def make(subject, effective, false_independent_rate):
    body={"schema":"evidence-capital-admission/1","subject":subject,"effective":round(effective,12),"false_independent_rate":round(false_independent_rate,12),"authority":"SELECT","actuation_performed":False}
    payload=json.dumps(body,sort_keys=True,separators=(",",":")).encode()
    return {"body":body,"digest":hashlib.sha256(payload).hexdigest()}

def replay(receipt):
    payload=json.dumps(receipt["body"],sort_keys=True,separators=(",",":")).encode()
    if hashlib.sha256(payload).hexdigest()!=receipt["digest"]: raise ValueError("RECEIPT_TAMPER")
    if receipt["body"]["actuation_performed"]: raise ValueError("AMBIENT_DO")
    return "REPLAY_MATCH"
