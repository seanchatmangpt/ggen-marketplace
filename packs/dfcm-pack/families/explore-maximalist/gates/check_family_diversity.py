#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
families={c.get('family') for c in p['candidates'] if c.get('family')}
if len(families) < 6:
    raise SystemExit(f'REFUSED:INSUFFICIENT_DIVERSITY:{len(families)}')
