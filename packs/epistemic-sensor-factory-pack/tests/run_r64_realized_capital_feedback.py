#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
queries = []
for q in sorted((ROOT / 'queries').glob('13*_r64_*.rq')) + sorted((ROOT / 'queries').glob('1400_r64_*.rq')):
    ordinal = int(q.name.split('_', 1)[0])
    if 1351 <= ordinal <= 1400:
        queries.append(q)
queries = sorted(set(queries), key=lambda p: int(p.name.split('_', 1)[0]))
assert len(queries) == 50, f'expected 50 R64 courts, got {len(queries)}'
assert [int(q.name.split('_', 1)[0]) for q in queries] == list(range(1351, 1401))
for q in queries:
    text = q.read_text()
    assert text.startswith('PREFIX esf: <https://ggen.dev/ontology/epistemic-sensor-factory#>\n'), q
    assert 'ProductionFunctionObservation' in text, q
    assert 'SELECT' in text or 'ASK' in text, q
    upper = text.upper()
    for forbidden in ('INSERT ', 'DELETE ', 'LOAD ', 'CLEAR ', 'DROP ', 'CREATE ', 'MOVE ', 'COPY ', 'ADD ', 'SERVICE '):
        assert forbidden not in upper, (q, forbidden)
print('R64 realized-capital feedback court: PASS; courts=50; consequential_do=false')
