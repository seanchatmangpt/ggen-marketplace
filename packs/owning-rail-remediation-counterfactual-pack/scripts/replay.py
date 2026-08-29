import hashlib,json
class Refused(ValueError): pass

def replay(receipt):
    body=receipt.get("body")
    expected=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    if receipt.get("digest")!=expected: raise Refused("REFUSED_REMEDIATION_RECEIPT_TAMPER")
    if body.get("authority")!="SELECT" or body.get("actuation_performed") is not False: raise Refused("REFUSED_REMEDIATION_AUTHORITY_DRIFT")
    return "REPLAY_MATCH"
