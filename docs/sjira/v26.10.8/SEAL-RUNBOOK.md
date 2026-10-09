# SEAL-RUNBOOK — fleet workgraph ledger sealing via sj_record — v26.10.8

**Status**: grounded design; seal machinery ALIVE, adapter + harness are named
prerequisites (see §5). Companion to `ADMISSION-LEDGER.jsonl` (78 rows:
50 admitted / 28 refused across 12 repos), `WORKGRAPH.ttl`,
affidavit `docs/sjira/v26.10.8/SJ-ALIGNED-RECORD-DESIGN.md` (the spec of
record).

---

## 1. Seal machinery — witnessed standing

### 1.1 affidavit sj_record (spec of record)

`affidavit@810f896`, branch `feat/sj-aligned-record`, `src/sj_record.rs`:

- `SjCampaign::new(SjCampaignDraft) -> Result<SjCampaign, SjRefusal>` — the
  admission gate (16-key contract; `src/sj_record.rs:449`).
- `SjCampaign::finalize() -> Result<SjRecord, SjRefusal>` — assembles the
  BLAKE3 chain via `ChainAssembler::append/finalize`, builds the JCS
  document, mints the digest-bound identity (src/sj_record.rs:518).
- `SjRecord::verify()` — full re-verification: 16-key re-admission, event
  reconstruction equality, chain recompute, chain-head binding, digest
  re-derivation (src/sj_record.rs:576).
- `SjRecord::to_json/from_json` — wire form; `from_json` refuses a tampered
  base at deserialize (src/sj_record.rs:612).
- Chain events minted per `SjCampaign::chain_events()`: one `commit` event per
  campaign commit, one `court` event per replay command, one `residue` event
  (src/sj_record.rs:460).

Witnessed court this session: `cargo test --features crypto-trust --test
sj_record` → **11 passed; 0 failed** (tests/sj_record.rs, real collaborators,
no mocks).

### 1.2 osx-clnr seal_sj_record (alternate seam)

`osx-clnr@78f3aea`, `src/domain/affidavit_integration.rs:318`:

```text
seal_sj_record(&mut SjWorkOrderRecord, &Receipt) -> anyhow::Result<Receipt>
```

Seals an `SjWorkOrderRecord` (projected from an `RReceipt` via
`from_r_receipt`, `src/domain/sj_projection.rs:71`) into an extended chain as
a terminal `sj_work_order_sealed` event and closes the
`SjWorkOrderRecord::chain_hash` seam. Witnessed this session:
`cargo test --lib sj_projection` → **5 passed; 0 failed**.

### 1.3 No CLI seam exists

Grep evidence: zero hits for `sj_record`/`seal_sj_record` in affidavit
`src/cli.rs`, `src/registry.rs`, `src/verbs/`, `src/bin/`; zero hits in
osx-clnr `src/nouns/` and `src/main.rs`. Sealing today is library-only: both
paths require a small harness. The `oclnr receipt` noun only exercises
`build_deletion_affidavit`, not the sj seam.

## 2. Ledger → draft mapping (the adapter contract)

`ADMISSION-LEDGER.jsonl` rows are **O, not drafts**. The fields do not map
1:1 onto `SjCampaignDraft`; the gaps are the missing adapter.

