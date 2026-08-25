import hashlib,json
class Refused(ValueError): pass
def manufacture(subject,generation,standing,reason):
    body={'schema':'chatman.runtime-evidence-authenticity-control/1','subject':subject,'generation':generation,'standing':standing,'reason':reason,'authority':'SELECT','actuation_performed':False}
    return {'body':body,'digest':hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()}
def replay(receipt):
    body=receipt['body']
    if body.get('authority')!='SELECT' or body.get('actuation_performed') is not False: raise Refused('REFUSED[RECEIPT_AUTHORITY_DRIFT]')
    expected=hashlib.sha256(json.dumps(body,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if expected!=receipt.get('digest'): raise Refused('REFUSED[RECEIPT_TAMPER]')
    return 'REPLAY_MATCH'
