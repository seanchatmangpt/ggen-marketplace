# HANDWRITTEN.md

Code in this pack that is not ontology, gate, template or generated projection. Every row is
`UNSUPPORTED(generator-capability)` with the reason no generator covers it. Vocabulary,
gates 070-097, the disposition rule and all twelve templates are pack capital, not residue.
Version 0.4.0 (release court, typed checks, root receipt) adds no code residue: the court script,
its import re-hash, probe and observation writer, the typed-checks list, IMPORTS.sha256 and both
receipts are rendered by ggen from graph facts, and the standing derivation is a template
`construct:`.

| path | standing | reason | owner |
|---|---|---|---|
| `lift/manifest_to_er.py` | UNSUPPORTED(generator-capability) | ggen renders RDF into text; it does not parse TOML into RDF. No marketplace pack lifts TOML to RDF: star-toml-pack generates Rust config structs, and the tomllib users in autofde-semantic-registry-pack and the xaas public-ontology profile are not RDF importers. 32 lines of stdlib tomllib, deterministic, lifted-observation output only. | this pack (manifest-import step) |
| `bin/run-gates.py` | UNSUPPORTED(generator-capability) | Reused from `packs/gym-autonomic-crown-pack/bin/run-gates.py` and extended to union the consumer's `ggen.toml` imports and apply the templates' `construct:` rules. It is the second, independent executor (rdflib next to ggen's own engine) of the same gates; ggen has no mode that runs a pack's gates outside a consumer sync. | this pack |
| `bin/import-crown-lift.py` | UNSUPPORTED(generator-capability) | ggen renders RDF into text; it does not parse receipt JSON into RDF. The lift is generic for any upstream stop-court crown (STOP receipt found by `identity.subject` `<checkpoint>/STOP`, gate receipts by `gate.checkpoint`, gate count from the court's own `N/M gates ALIVE`, paired field configurable) and its output is a pure function of the receipt bytes and the two bound SHAs. Prototype: the scan's 31-line lift_ttl.py; this is 66 lines of stdlib. | this pack (crown-import step) |
| `bin/import-crown-generate.sh` | UNSUPPORTED(generator-capability) | Orchestration only (lift, explicit runner, `ggen sync run`, byte comparison), following `packs/gym-autonomic-crown-pack/bin/crown-generate.sh`; ggen has no mode that lifts JSON, re-checks a committed lift and diffs a committed render in one command. Read-only on the consumer. | this pack |
| `qualification/fixtures/derive-fixtures.py` | UNSUPPORTED(generator-capability) | Provenance replay for the imported-crown fixtures: re-derives every fixture directory from real xaas git blobs (checked by object id) and records each qualification rewrite in the rewritten receipt itself. | this pack |
| `qualification/qualify.sh` | UNSUPPORTED(generator-capability) | Qualification harness (real ggen, real rdflib, real git repositories and the rendered court script in scratch copies; no mocks). The marketplace's `scripts/qualify_packs_r18.py` renders a pack once against `qualification/consumer.ttl` but has no mutant/expected-refusal contract. Step 7 (0.4.0) drives sync -> court -> sync, the typed-exit witnesses and `court-mutants.EXPECTED.tsv`. | this pack |

The fixture inputs under `qualification/` are byte copies or lifted observations of real sources,
not handwritten facts; `qualification/consumer-v26.9.23/SOURCES.md` records each source and sha256.
The imported-crown fixtures (`qualification/fixtures/*-receipts/`) are derived by
`derive-fixtures.py` from real xaas receipt blobs; every qualification rewrite (the positive
witness's STOP=true and ALIVE gates, and each one-change mutant) is recorded inside the
rewritten receipt's `qualification_rewrite` object and in `qualification/fixtures/SOURCES.md`.
The two fixture-only choices (the target release's role names and constitutional mappings in
`consumer-v26.9.23/release.ttl`) are qualification data, not v26.9.23 release decisions; so are
its 0.4.0 court facts (gates, probes, the typed check, imports, root receipt). Its `observed.ttl`
is the court's own output (`COURT_OBSERVED`), not hand-written; `qualify.sh` step 7 requires a
fresh court run to reproduce it (subject line excepted). `qualification/chatman-receipt.schema.json`
is a byte copy of chatman-ecosystem `schemas/receipt.schema.json` at c59596f5.
