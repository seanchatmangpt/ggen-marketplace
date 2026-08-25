from pathlib import Path
text=Path(__file__).parents[1].joinpath('composition.toml').read_text()
assert 'source_pack = "github-live-evidence-ingestion-pack"' in text,'REFUSED[MISSING_SOURCE_PACK]'
assert 'target_pack = "github-controloutcome-observation-pack"' in text,'REFUSED[MISSING_TARGET_PACK]'
assert 'actuation_performed = false' in text,'REFUSED[COMPOSITION_DO_LEAK]'
assert text.count('reversible = true') >= 2,'REFUSED[IRREVERSIBLE_COMPOSITION_EDGE]'
