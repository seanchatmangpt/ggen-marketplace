#!/usr/bin/env python3
import hashlib, json, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
canonical=json.dumps(p, sort_keys=True, separators=(',', ':')).encode()
print(hashlib.sha256(canonical).hexdigest())
