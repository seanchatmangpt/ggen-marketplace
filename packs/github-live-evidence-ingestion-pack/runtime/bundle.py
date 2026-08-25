#!/usr/bin/env python3
import json, sys
from collections import defaultdict

def bundle(items):
    groups=defaultdict(list)
    for item in items: groups[item['exact_subject']].append(item)
    return [{"exact_subject":s,"observations":sorted(v,key=lambda x:(x['evidence_kind'],x['receipt_digest'])),"count":len(v)} for s,v in sorted(groups.items())]

if __name__ == '__main__':
    items=[json.loads(line) for line in sys.stdin if line.strip()]
    for row in bundle(items): print(json.dumps(row,sort_keys=True,separators=(',',':')))
