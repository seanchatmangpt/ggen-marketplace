import hashlib,json

def digest(body): return hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def receipt(subject,ggen,selection,standing):
    body={'schema':'evidence-capital.realization-control/1','subject':subject,'ggen':ggen,'selection':selection,'standing':standing,'authority':'SELECT','actuation_performed':False}
    return body|{'digest':digest(body)}
def replay(value):
    body={k:v for k,v in value.items() if k!='digest'}
    return value.get('digest')==digest(body) and body.get('authority')=='SELECT' and not body.get('actuation_performed')
