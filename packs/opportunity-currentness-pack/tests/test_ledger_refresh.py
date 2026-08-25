import importlib.util,re
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'ledger_refresh.py'; s=importlib.util.spec_from_file_location('r',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
row={'opportunity':'x','source_ledger':'ledger.jsonl','capability_head':'1'*40,'merge_sha':'2'*40}
a=m.refresh(row); b=m.refresh(row)
assert a==b and a['standing']=='ALIVE' and a['actuation_performed'] is False
assert re.fullmatch(r'[0-9a-f]{64}',a['receipt_digest'])
