import hashlib,json

def make(source,candidates,strategy):
    body={"schema":"candidate-admission-portfolio/1","source":source,"candidates":sorted(candidates),"strategy":strategy,"authority":"SELECT","actuation_performed":False}
    digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"body":body,"digest":digest}

def replay(receipt):
    digest=hashlib.sha256(json.dumps(receipt["body"],sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if digest != receipt["digest"]: raise ValueError("RECEIPT_TAMPER")
    if receipt["body"]["actuation_performed"]: raise ValueError("AMBIENT_DO")
    return "REPLAY_MATCH"
