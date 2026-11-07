# pack-scaffold-generator

Ontology-backed generator for conforming NEW ggen marketplace packs. Lane C4
(CONSTRUCT, new files only).

## Structure actually required of a pack (extracted from scaffolds/pack-skeleton,
CLAUDE.md, and sa2a-chicago-court-pack / a2a-conformance-pack /
ash-extension-starter-pack)

- `pack.toml`: `[pack]` name (kebab-case), SemVer, non-empty description;
  `[capabilities]` provides urn.
- Turtle at pack root or under `ontology/` (marketplace Turtle check).
- Packaging profile derived: project (`ggen.toml`), projection (`templates/`),
  semantic (neither) -- a profile is not a maturity level.
- Gates: `.rq`/`.py`/`.sh` under `gates/`; witness courts under
  `gate-court.toml` require exact-stem pass/fail witnesses per gate
  (scripts/check_gate_witness_courts.py).
- Receipt discipline: standing vocabulary, born UNVERIFIED
  (receipt-standing-law).

## Use

Declare one individual in the consuming graph:

```turtle
@prefix psg: <https://seanchatmangpt.github.io/packs/pack-scaffold-generator#> .

psg:my-pack a psg:PackScaffold ;
    psg:packName "my-pack" ;
    psg:packIri "https://seanchatmangpt.github.io/packs/my-pack#" ;
    psg:packProfile "semantic" ;
    psg:packDescription "..." ;
    psg:capabilityUrn "urn:ggen:pack:my-pack" .
```

Then run the templates (see qualification/falsifier.py for the exact consumer
ggen.toml shape: `[packs] path` + `[ontology] source` + `[templates] dir`).

## Gates (this pack)

- `gates/010_scaffold_spec_complete.rq` -- every PackScaffold carries all five
  required properties; witnesses pass/fail share its stem.
- `gates/020_pack_name_kebab.rq` -- packName kebab-case law; witnesses pass/fail.

## Falsifier (executed)

`python3 packs/pack-scaffold-generator/qualification/falsifier.py` builds
tmp/c4-demo, renders a scratch pack with the real `ggen sync run` twice
(determinism), asserts 8 non-empty scaffold files, parses the generated
Turtle, proves the generated identity gate flips (0 pass rows / >=1 fail
rows), checks `Standing: UNVERIFIED` in RECEIPT.md, and runs the repo stem
court over the generated pack. Exit 0 = PASS.
