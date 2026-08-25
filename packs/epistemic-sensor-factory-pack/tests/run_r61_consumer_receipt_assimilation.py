#!/usr/bin/env python3
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
queries=sorted((ROOT/'queries').glob('11*_r61_*.rq'))
assert len(queries)==42, f'expected 42 R61 sensors, got {len(queries)}'
for q in queries:
    text=q.read_text()
    assert 'SELECT' in text and 'esf:' in text, q
fixture=(ROOT/'fixtures/r61-consumer-receipt-assimilation.ttl').read_text()
for token in ['e7bc695976bba37d1abf73a266da1b2267ca2a1d','ConsumerExecutionReceipt','DependencyReliefEvidence','standing "ALIVE"','replayVerified true']:
    assert token in fixture, token
ontology=(ROOT/'ontology.r61-consumer-receipt-assimilation.ttl').read_text()
for token in ['prov:','dqv:','dcat:','dcterms:','odrl:','consequentialDo "PROHIBITED"']:
    assert token in ontology, token
print('R61 receipt-assimilation court: PASS; sensors=42; consequential_do=false')
