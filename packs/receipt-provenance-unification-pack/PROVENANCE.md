# PROVENANCE — receipt-provenance-unification-pack

## Authority boundary

This pack carries **no runtime actuation authority**. It generates exactly two
artifacts:

1. `generated/unified_receipt_validator.py` — a *pure predicate* over JSON
   documents. It opens a file read-only, returns a verdict, and exits. It
   writes nothing, mutates no git state, and admits nothing.
2. `generated/receipt_contract_matrix.json` — data (a census).

Consequential DO — writing a receipt, admitting an actuation, moving a gitlink,
publishing a release — stays behind GymAct/BRCE admission and is out of scope
here. `gates/01_no_actuation.rq` refuses any individual in this ontology that
claims actuation authority.

## Where every fact came from

Every `rp:ReceiptContract`, `rp:ValueForm`, `rp:FieldBinding` and
`rp:Validator` individual in `ontology.ttl` carries `rp:sourceFile` (and
`rp:sourceLine` where line-anchored) naming the real file on disk it was
transcribed from. Nothing here was inferred from a repo name or a field name.
The five contracts were read in full before transcription:

| Contract | Read from |
|---|---|
| `ecosystem_sync` | `vendor/ggen-ecosystem/docs/RECEIPT-SCHEMA.md` + `scripts/verify-receipt.sh` |
| `ecosystem_bootstrap` | `vendor/ggen-ecosystem/receipts/bootstrap-ggen-ecosystem-sync.json` |
| `gym_autonomic_crown` | `artifacts/autonomic-crown.json` + `scripts/crown-submodules.py` |
| `autofde_ledger` | `vendor/autofde-lab/src/autofde_lab/receipts/receipt.schema.json` + `receipt_store.py` |
| `clean_session` | `vendor/autofde-lab/schemas/chatman-clean-session-receipt.schema.json` |

## Published vocabularies reused

`prov:` (Entity/Activity/SoftwareAgent/used), `dcterms:` (title/source),
`dcat:Dataset`, `skos:` (Concept/prefLabel), `dqv:` (QualityAnnotation,
inDimension dqv:Consistency). Only `rp:` terms with no public equivalent are
minted — `rp:dottedPath`, `rp:valueForm`, `rp:reasonDelimiter`,
`rp:contractKey`.

## What is NOT claimed

- The generated validator reaches **exit-code parity with the real
  `verify-receipt.sh` on the 4 fixtures exercised**, not "on all inputs".
  `verify-receipt.sh`'s forward-compatibility clause (unknown fields permitted)
  is preserved; its exact stderr *wording* is not reproduced.
- `receipt_store.verify_chain`'s BLAKE3/sha256 **chain-link re-derivation is
  not subsumed** by this pack. Chain verification is an algorithm over an
  ordered ledger, not a field-shape predicate; only `autofde_ledger`'s field
  shapes are covered here. `verify_chain` remains authoritative for the chain.
- No existing pack, script, schema, or receipt was modified. This pack is
  additive; adopting it in any repo is a separate, human-gated decision.
