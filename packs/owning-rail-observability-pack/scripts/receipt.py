"""HANDWRITTEN_IRREDUCIBLE_REASON: canonical receipt hashing/replay is executable cryptographic runtime substrate."""
import hashlib,json
def make(subject,standing,cut):
    body={"schema":"ggen.marketplace/owning-rail-observability/1","subject":subject,"standing":standing,"blocker_cut":list(cut),"authority":"OBSERVE|VERIFY","actuation_performed":False}
    raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    return {"body":body,"sha256":hashlib.sha256(raw.encode()).hexdigest()}
def replay(r):
    body=r["body"]; raw=json.dumps(body,sort_keys=True,separators=(",",":"))
    return body.get("authority")=="OBSERVE|VERIFY" and body.get("actuation_performed") is False and hashlib.sha256(raw.encode()).hexdigest()==r.get("sha256")
