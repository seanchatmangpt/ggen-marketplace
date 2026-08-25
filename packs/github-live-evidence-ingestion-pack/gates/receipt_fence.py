from pathlib import Path
import json,re
for path in Path(__file__).parents[1].joinpath('fixtures').glob('*.jsonl'):
    for line in path.read_text().splitlines():
        if not line.strip(): continue
        row=json.loads(line)
        digest=row.get('receipt_digest','')
        assert re.fullmatch(r'[0-9a-f]{64}',digest),'REFUSED[INVALID_RECEIPT]'
