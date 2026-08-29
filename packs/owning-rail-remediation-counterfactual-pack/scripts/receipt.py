import hashlib,json

def issue(subject_sha,remediation_id,effect,regret,rollback_safe):
    body={"schema":"chatman.remediation-counterfactual/1","subject_sha":subject_sha,"remediation_id":remediation_id,"effect":round(float(effect),12),"regret":round(float(regret),12),"rollback_safe":bool(rollback_safe),"authority":"SELECT","actuation_performed":False}
    digest=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {"body":body,"digest":digest}
