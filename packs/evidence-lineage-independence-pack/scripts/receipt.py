import hashlib,json
def manufacture(subject,verdict,status):
 body={"schema":"chatman.evidence-lineage-independence/1","repo":subject.repo,"sha":subject.sha,"semantic_digest":subject.semantic_digest,"dependence_state":verdict.state,"effective_capital":verdict.capital,"standing":status,"authority":"OBSERVE|VERIFY","actuation_performed":False}
 raw=json.dumps(body,sort_keys=True,separators=(",",":"));return {"body":body,"sha256":hashlib.sha256(raw.encode()).hexdigest()}
