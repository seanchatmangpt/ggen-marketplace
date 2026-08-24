import hashlib, json

def canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"))

def issue(subject,generation,strategy,standing):
    body={"schema":"ggen.evidence-capital-control-policy/1","subject":subject,"generation":generation,"strategy":strategy,"standing":standing,"authority":"SELECT","actuation_performed":False}
    return {**body,"digest":hashlib.sha256(canonical(body).encode()).hexdigest()}

def replay(receipt):
    digest=receipt["digest"]; body={k:v for k,v in receipt.items() if k!="digest"}
    if body.get("authority")!="SELECT" or body.get("actuation_performed") is not False: raise ValueError("REFUSED[AUTHORITY_DRIFT]")
    if hashlib.sha256(canonical(body).encode()).hexdigest()!=digest: raise ValueError("REFUSED[RECEIPT_TAMPER]")
    return "REPLAY_MATCH"
