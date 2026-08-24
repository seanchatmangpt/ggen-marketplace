import hashlib,json
def manufacture(subject,authenticity,calibration,standing_value):
    body={"schema":"chatman.runtime-evidence-authenticity/1","repo":subject.repo,"sha":subject.sha,"semantic_digest":subject.semantic_digest,"generation":subject.generation,"authenticity_state":authenticity.state,"calibration_state":calibration.state,"standing":standing_value,"authority":"OBSERVE|VERIFY","actuation_performed":False}
    raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    return {"body":body,"sha256":hashlib.sha256(raw.encode()).hexdigest()}
