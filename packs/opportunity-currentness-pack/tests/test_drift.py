import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'drift.py'; s=importlib.util.spec_from_file_location('d',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
a='1'*40; b='2'*40
assert m.evaluate({'qualified_head':a,'default_head':a,'contained_heads':[]})['state']=='CURRENT'
assert m.evaluate({'qualified_head':a,'default_head':b,'contained_heads':[a]})['state']=='CONTAINED_AFTER_DRIFT'
assert m.evaluate({'qualified_head':a,'default_head':b,'contained_heads':[]})['standing']=='PARTIAL_ALIVE'
