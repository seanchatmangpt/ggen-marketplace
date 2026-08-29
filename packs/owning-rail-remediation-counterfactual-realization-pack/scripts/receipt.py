import hashlib, json

def manufacture(subject, calibration, standing):
    body={"schema":"chatman.measure-remediation-counterfactual-realization/1","subject":subject,
          "support":calibration.support,"mae":calibration.mae,"false_safe_rate":calibration.false_safe_rate,
          "wilson_upper":calibration.wilson_upper,"standing":standing,
          "authority":"OBSERVE|VERIFY","actuation_performed":False}
    raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    return {"body":body,"sha256":hashlib.sha256(raw.encode()).hexdigest()}
