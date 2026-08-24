import hashlib,json

def manufacture(subject, calibration, gain, information, root_summary, worst, status):
    body={
      "schema":"chatman.evidence-capital-realization/1",
      "repo":subject.repo,"sha":subject.sha,"semantic_digest":subject.semantic_digest,"generation":subject.generation,
      "calibration_state":calibration.state,"false_capital_rate":[calibration.false_capital_rate.numerator,calibration.false_capital_rate.denominator],
      "mean_loss_reduction":gain.mean_loss_reduction,"useful_rate":[gain.useful_rate.numerator,gain.useful_rate.denominator],
      "mean_information_gain":information["mean_reported_gain"],"realization_roots":root_summary["roots"],
      "worst_stratum":worst["stratum"],"worst_mean_loss_reduction":worst["mean_loss_reduction"],
      "standing":status,"authority":"OBSERVE|VERIFY","actuation_performed":False}
    raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    return {"body":body,"sha256":hashlib.sha256(raw.encode()).hexdigest()}
