import importlib.util
from pathlib import Path
p=Path(__file__).parents[1]/'runtime'/'normalize.py'
s=importlib.util.spec_from_file_location('n',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
for env,expected in [
 ({'repository':'o/r','head_sha':'bad','kind':'run','payload':{}},'REFUSED[INEXACT_HEAD_SHA]'),
 ({'repository':'o/r','head_sha':'1'*40,'kind':'deploy','payload':{}},'REFUSED[UNSUPPORTED_EVIDENCE_KIND]')]:
 try: m.normalize(env); raise AssertionError('expected refusal')
 except ValueError as exc: assert str(exc)==expected
