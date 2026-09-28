#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from qualify_projection import digest, qualify

HERE=Path(__file__).resolve().parents[1]
root=json.loads((HERE/"fixtures/root.json").read_text())
consumers=json.loads((HERE/"fixtures/consumers.json").read_text())
receipts=[]
for c in consumers:
    mapping={"root_subject":root["exact_subject"],"consumer_subject":c["exact_subject"],
             "consumer_repo":c["consumer_repo"],"projected_terms":sorted(c["projected_terms"])}
    c={**c,"mapping_digest":digest(mapping)}
    receipt=qualify(root,c)
    if receipt["refusals"]: raise SystemExit("REFUSED:"+json.dumps(receipt,sort_keys=True))
    receipts.append(receipt)
if len({r["consumer_repo"] for r in receipts}) < 3: raise SystemExit("REFUSED[INSUFFICIENT_HETEROGENEITY]")
first=json.dumps(receipts,sort_keys=True,separators=(",",":"))
second=json.dumps(receipts,sort_keys=True,separators=(",",":"))
if first != second: raise SystemExit("REFUSED[NON_DETERMINISTIC_REPLAY]")
print(first)
