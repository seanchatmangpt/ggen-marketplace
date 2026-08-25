import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'normalize.py'
s=importlib.util.spec_from_file_location('n',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
env={'repository':'o/r','head_sha':'1'*40,'kind':'run','payload':{'run_id':1}}
a=m.normalize(env);b=m.normalize(env)
assert a==b
assert a['exact_subject']=='o/r@'+'1'*40
assert a['actuation_performed'] is False