| SjCampaignDraft field | source | gap |
|---|---|---|
| work_order_id | row.order | — direct |
| repo | row.repo | — direct |
| origin_ceiling / origin_grant / origin_actor | row.origin_authority IRI (27 rows carry it) | 51 rows lack it → default `None`/`NONE`/`coordinator:recorded` |
| provider_name / provider_execution_id | fixed `"sjira.v26108.admitter"` / row `admitted_via`+`ts` | derivable |
| identity.subject | row.order | — direct |
| identity.subject_sha (40-hex) | **missing** — rows carry `work_order_digest` (sha256 content digest), refused typed as `SjRefusal::BadSha` (src/sj_record.rs:318) | resolve per order from the landing repo's git log / landing-batch receipts |
| identity.base_sha (40-hex) | **missing** | parent of the landing commit |
| commits[] (7..40 hex) | **missing** | per-order landing commits; `BadCommitSha` gate refuses otherwise |
| residue_declaration | row.refusal_reason for refused rows; "28 refusals recorded, 50 admitted" summary for the campaign | derivable |
| files_changed | **missing** | from landing receipts / `git show --name-only` |
| replay_commands (minItems 1; real cmd/exit/cwd) | **missing** | the court/gate commands actually run per order — `EmptyReplay` refuses otherwise |
| standing | row.admitted → `ALIVE` / refused → `REFUSED` + `broken_term` (refusal_reason parsed to `BrokenTerm`) | mapping rule |
| derived_from | row.candidates / row.workgraph path | derivable |
| predecessor_work_order_ids | row.supersedes | direct where present |

Precedent for the refusal shape: ledger row `SJIRA-V8-002`,
`refusal_reason: {:invalid_sha, :base_sha, "20aadd175"}` → standing `REFUSED`,
`broken_term` = invalid base sha. (This is the same class of refusal
`SjRefusal::BadSha` enforces in code.)

## 3. Harness prerequisite (named, small)

A tiny Rust harness is required (library-only seal, §1.3). Spec:

```rust
// examples/seal_sj_record.rs (affidavit, feature crypto-trust)
// stdin: JSONL of SjCampaignDraft-shaped objects (§2 mapping applied)
// per line: SjCampaign::new(draft)? -> finalize()? -> to_json()?
//           println SjRecord::subject_digest_hex() + chain head
// stdout: record JSON per line; final line prints campaign chain head.
```

Write records to `docs/sjira/v26.10.8/seal/<ORDER>.sj-record.json`
(durable_location), and the whole-file chain head to
`docs/sjira/v26.10.8/seal/CHAIN-HEAD.txt`.

## 4. Seal run

```bash
# 0. Court gate (witnessed green at 810f896)
cd /Users/sac/affidavit && git checkout 810f896
cargo test --features crypto-trust --test sj_record   # expect: 11 passed

# 1. Build drafts: resolve per-order subject/base SHAs, commits,
#    files_changed, replay commands from landing receipts + git logs
#    (§2 mapping). Output: /tmp/seal/drafts.jsonl (78 rows, incl. REFUSED).

# 2. Seal
cargo run --features crypto-trust --example seal_sj_record \
  < /tmp/seal/drafts.jsonl \
  > /tmp/seal/records.jsonl

# 3. Persist + verify (independent re-verify path: from_json re-runs the
#    full verify() law)
#    for each record: SjRecord::from_json(bytes)?.verify()?  -> Ok
#    then commit docs/sjira/v26.10.8/seal/ and record CHAIN-HEAD.txt.
```

**Expected chain head**: not pre-computable (BLAKE3 chain over the full event
sequence incl. real commit SHAs and exit codes) — it is whatever
`finalize()` mints and `from_json().verify()` re-derives. The falsifier is
exactness, not a remembered value: any byte drift between seal and re-verify
refuses with `EventClaimMismatch`/`ChainTamper`.

## 5. Standing

| piece | standing | evidence |
|---|---|---|
| sj_record seal law | ALIVE | 11/11 court tests at 810f896, run this session |
| osx-clnr seal_sj_record seam | ALIVE | 5/5 sj_projection tests at 78f3aea, run this session |
| CLI seal surface | REFUSED (by absence) | zero registry/verb/noun hits (§1.3) |
| ledger→draft adapter | UNVERIFIED | mapping table §2 is designed, resolver not yet built |
| seal harness | UNVERIFIED | spec §3, not yet compiled |

BLOCKED-then-GO: the runbook is executable once §3's harness exists (~50
lines) and §2's SHA resolver runs; neither requires new law — only
`SjCampaignDraft` assembly from data already on disk.
