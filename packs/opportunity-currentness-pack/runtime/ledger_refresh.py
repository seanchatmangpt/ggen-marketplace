#!/usr/bin/env python3
import hashlib,json,re,sys
SHA=re.compile(r'^[0-9a-f]{40}$')
def canonical(x): return json.dumps(x,sort_keys=True,separators=(',',':'))
def refresh(row):
    opportunity=row.get('opportunity'); capability=row.get('capability_head'); merge=row.get('merge_sha'); source=row.get('source_ledger')
    if not isinstance(opportunity,str) or not opportunity: raise ValueError('REFUSED[INVALID_OPPORTUNITY]')
    if not isinstance(source,str) or not source.endswith('.jsonl'): raise ValueError('REFUSED[INVALID_SOURCE_LEDGER]')
    if not all(isinstance(x,str) and SHA.fullmatch(x) for x in [capability,merge]): raise ValueError('REFUSED[INEXACT_HEAD]')
    fact={'type':'opportunity-realization','opportunity':opportunity,'source_ledger':source,'capability_head':capability,'merge_sha':merge,'standing':'ALIVE','authority':'OBSERVE|VERIFY|CONSTRUCT','actuation_performed':False}
    fact['receipt_digest']=hashlib.sha256(canonical(fact).encode()).hexdigest()
    return fact
if __name__=='__main__':
    try: print(canonical(refresh(json.load(sys.stdin))))
    except (ValueError,json.JSONDecodeError) as e: print(str(e),file=sys.stderr); raise SystemExit(2)
