import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'lineage.py'
s=importlib.util.spec_from_file_location('l',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
items=[{'exact_subject':'o/r@'+'1'*40,'evidence_kind':'run','receipt_digest':'a'*64},{'exact_subject':'o/r@'+'1'*40,'evidence_kind':'job','receipt_digest':'b'*64}]
edges=m.lineage(items)
assert len(edges)==1 and edges[0]['relation']=='same-exact-subject'
