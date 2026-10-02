#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
for c in p['candidates']:
    forbidden={'execute','deploy','merge','release','send','delete'}
    tokens={t.lower() for t in str(c).replace(':',' ').replace('-',' ').split()}
    if forbidden & tokens:
        raise SystemExit('REFUSED:EXPLORE_HAS_DO_AUTHORITY:' + c['id'])
