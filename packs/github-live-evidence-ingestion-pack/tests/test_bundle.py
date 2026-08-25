import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'bundle.py'
s=importlib.util.spec_from_file_location('b',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
items=[{'exact_subject':'a/r@'+'1'*40,'evidence_kind':'run','receipt_digest':'a'*64},{'exact_subject':'b/r@'+'2'*40,'evidence_kind':'job','receipt_digest':'b'*64}]
out=m.bundle(items)
assert [x['count'] for x in out]==[1,1]
assert len({x['exact_subject'] for x in out})==2
