from pathlib import Path
text=Path(__file__).parents[1].joinpath('ontology.ttl').read_text()
assert 'ocp:appendOnlyLedger true' in text,'REFUSED[MUTABLE_LEDGER]'
assert 'ocp:preservesPriorFacts true' in text,'REFUSED[HISTORY_ERASURE]'
