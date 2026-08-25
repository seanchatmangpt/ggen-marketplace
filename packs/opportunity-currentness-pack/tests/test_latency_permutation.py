import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'latency.py'; s=importlib.util.spec_from_file_location('l',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
rows=[{'discovered_at':'2026-08-25T00:00:00Z','realized_at':'2026-08-25T00:00:30Z'},{'discovered_at':'2026-08-25T00:00:00Z','realized_at':'2026-08-25T00:00:10Z'}]
assert m.evaluate(rows)==m.evaluate(list(reversed(rows)))
