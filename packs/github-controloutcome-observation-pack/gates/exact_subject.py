from pathlib import Path
import re
text = Path(__file__).parents[1].joinpath('ontology.ttl').read_text()
subjects = re.findall(r'gco:exactSubject "([^"]+)"', text)
assert subjects and all(re.fullmatch(r'[^@]+@[0-9a-f]{40}', s) for s in subjects), 'REFUSED[INEXACT_SUBJECT]'
