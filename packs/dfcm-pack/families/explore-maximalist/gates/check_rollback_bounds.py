#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
bad=[c['id'] for c in p['candidates'] if not isinstance(c.get('rollback_cost'), int) or c['rollback_cost'] < 0 or c['rollback_cost'] > 3]
if bad:
    raise SystemExit('REFUSED:ROLLBACK_BOUND:' + ','.join(bad))
