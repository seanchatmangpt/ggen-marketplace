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

## 6. Hub main-sync (R31)

Round-close rule: `origin/main` must be a strict ancestor of (or equal to)
`hdit-v2-structs` at round close; main absorbs the branch by fast-forward
only, per the v26.10.7 precedent (hand FFs a9b6a11a9, f7a32faaf). No merge
commits, no rebase, no force-push.

Check:

```sh
./scripts/check_main_sync.sh   # exit 0 = in sync; exit 1 = out of sync
```

Repair (fast-forward main to the branch tip, run only when the check
reports the branch ahead):

```sh
git push origin hdit-v2-structs:main
```

R31 witness: check ran at branch tip f7a32faaf with
`OK: origin/main == hdit-v2-structs (f7a32faaf)`, exit 0 — no repair due.

## Machine-wide CPU-fairness limiter for long audits (R41)

Witness/audit runs that spawn many doc-hdit processes must go through the
machine-wide semaphore in `scripts/run_fleet_courts.sh` (mkdir slots under
`/tmp/doc-hdit-semaphore`, default 4 concurrent, 5s poll, 30-minute
acquisition timeout, exit 99 on timeout; tunable via `DOC_HDIT_MAX_CONC`,
`DOC_HDIT_SEM_DIR`, `DOC_HDIT_SEM_TIMEOUT`). Witness probe (2026-10-09): 6
background stubs through the limiter — first 4 start together, remaining 2
start only after earlier slots release; max overlap 4.

Rules:

- Long audits (anything spawning doc-hdit fleets, e.g. witness/audit rounds)
  must run **nohup-detached**, never inline in an interactive session — the
  attempt-4 incident (2026-10-09) tied up the session for ~4.5h wall under
  24-37 concurrent processes at 100% CPU.
- Run long audits through the limiter entry point:

  ```sh
  nohup bash scripts/run_fleet_courts.sh > /tmp/fleet-courts.log 2>&1 &
  ```

- The limiter only gates entry; court semantics are unchanged (exit 0 iff
  all courts pass). Synthetic self-check: `bash scripts/run_fleet_courts.sh
  --probe-limiter`.

## Pin-stability law (R62)

The extractor (`scripts/gen_doc_surface.py`) commit and its
`PIN-ROTATION-LEDGER.md` current-row update are **atomic**: they land in
the SAME commit. Enforced by `scripts/check_pin_freshness.sh` (POSIX sh,
exit 0 iff the live extractor sha256 appears on the ledger's current row;
exit 1 with the repair message otherwise), wired as a fail-fast pre-step
in `scripts/run_fleet_courts.sh` before the semaphore/courts. The ledger
is the single pin authority — sibling receipts use the stable ledger
reference form, never an inline hash. Probe override: `PIN_LEDGER=<path>`.
Witnessed 2026-10-09: exit 0 on the live ledger (b88297e6 = current);
exit 1 via a doctored temp-copy ledger (real ledger untouched).

### Commit-hook guard (R81)

`bash scripts/install-pin-hook.sh` installs the same pin law as a pair of
git hooks in `.git/hooks/` (idempotent marker-delimited block; existing
hooks preserved, including the git-lfs post-commit). Because pre-commit
cannot see its own commit's ledger row, the guard DEFERS verification:

- `pre-commit`: staged diff touches `scripts/gen_doc_surface.py` → write
  `.git/PIN-CHECK-PENDING`, loud warning, exit 0 (never blocks);
- `post-commit`: if the marker exists, sha256 the COMMITTED extractor
  bytes (`git show HEAD:` piped through an archived temp copy) and require
  it on the committed ledger's current row. Pass → marker removed. Fail →
  LOUD violation banner, exit 1 (post-commit cannot roll the commit back;
  the exit makes the violation visible), marker KEPT until a follow-up
  ledger commit repairs it.

Hook law: an extractor commit may land, but a violation is unmissable and
persists until the ledger is repaired in an immediate follow-up commit.
Witnessed 2026-10-09 on `hdit-v2-structs` (scratch branches, real hooks):
clean rotation → `pin-freshness: OK ... found in ledger current row`,
marker removed; rotation-without-ledger → full PIN LAW VIOLATED banner,
marker kept.
