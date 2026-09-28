from pathlib import Path
from rdflib import Graph
import hashlib, json
ROOT=Path(__file__).parent
def qualify(path):
 g=Graph(); g.parse(ROOT/'ontology.ttl',format='turtle'); g.parse(path,format='turtle')
 return [(str(r.subject),str(r.reason)) for r in g.query((ROOT/'gates.rq').read_text())]
def receipt(path):
 p=Path(path); body={'subject':p.name,'violations':qualify(p),'authority':'none','input_digest':hashlib.sha256(p.read_bytes()).hexdigest(),'court_digest':hashlib.sha256((ROOT/'gates.rq').read_bytes()).hexdigest()}
 body['receipt_digest']=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest(); return body
if __name__=='__main__':
 p=ROOT/'witness.ttl'; a=receipt(p); b=receipt(p); assert not a['violations']; assert a==b; print(json.dumps(a,sort_keys=True))
