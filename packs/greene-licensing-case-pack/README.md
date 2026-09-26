# greene-licensing-case-pack

A licensing proposal packet for the strategic-doctrine executable lab,
modeled as a canonical Semantic Case Study. The packet is a PROPOSAL_DRAFT
authored and signed by the user; no tool in this pack sends it anywhere.

```text
ontology/greene-case.ttl   case, 5 claims, evidence, digests, falsifiers,
                           5 non-claims, letter, rights table, demo steps
ontology/greene-deck.ttl   10 pres:Slide facts (pptx-presentation-pack)
ontology/cs-pres-bridge.ttl pres:Presentation, pres:Slide subClassOf cs:Projection
  -> gates 050 / 060 / 070 + semantic-case-study-pack gates 010-040
  -> ggen sync run (runners/render_packet.py)
  -> letter.md, rights-table.md, appendix.md, demo-spec.md
  -> deck.json + render.mjs via pptx-presentation-pack templates (ggen_igniter)
```

## Claims and evidence

Every claim has standing ALIVE_FIXTURE, evidence ceiling REPO_LOCAL_FIXTURE
and authority ceiling NONE. Claims C01-C04 are bound to the doctrine lab at
`seanchatmangpt/autofde-lab@d6becb595aedac4f18cab84f80bf5aa90e1a45e4`; the
digests (ledger tail, matrix, report, `report.json` and `ledger.jsonl`
sha256) were recomputed by running the lab there and reproduced byte for
byte by a second process. C05 is bound to the strategic-doctrine catalog
projection at `seanchatmangpt/ggen-marketplace@c0f27e5bed97b164ac267f86d8d9d989982319e8`.

## Gates

| Gate | Refuses |
|---|---|
| `050_no_endorsement_language` | any literal implying affiliation or backing by an author, publisher or rights holder |
| `060_no_quoted_source_text` | quoted-text predicates, blockquote markers, typographic quotes, long quoted spans |
| `070_letter_author_is_user` | a letter not signed by exactly one `glc:User`, not a PROPOSAL_DRAFT, or marked sent |

Each gate has an exact-stem pass and fail witness (`gate-court.toml`); the
runner is `runners/semantic_runner.py`.

## Imports

The packet imports semantic-case-study-pack, pptx-presentation-pack,
evidence-standing-pack and decision-optionality-pack. They are wired by
`runners/render_packet.py`, not as `pack.toml` `[dependencies]`:

- ggen refuses a `[dependencies]` entry unless the consumer also lists that
  pack in `[packs]` (FM-PACK-014);
- ggen refuses template-less packs as `[packs]` entries (FM-PACK-005):
  pptx-presentation-pack ships only `.eex` templates and
  decision-optionality-pack ships none;
- `scripts/qualify_packs.py` qualifies each pack in isolation and does not
  compose dependencies.

The runner lists semantic-case-study-pack in `[packs]`, imports the other
three at ontology level, and passes this pack's `ontology/` instance files
as `extra_ontologies` (ggen loads only a pack's root `ontology.ttl`).
`qualification.toml` unions the same instance files for isolated
qualification.

## Render

```bash
python3 packs/greene-licensing-case-pack/runners/render_packet.py --consumer /tmp/greene-render
```

## Tests

```bash
python3 -m pytest tests/test_greene_licensing_case_pack.py -q
```

## See also

- `packs/semantic-case-study-pack/` (cs: vocabulary, gates 010-040)
- `packs/pptx-presentation-pack/README.md` (deck manufacture)
- `packs/strategic-doctrine-pack/README.md` (the sd: catalog)
