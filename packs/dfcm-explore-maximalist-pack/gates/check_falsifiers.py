#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
bad=[c['id'] for c in p['candidates'] if not str(c.get('falsifier','')).strip()]
if bad:
    raise SystemExit('REFUSED:MISSING_FALSIFIER:' + ','.join(bad))
