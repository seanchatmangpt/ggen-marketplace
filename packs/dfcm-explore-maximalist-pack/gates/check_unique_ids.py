#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
ids=[c['id'] for c in p['candidates']]
if len(ids)!=len(set(ids)):
    raise SystemExit('REFUSED:DUPLICATE_CANDIDATE_ID')
