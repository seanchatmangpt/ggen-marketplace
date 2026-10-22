# industry-pharma-21cfr

21 CFR Part 11 / EU Annex 11 electronic-records compliance pack (pharmaceuticals
and life sciences). Audit-trail semantics are **PROV-O** (W3C PROVENANCE-O,
`https://www.w3.org/ns/prov-o#`): attribution, generation and time intervals
carry who/what/when. A minimal `p11:` vocabulary adds only the Part 11 faces
PROV-O does not name: **why**, e-signature bound to a `prov:Agent`, the
deviation/CAPA quality loop, and WORM immutability.

## What it carries

- `ontology.ttl`: the vocabulary (ElectronicRecord, BatchRecord, ESignature,
  AuditTrail, Deviation, CAPA, RecordMutation, WormStore/OpenStore,
  QualityValidationStep, QualityPolicyFlag), each class annotated with
  `p11:requiresProperty`, plus one fully compliant batch-record individual
  chain (batch-101) so the gates are zero-rows over the pack graph.
- `templates/electronic-record-shacl.ttl.tmpl`: renders SHACL from the
  ontology's own `requiresProperty` annotations — an electronic record MUST
  have attribution + signature + audit trail + timestamp, a deviation MUST
  have a CAPA.
- `templates/client-walkthrough.md.tmpl`: browser-console walkthrough over the
  smalt substrate faces: Blob WORM record commit (immutability policy = Part 11
  retention, `lib/smalt/egress_router.ex:1313/1563/2282`), the attestation face
  for the signing host (`POST /attest/:type`, `AttestRoutes.ex:17`), the
  AppConfig quality-policy gate (`appconfig_features.ex:100`), and KV PS256
  e-signatures (`kv_pss.ex:1-8`).
- `gates/` — eight refusal gates, each witnessed both ways (the four 21 CFR Part
  11 gates plus the IND-3 pillar gates 050/060/070/080 — see `RECEIPT.md` and
  the consumer's `PILLARS.md`):
  | gate | refusal |
  |---|---|
  | `010_signature_missing.rq` | record without an e-signature bound to a `prov:Agent` |
  | `020_audit_trail_missing.rq` | record without a trail, trail missing who/what/when/why, or trail missing `prov:endedAtTime` |
  | `030_capa_missing.rq` | deviation without a linked CAPA with an action |
  | `040_mutation_non_worm.rq` | record mutation written through a non-WORM store |
  | `050_journal_scope_missing.rq` (P1) | batch record without an isolated per-batch storage scope / `journalPath` |
  | `060_esig_attestation_missing.rq` (P2) | e-signature without a `sha256:` SKR attestation measurement fingerprint |
  | `070_ai_annotation_unadjudicated.rq` (P3) | AI-derived quality annotation mutating a record with no `JudgeActivity` verdict |
  | `080_merkle_seal_missing.rq` (P5) | completed batch record without a `MerkleSeal` (sealed `sha256:` root + 320-byte receipt digest) |

## Qualification

```bash
python3 scripts/marketplace.py validate
python3 packs/industry-pharma-21cfr/qualification/verify.py
```

`qualification/verify.py` is a Chicago verifier: real rdflib, real gates,
asserts final state — pack graph clean, every PASS witness clean across all
gates, every FAIL witness flips exactly its own gate and zero others
(exactly-one-law; a court that cannot flip is the failure). The
`gate-court.toml` runner is the dflss-exemplar semantic runner
(`runners/semantic_runner.py`, exit 0 observed / 2 REFUSED / 3 structural).

## Consumer

`~/ggen/examples/industry/pharma-21cfr/` consumes the pack: it vendors
`pack-vocabulary.ttl` (a copy of the pack's `ontology.ttl`, the pack pin) and a
copy of the pack templates (ggen refuses absolute/traversal template paths, so
the consumer owns a real `templates/` dir), plus its own `data.ttl`
individuals.

```bash
cd ~/ggen/examples/industry/pharma-21cfr && ggen sync run
```

Generates `generated/pharma-21cfr-shacl.ttl` (valid Turtle, 91 triples) and
`generated/pharma-21cfr-walkthrough.md`; two consecutive syncs are
byte-identical (BLAKE3 receipt in `.ggen-v2/receipt.json`).

## Evidence boundary

Marketplace admission and rdflib court qualification only. No execution
authority; the walkthrough names real substrate routes but executes nothing.
