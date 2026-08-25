from pathlib import Path
text=Path(__file__).parents[1].joinpath('composition.toml').read_text()
for pack in ['github-live-evidence-ingestion-pack','ggen-project-boundary-pack','github-controloutcome-observation-pack']:
    assert f'pack = "{pack}"' in text, f'REFUSED[MISSING_INPUT_PACK]:{pack}'
assert text.count('reversible = true')==3,'REFUSED[IRREVERSIBLE_OUTPUT]'
assert 'actuation_performed = false' in text,'REFUSED[COMPOSITION_DO_LEAK]'
