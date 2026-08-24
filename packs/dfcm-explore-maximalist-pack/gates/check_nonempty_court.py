#!/usr/bin/env python3
import json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
if not p.get('candidates'):
    raise SystemExit('REFUSED:EMPTY_COMPARISON_COURT')
