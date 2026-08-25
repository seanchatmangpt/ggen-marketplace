from pathlib import Path
import re
text='\n'.join(p.read_text() for p in Path(__file__).parents[1].joinpath('fixtures').glob('*.jsonl'))
subjects=re.findall(r'"exact_subject":"([^" ]+)"',text)
assert subjects and all(re.fullmatch(r'[^@]+@[0-9a-f]{40}',s) for s in subjects),'REFUSED[INEXACT_SUBJECT]'
