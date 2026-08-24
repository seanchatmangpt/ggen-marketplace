import hashlib,json
def manufacture(subject,calibration,worst,status):
 body={'schema':'chatman.evidence-capital-control-realization/1','repo':subject.repo,'sha':subject.sha,'semantic_digest':subject.semantic_digest,'generation':subject.generation,'support':calibration.support,'mae':calibration.mae,'false_positive_rate':calibration.false_positive_rate,'worst_stratum_gain':worst[0],'standing':status,'authority':'OBSERVE|VERIFY','actuation_performed':False}
 raw=json.dumps(body,sort_keys=True,separators=(',',':'))
 return {'body':body,'sha256':hashlib.sha256(raw.encode()).hexdigest()}
