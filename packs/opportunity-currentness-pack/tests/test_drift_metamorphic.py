import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'drift.py'; s=importlib.util.spec_from_file_location('d',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
a='1'*40; b='2'*40
before=m.evaluate({'qualified_head':a,'default_head':b,'contained_heads':[]})
after=m.evaluate({'qualified_head':a,'default_head':b,'contained_heads':[a]})
assert before['standing']=='PARTIAL_ALIVE'
assert after['standing']=='ALIVE'
assert after['state']=='CONTAINED_AFTER_DRIFT'
