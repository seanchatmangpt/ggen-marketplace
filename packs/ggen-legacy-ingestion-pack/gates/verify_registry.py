#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PARTS=[ROOT/'registry-a.tsv',ROOT/'registry-b.tsv']
EXPECTED={'fam':24,'fmt':511,'live':62,'ctl':83,'stage':10}
STAGES={'detected','identified','hashed','decoded','parsed','normalized','observed','mapped','admitted','quarantined'}
LAWS={'unknown-opaque','opaque-artifact-preservation','no-silent-drop','observed-zero-vs-not-run','decoder-unsupported-not-invisible','quarantine-does-not-delete'}
CROWN={'exact-source-coordinate','content-digest','bounded-recursive-expansion','archive-path-traversal-refusal','sandboxed-decoder','default-deny-network','no-auto-execution','secret-fencing','tenant-isolation','data-residency','legal-hold','provenance-dag','decoder-identity','schema-validation','semantic-admission','contradiction-preservation','typed-failure','read-only-live-observation','pagination-closure','receipt-chain','independent-replay','spdx-cyclonedx-supply-chain','live-least-privilege','dry-run-before-consequential-extension','crown-independent-verifier'}
def fail(code,detail):
 print(json.dumps({'standing':'REFUSED','code':code,'detail':detail},sort_keys=True)); raise SystemExit(1)
raw=b''; rows=[]
for p in PARTS:
 b=p.read_bytes()
 if b'\r' in b: fail('NON_CANONICAL_NEWLINE',p.name)
 raw+=b
 rows.extend(csv.DictReader(b.decode().splitlines(),delimiter='\t'))
counts=Counter(r['k'] for r in rows)
if dict(counts)!=EXPECTED: fail('COUNT_MISMATCH',{'observed':dict(counts),'expected':EXPECTED})
orders=[int(r['o']) for r in rows]; ids=[r['id'] for r in rows]
if orders!=list(range(1,691)): fail('ORDER_GAP',orders[:10])
if len(ids)!=len(set(ids)): fail('DUPLICATE_IDENTIFIER','identifier collision')
families={r['id'] for r in rows if r['k']=='fam'}
for r in rows:
 if not r['id']: fail('REQUIRED_FIELD',r['o'])
 if r['k']=='fmt' and r['parent'] not in families: fail('UNKNOWN_FAMILY',r)
byid={r['id']:r for r in rows}
if LAWS-set(byid): fail('NO_SILENT_DROP_LAW',sorted(LAWS-set(byid)))
if {x for x in STAGES if byid.get(x,{}).get('k')!='stage'}: fail('STAGE_CLOSURE','missing stage')
for x in CROWN:
 r=byid.get(x)
 if not r or r['k']!='ctl' or r['pri']!='P0' or r['m']!='true': fail('CROWN_CONTROL',x)
print(json.dumps({'standing':'ALIVE','schema':'ggen.legacy.ingestion.registry.v1','sha256':hashlib.sha256(raw).hexdigest(),'rows':len(rows),'counts':dict(counts)},sort_keys=True))
