#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
queries=[]
for q in sorted((ROOT/'queries').glob('11*_r61_*.rq')):
    ordinal=int(q.name.split('_',1)[0])
    if 1101 <= ordinal <= 1142:
        queries.append(q)
assert len(queries)==42, f'expected 42 R61 sensors, got {len(queries)}'
for q in queries:
    text=q.read_text()
    assert 'SELECT' in text and 'esf:' in text, q
projection=ROOT/'queries/1143_r61_receipt_assimilation_projection.rq'
assert projection.exists() and 'SELECT' in projection.read_text()
fixture=(ROOT/'fixtures/r61-consumer-receipt-assimilation.ttl').read_text()
for token in ['e7bc695976bba37d1abf73a266da1b2267ca2a1d','ConsumerExecutionReceipt','DependencyReliefEvidence','standing "ALIVE"','replayVerified true']:
    assert token in fixture, token
ontology=(ROOT/'ontology.r61-consumer-receipt-assimilation.ttl').read_text()
for token in ['prov:','dqv:','dcat:','dcterms:','odrl:','consequentialDo "PROHIBITED"']:
    assert token in ontology, token
manifest=(ROOT/'ggen.toml').read_text()
for token in ['consumer-receipt-assimilation-report','1143_r61_receipt_assimilation_projection.rq','consumer-receipt-assimilation-report.json.tera']:
    assert token in manifest, token
print('R61 receipt-assimilation court: PASS; sensors=42; projection=1; consequential_do=false')
