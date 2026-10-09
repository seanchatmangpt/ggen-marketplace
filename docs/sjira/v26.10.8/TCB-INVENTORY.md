# TCB Inventory — seL4 Doctrine, v26.10.8

Operationalization of
`docs/dissertation/HARDENING-AS-RADICAL-ARCHITECTURAL-SUBTRACTION.md`.
All footprints re-read from disk 2026-10-08. Subject SHAs: ggen
`5d209290c` (working tree; note: dispatch named `fcfd6349`, tree has since
moved — footprints measured against working tree at read time), ggen-marketplace
`2de3d52fe` (branch `hdit-v2-structs`), affidavit working tree.

## TCB rows

| # | Primitive | Real footprint | LOC |
|---|---|---|---|
| 1 | Graphlaw Datalog fixpoint + stratification | `/Users/sac/ggen/crates/praxis-graphlaw/src/datalog.rs` — `validate_rules` (`pub fn` at line 83, safety check at 104-118, empty-ruleset guard 92-98, Bellman-Ford-style relaxation with cycle check, `while changed && iteration <= num_predicates` at line 296); helpers `collect_formula_vars` (line 15), `relation_of` (line 62) | 325 |
| 2 | Type-3 wire parser (graphlaw transport surface) | `/Users/sac/ggen/crates/praxis-graphlaw/src/parser/mod.rs` — `parse_triples` (line 26), `parse_triple` (line 109), `parse` (line 147), `parse_rules` (line 216), `parse_n3_document` (line 225). **Honest deviation**: no crate named `ex4pm` exists under `~/ggen/crates/`; the only graphlaw transport parser is `praxis-graphlaw/src/parser/mod.rs`. The name "Type-3 wire DFA" does not appear verbatim in the source; the parser is a hand-rolled recursive-descent triple/rule parser (preprocess → tokenize-free line parsing), not a table-driven DFA. Footprint cited is the real parser that exists. | 347 |
| 3 | Affidavit verify path (BLAKE3 chain) | `/Users/sac/affidavit/src/sj_record.rs` — `SjRecord::verify` (line 576: document law → `rebuild_events` (579) → `recompute_chain` (583) → chain-head binding check (585-588) → `subject_digest` comparison (590-597)); `rebuild_events` (line 901); `from_json` re-verifies on deserialize (609-621). Chain law in `/Users/sac/affidavit/src/chain.rs` — `recompute_chain` (line 72), 367 LOC. | sj_record.rs: 982; chain.rs: 367 |
| 4 | ML-DSA (FIPS 204) verify — **honest correction**: not in `sj_record.rs`; lives in the PQC module | `/Users/sac/affidavit/src/crypto_trust_pqc.rs` — `ml_dsa65_verify` (line 120), `ml_dsa65_sign` (103), `ml_dsa65_from_seed` (88), `slh_dsa128s_verify` (192), `hybrid_verify` (246); module doc line 6: "ML-DSA-65 via `ml-dsa` (FIPS 204)". `sj_record.rs` verify path is BLAKE3-chain-only; zero ML-DSA references there (grep confirmed). | 581 |

## Mechanism-not-policy grep (Lesson 2 audit)

Kernel crates searched: `praxis-core`, `praxis-graphlaw`, `ggen-engine`,
`ggen-graph` (`src/` trees).

**Cloud/vendor policy terms** (`aws|gcp|google.cloud|iam|s3|dynamodb|azure|
stripe|kafka`, case-insensitive, tests filtered): **zero real hits.** All
raw matches are substring false positives: `aws` inside `laws`/`Laws`
(e.g. `ggen_law.rs:3` "every LawState ingestion passes through"; `datalog.rs:216`
"nixon_diamond corpus"), `s3` inside local variable names
(`receipt_validator.rs:106,120` `s1..s5` stage vars), `iam` as substring of
nothing beyond those. No AWS/GCP/Azure/IAM import, client, or configuration
exists in the kernel crates.

**`ledger` hits** (reported honestly, not suppressed): ~13 hits, all
`praxis-core/src/receipt_epoch.rs` + `receipt_validator.rs` — internal
"admission ledger" terminology (`AdmissionLedger` enum, line 347;
`derive_andon`, line 365). This is the fabric's own receipt-ledger vocabulary,
not a cloud ledger service integration. Verdict: **mechanism-not-policy
holds for the kernel crates** — the only domain vocabulary present is the
fabric's own admission law.

## Falsifiers

- Any footprint above failing to re-read at cited file:line falsifies the row.
- A real (non-substring) cloud/IAM hit in the kernel crates falsifies the
  mechanism-not-policy verdict.
- ggen `Cargo.toml`/`Cargo.lock` are dirty in the working tree (pre-existing,
  unrelated lanes); praxis-graphlaw has an untracked `ggen_law.rs` — footprints
  for `datalog.rs`/`parser/mod.rs` are unaffected (tracked, unmodified).
