#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
required={'id','title','family','rollback_cost','falsifier'}
for c in p['candidates']:
    missing=required-set(c)
    if missing:
        raise SystemExit('REFUSED:MISSING_RECEIPT_FIELDS:' + c.get('id','UNKNOWN') + ':' + ','.join(sorted(missing)))
