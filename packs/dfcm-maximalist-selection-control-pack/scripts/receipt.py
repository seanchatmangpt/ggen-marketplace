import hashlib, json

def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))

def issue(subject,policy,selected,preserved):
    body={"schema":"ggen.dfcm-maximalist-selection-control/1","subject":subject,"policy":policy,"selected":sorted(selected),"preserved":sorted(preserved),"authority":"SELECT","actuation_performed":False}
    digest=hashlib.sha256(canonical(body).encode()).hexdigest()
    return {**body,"digest":digest}

def replay(receipt):
    digest=receipt["digest"]
    body={k:v for k,v in receipt.items() if k!="digest"}
    if body.get("authority")!="SELECT" or body.get("actuation_performed") is not False:
        raise ValueError("REFUSED[AUTHORITY_DRIFT]")
    if hashlib.sha256(canonical(body).encode()).hexdigest()!=digest:
        raise ValueError("REFUSED[RECEIPT_TAMPER]")
    return "REPLAY_MATCH"
