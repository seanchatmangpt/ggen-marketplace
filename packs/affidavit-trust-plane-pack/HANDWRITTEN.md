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
| queries/*.rq (28) | query | n/a (ggen-produced by definition) | SELECT projections over ontology.ttl individuals |
| templates/*.rs.tmpl (28) | template | n/a (ggen-produced by definition) | render ontology facts; see UNSUPPORTED row for algorithmic bodies. 12 are bound by this pack's `ggen.toml` and rendered into `generated/`; the other 16 are not bound by this pack's `ggen.toml` (consumer-bound; not self-rendered here) |
| gates/ (13) | gate | n/a (ggen-produced by definition) | anti-vacuity gates over the rendered plane |
| generated/*.rs (12) | projection | n/a (ggen-produced by definition) | byte-output of `ggen sync run` in this pack (self-proof; the 12 `ggen.toml` rules); never hand-edited. Regenerate with `ggen sync run` from the pack directory |
| templates/*.rs.tmpl (algorithmic bodies: signing, verification, canonicalization logic) | template | UNSUPPORTED(generator-capability) | crypto algorithmic bodies are real code inside Tera templates per the admitted affidavit-pack Round-5 boundary: no ggen generator capability expresses algorithm bodies; enumerable facts remain in ontology.ttl, algorithms live in templates |

## Upstream provenance pin

- upstream: `/Users/sac/affidavit` branch `feat/advanced-witness-capability-set`
- commit: `3b2e4138313844fa85b14e4fbff51e734c4babad` (2026-10-05, clean HEAD)
- seam 1: `crypto_trust_verify::certify_signed(&SignatureEnvelope, &[u8], &str,
  &Es256SigningKey) -> Result<CryptoStandingReceipt, VerifyRefusal>`;
  feature-gated `crypto-trust` (lib.rs:167; method at
  src/crypto_trust_verify.rs:471)
- seam 2: `event_builder::EventBuilder` (ungated, src/lib.rs:118)
- role: OPTIONAL certified-receipts upgrade seam for paid-delivery receipts.
  The chain rule stays `paid-delivery-chain/v1` plain sha256 fold; this seam
  adds signatures, never replaces it.
- failure mode: fail-open-to-uncertified — missing seam or unsigned records
  still verify fold-only.
