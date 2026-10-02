#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
required={'search','distributed','verification','formal','game-theory','semantics','process-intelligence','security','graph','order-theory','receipt'}
actual={c.get('family') for c in p['candidates']}
missing=required-actual
if missing:
    raise SystemExit('REFUSED:MISSING_FAMILIES:' + ','.join(sorted(missing)))
