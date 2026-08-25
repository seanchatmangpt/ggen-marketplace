#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
queries = []
for q in sorted((ROOT / 'queries').glob('12*_r62_*.rq')):
    ordinal = int(q.name.split('_', 1)[0])
    if 1201 <= ordinal <= 1250:
        queries.append(q)
assert len(queries) == 50, f'expected 50 R62 sensors, got {len(queries)}'
for q in queries:
    text = q.read_text()
    assert 'esf:' in text, q
    assert 'DependencyReliefEvidence' in text, q
    assert any(form in text for form in ('SELECT', 'ASK')), q
    upper = text.upper()
    for forbidden in ('INSERT ', 'DELETE ', 'LOAD ', 'CLEAR ', 'DROP ', 'CREATE ', 'MOVE ', 'COPY ', 'ADD ', 'SERVICE '):
        assert forbidden not in upper, (q, forbidden)
print('R62 dependency-relief replication court: PASS; sensors=50; consequential_do=false')
