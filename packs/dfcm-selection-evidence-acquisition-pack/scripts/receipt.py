import hashlib,json
class Refused(ValueError): pass
def manufacture(source,experiment):
    body={'schema':'chatman.selection-evidence-acquisition/1','source':source,'experiment':experiment,'authority':'SELECT','actuation_performed':False}
    return {'body':body,'digest':hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
def replay(receipt):
    body=receipt['body']
    if body.get('authority')!='SELECT' or body.get('actuation_performed') is not False: raise Refused('REFUSED[RECEIPT_AUTHORITY_DRIFT]')
    expected=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if expected!=receipt.get('digest'): raise Refused('REFUSED[RECEIPT_TAMPER]')
    return 'REPLAY_MATCH'
