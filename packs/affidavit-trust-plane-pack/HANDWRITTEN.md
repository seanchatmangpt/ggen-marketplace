# HANDWRITTEN.md — affidavit-trust-plane-pack ledger

Pack law: every file of kind template/ontology/gate is ggen-produced by
definition (it renders or governs a projection of `ontology.ttl`). Therefore
the handwritten ledger for those files is structurally `n/a` — no hand-written
bytes exist in this pack. The single admitted exception is recorded as
`UNSUPPORTED(generator-capability)` per the admitted affidavit-pack Round-5
boundary: enumerable facts (struct fields, enum variants, parameter sets,
field orders, standings) live in `ontology.ttl`; algorithmic crypto bodies
are real code inside Tera templates.

| path | kind | standing | reason |
|---|---|---|---|
| pack.toml | manifest | n/a (ggen-produced by definition) | pack admission metadata; no template/ontology/gate bytes |
| ontology.ttl | ontology | n/a (ggen-produced by definition) | the source graph itself; everything below it is a projection |
| targets.toml | manifest | n/a (ggen-produced by definition) | language targets declaration |
| ggen.toml | manifest | n/a (ggen-produced by definition) | rule table binding queries/templates to outputs |
| package.toml | manifest | n/a (ggen-produced by definition) | named outputs for consumer packs |
| queries/*.rq (10) | query | n/a (ggen-produced by definition) | SELECT projections over ontology.ttl individuals |
| templates/*.rs.tmpl (10) | template | n/a (ggen-produced by definition) | render ontology facts; see UNSUPPORTED row for algorithmic bodies |
| gates/ | gate | n/a (ggen-produced by definition) | anti-vacuity gates over the rendered plane |
| generated/*.rs (10) | projection | n/a (ggen-produced by definition) | byte-output of `ggen sync`; never hand-edited |
| templates/*.rs.tmpl (algorithmic bodies: signing, verification, canonicalization logic) | template | UNSUPPORTED(generator-capability) | crypto algorithmic bodies are real code inside Tera templates per the admitted affidavit-pack Round-5 boundary: no ggen generator capability expresses algorithm bodies; enumerable facts remain in ontology.ttl, algorithms live in templates |
