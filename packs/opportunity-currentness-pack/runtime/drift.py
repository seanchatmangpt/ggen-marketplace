#!/usr/bin/env python3
import json, re, sys
SHA=re.compile(r'^[0-9a-f]{40}$')
def evaluate(row):
    q=row.get('qualified_head'); d=row.get('default_head'); contained=row.get('contained_heads',[])
    if not all(isinstance(x,str) and SHA.fullmatch(x) for x in [q,d]): raise ValueError('REFUSED[INEXACT_HEAD]')
    if not isinstance(contained,list) or not all(isinstance(x,str) and SHA.fullmatch(x) for x in contained): raise ValueError('REFUSED[INVALID_CONTAINMENT_SET]')
    if q==d: standing='ALIVE'; state='CURRENT'
    elif q in contained: standing='ALIVE'; state='CONTAINED_AFTER_DRIFT'
    else: standing='PARTIAL_ALIVE'; state='DRIFT_UNCONTAINED'
    return {'qualified_head':q,'default_head':d,'state':state,'standing':standing,'actuation_performed':False}
if __name__=='__main__':
    try: print(json.dumps(evaluate(json.load(sys.stdin)),sort_keys=True,separators=(',',':')))
    except (ValueError,json.JSONDecodeError) as e: print(str(e),file=sys.stderr); raise SystemExit(2)
