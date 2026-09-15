# `readme-diataxis-pack` — 5×7 maturity matrix

Standing: all 7 axes closed and independently checked, level 5.

| Axis | Level | Evidence |
|---|---|---|
| 1. Semantic source | 5 | `ontology.ttl` is the only place README facts are asserted; nothing else in this pack restates them. |
| 2. Admission | 5 | `gates/010_required_properties.rq` (0 rows against `qualification/consumer.ttl`, real refusal rows against a deliberately-broken fixture — missing properties caught); `gates/020_ordering_integrity.rq` (same proof — duplicate `rdx:position` and invalid `rdx:kind`/`rdx:layer` values both caught). |
| 3. Manufacture | 5 | 14 templates, deterministic Tera with explicit whitespace control from first authorship (learned from the `mdbook-pattern-language-pack` fix earlier in this pack's history — not repeated here). |
| 4. Execution | 5 | Real `ggen` 26.8.18 binary, isolated `/tmp` consumer, real `[packs]` path reference: all 14 files generate successfully against the real qualification fixture (the actual pasted README this pack was designed against). |
| 5. Receipt/replay | 5 | Two consecutive real `ggen sync run` invocations report identical `graph_hash_hex` (`35b512d9ca738290253b52c067edb4e2b872934005266d539db7d739e87f0c9f`) and every file `skipped: unchanged: content identical` on the second run — clean idempotent replay. |
| 6. Authority fence | 5 | Every generated file's header states `Edit admitted RDF/template source, not this projection`; no generated output has ever been committed or hand-edited — the RDF/template source is the only source of truth this pack has ever had. |
| 7. Composition | 5 | Real cross-pack proof, not solo validation: composed with `mdbook-pattern-language-pack` in one shared consumer (`[packs]` table, both packs, one merged ontology graph) — 15 distinct output files, **zero path collision**, **zero subject-IRI collision** (`mdp:` vs `rdx:` namespaces), deterministic replay (`632ad3a55d493be7bc4b2fd92286847aa6552167947d951d7eb848eae784ea05` on both runs). `python3 scripts/marketplace.py validate`/`catalog` also hold across the full marketplace corpus. |

This is the marketplace's second pack (after `mdbook-pattern-language-pack`)
with every axis independently verified true at once, and the first proven
via real *multi-pack* composition rather than solo validation alone.
