import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'normalize.py'
s=importlib.util.spec_from_file_location('n',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
env={'payload':{'z':2,'a':1},'kind':'commit_status','head_sha':'2'*40,'repository':'o/r'}
first=m.canonical(m.normalize(env));second=m.canonical(m.normalize({'repository':'o/r','head_sha':'2'*40,'kind':'commit_status','payload':{'a':1,'z':2}}))
assert first==second
