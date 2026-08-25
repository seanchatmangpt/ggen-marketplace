import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'latency.py'; s=importlib.util.spec_from_file_location('l',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
out=m.evaluate([{'discovered_at':'2026-08-25T00:00:00Z','realized_at':'2026-08-25T00:00:10Z'},{'discovered_at':'2026-08-25T00:00:00Z','realized_at':'2026-08-25T00:00:30Z'},{'discovered_at':'2026-08-25T00:00:00Z','realized_at':None}])
assert out['samples_seconds']==[10.0,30.0]
assert out['median_seconds']==20.0 and out['unrealized_count']==1
