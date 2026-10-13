# SEAL-RECEIPT — backlog [81] Phase-4 attestation closure — v26.10.8

Sealed 2026-10-08 by lane `seal-harness` per `SEAL-RUNBOOK.md` §2–§5
(ccbf58273). Both seal surfaces executed over the full 78-row
`ADMISSION-LEDGER.jsonl` (50 admitted / 28 refused).

**R60 refresh (2026-10-09)**: 5 records appended for the R-wave ACCEPTED
doc-hdit certify lands (RCERT-EX4PM-26108, RCERT-FROZEN-DUCKDB-26108,
RCERT-CASTLE-26108, RCERT-ASHGRAPHLAW-26108, RCERT-ASHSURF-26108) — see
"R60 seal refresh" below; 5 linkage-addendum records appended for the same
five RCERTs per the V18 review — see "R88 chain-head linkage addendum" below.
Records: **88**. Campaign chain head:
`fe05e4a3bec2930ccb730f1e98549c2e0f9bec7fea6208058cf1bfc0d506f4f3`
(prior head `d0265c9bbdc141ac8cad21cd736c96ecf1c9d351721f133f239de250d6137508`
preserved as the RCERT-ASHSURF-26108 record head).

## Artifacts (this directory + seal/)

- `seal/build_drafts.py` — §2 adapter: ledger row -> SjCampaignDraft wire row.
- `seal/drafts.jsonl` — 78 drafts (byte-exact adapter output) + 5 R60
  refresh rows = 83 total.
- `seal/<ORDER>.sj-record.json` ×83 — sealed `SjRecord` wire forms (78
  original + 5 R60 refresh).
- `seal/CHAIN-HEAD.txt` — per-record chain heads, campaign order.
- `seal/standing-table.tsv` — order / standing / broken_term / subject_sha /
  chain head / osx-clnr seal head, all 78 rows.
- `seal/OSXCLNR-SEAL-HEADS.txt` — osx-clnr `seal_sj_record` extension chain
  heads (one per record).
- affidavit lane: `examples/seal_sj_record.rs` (§3 harness).

## Executed chain (all commands real, this session)

1. Court gate: `cargo test --features crypto-trust --test sj_record`
   (affidavit, at 6110e1b containing 810f896) → **11 passed; 0 failed**.
2. Adapter: `python3 docs/sjira/v19.../seal/build_drafts.py` → 78 drafts,
   50 ALIVE / 28 REFUSED (matches ledger exactly).
3. Harness: `cargo run --features crypto-trust --example seal_sj_record --
   /tmp/seal4/records < /tmp/seal4/drafts.jsonl` → **sealed 78 records**; each
   record re-verified in-process via `SjRecord::from_json(&json).verify()` —
   78/78 OK, zero refusals.
4. osx-clnr @78f3aea: temporary harness `examples/seal_campaign.rs` (untracked,
   removed after run): RReceipt JSONL (projected from the sealed records) →
   `from_r_receipt` → `seal_sj_record` → **osx-clnr sealed 78 records**.
5. Independent verification output: per-record `OK` with chain head, e.g.
   final record SJIRA-V8-004C, campaign chain head
   `76305b343d47889cdc9e9eb2a5f4d36150c811dc0d3864034c8218c56b108fca`.
   Determinism: a full second seal run was byte-identical
   (`diff -r` over 78 records + CHAIN-HEAD.txt).

## Resolution law (adapter §2 mapping, disclosed per draft)

- `subject_sha` = last `sj:landedCommit` per order in the repo's
  `docs/sjira/v26.10.8*/WORKGRAPH.ttl`, git-verified via
  `git rev-parse --verify <sha>^{commit}` in `/Users/sac/<repo>`; fallback
  repo HEAD where no workgraph entry exists (refused rows without one).
- `base_sha` = `sj:baseSha` (git-verified) else parent of subject_sha.
- `files_changed` = union of `git show --name-only` over the resolved commits.
- `replay_commands` = the real admitter command that produced the row
  (`scripts/admit_workgraphs.py`, or the row's receipted `admitted_via`), with
  the receipted exit 0 (cited in `derived_from`; not re-executed in this lane).
- standing: admitted → ALIVE; refused → `REFUSED(<refusal_reason>)` +
  broken_term by class: invalid_sha / base_sha / invalid_repository →
  `RMissingIdentity`; no_workgraph / unsupported_projection_type → `MuOnO`;
  missing acceptance → `RMissingStanding` (11 / 7 / 10 rows).

## Disclosures

- Round-2/3 rows repeat some order ids; later occurrences are row-unique as
  `<ORDER>@roundN` in drafts and records. The two `order: null` rows draft as
  `UNSCOPE-castle-goal-<ts>` / `UNSCOPE-castle-goal-<ts>@round2` (repo
  resolved to `/Users/sac/castle` per ADMISSION-CONTEXT.md), standing
  REFUSED, broken_term MuOnO.
- replay exit codes are receipted values from the admission runs
  (SEMANTIC-WAVE-RECEIPT.md / CONVERGENCE.md), not re-executed in this lane.

## Standing

| piece | standing | evidence |
|---|---|---|
| sj_record seal law | ALIVE | 11/11 court tests, this session |
| ledger→draft adapter | ALIVE | 78/78 rows drafted, census 50/28 exact |
| seal harness | ALIVE | 78/78 sealed + from_json().verify() OK |
| osx-clnr seal_sj_record | ALIVE | 78/78 extension-sealed |
| CLI seal surface | REFUSED (by absence) | unchanged (runbook §1.3) |

## R60 seal refresh (2026-10-09, lane R60)

Appended 5 records for the R-wave ACCEPTED doc-hdit certify lands that
postdate the original 78-row seal. Scope note: zcode-cli `a649d43` is a
FAIL-honest landing (not ACCEPTED) and bcinr's certify is
`REFUSED:DOC_HDIT_CERTIFY` — both excluded per the ACCEPTED-only rule; the
ex4pm row is the re-certify `d52fb4d` (ACCEPTED at 17e2831).

### Records added (each cites its on-disk receipt, git-verified this session)

| record | repo | subject (certify landing commit) | receipt cited | record chain head |
|---|---|---|---|---|
| RCERT-EX4PM-26108 | ex4pm | `d52fb4d2c6b87848a3efdcc4defb70a081b9d219` | `docs/sjira/v26.10.8/CERTIFY-VERIFY.md` | `a9066b1e63fe2c44d4ea048c4d0ee82ada3dfabb6e55bcd003a816a9a0c998f7` |
| RCERT-FROZEN-DUCKDB-26108 | frozen-duckdb | `7063b9d4d726d9c03cfec3e98c2962c77ed25655` | `docs/sjira/v26.10.8/DOC-HDIT-CERTIFY-RECEIPT.md` | `6dbe9a0d95520e56ed7d6cd01e283d2e4650aa53a7d6dfa349614d2c00886d0b` |
| RCERT-CASTLE-26108 | castle | `d6f136c78cab68e4859cf8d4dbc4245e29400116` | `docs/sjira/v26.10.8/CAMPAIGN-RECEIPT.md` + `doc-hdit.receipts.jsonl` | `bffc004718905957c8de99a8b586f63137f532a963b2b06a5d5286a43966b1b4` |
| RCERT-ASHGRAPHLAW-26108 | ash_graphlaw | `949eae9a7780ae253f0aa7defc0be2d6897fd589` | `docs/sjira/v26.10.8/CERTIFY-VERIFY.md` | `274d82d08d6d2fd0024cbbca881e2def9eb4e41af3efabd4f50f15b21f86a1b8` |
| RCERT-ASHSURF-26108 | ash_surface | `75706045028584d22a3e1ac0f9babc65713c0017` | `doc-hdit-certify-meta.json` + `doc-hdit.receipts.jsonl` | `d0265c9bbdc141ac8cad21cd736c96ecf1c9d351721f133f239de250d6137508` |

### Executed (all real, this session)

1. Court gate: `cargo test --features crypto-trust --test sj_record`
   (affidavit @ `ceb33d4`) → **12 passed; 0 failed** (runbook witnessed 11 at
   810f896; one test added since, zero failures).
2. Drafts: 5 rows appended to `seal/drafts.jsonl` (83 total). subject/base
   SHAs resolved by `git rev-parse` in each owning canonical checkout;
   files_changed from `git show --name-only`.
3. Seal: `cargo run --features crypto-trust --example seal_sj_record --
   /tmp/seal-r60/records < /tmp/seal-r60/drafts.jsonl` → **sealed 5 records**,
   each re-verified in-process via `SjRecord::from_json(&json).verify()` —
   5/5 OK, zero refusals. Records copied to `seal/`; heads appended to
   `seal/CHAIN-HEAD.txt` and `seal/standing-table.tsv` (append-only; prior
   78 rows byte-unchanged → chain continuity preserved).
4. osx-clnr extension seal (§1.2 seam): **NOT re-run this refresh** — the
   osx-clnr `seal_sj_record` extension pass over the 78 original records has
   no reproducing harness on disk (temporary `examples/seal_campaign.rs` was
   removed after the original run). The 5 new rows carry `-` in the
   `osxclnr_seal_head` column of `standing-table.tsv`. Typed as
   UNSUPPORTED(osx-clnr-extension-harness-removed), not silently skipped.

### Chain continuity

Parent of the refresh = prior campaign chain head
`76305b343d47889cdc9e9eb2a5f4d36150c811dc0d3864034c8218c56b108fca`
(SJIRA-V8-004C, record 78). New records appended in campaign order
(EX4PM → FROZEN-DUCKDB → CASTLE → ASHGRAPHLAW → ASHSURF); CHAIN-HEAD.txt is
append-only, 78 → 83 lines; new campaign chain head
`d0265c9bbdc141ac8cad21cd736c96ecf1c9d351721f133f239de250d6137508`
(RCERT-ASHSURF-26108).

## R88 chain-head linkage addendum (2026-10-09, lane R88)

V18 review found 0/5 RCERT records carry the owning repos' doc-hdit BLAKE3
chain heads. The runbook specifies no amendment record type, so this refresh
follows the R60 pattern: 5 `@chainlink` records appended to `seal/drafts.jsonl`,
sealed via `cargo run --features crypto-trust --example seal_sj_record`
(affidavit) — **sealed 5 records, 5/5 from_json().verify() OK, zero refusals**;
heads appended to `seal/CHAIN-HEAD.txt` and `seal/standing-table.tsv`
(append-only; prior 83 rows byte-unchanged). osx-clnr extension seal: `-`
(UNSUPPORTED(osx-clnr-extension-harness-removed), same as R60).

Each row adds `repo_chain_head` + `repo_chain_file`, verified this session by
python3 JSONL re-parse of the owning repo's chain file (real hashes, verdict
ACCEPTED; replay command executed exit 0 per row):

| record | repo | repo_chain_file | repo_chain_head | sealed record head |
|---|---|---|---|---|
| RCERT-EX4PM-26108@chainlink | ex4pm | `docs/sjira/v26.10.8/ex4pm.chain.jsonl` (secondary `ex4pm.chain.17e2831.jsonl`: `29e4c748dff0577753a3c7a03787fb17e49ef855fb1f1667f25e1593d3980bab`) | `0f44312119cf7dab27119687e6767b5370d8e7775850cf8e111298d0f63396c8` | `e4afa872f965b8290c07cede04afbff76dcb402ac29cc147e6a7188a425d05f3` |
| RCERT-FROZEN-DUCKDB-26108@chainlink | frozen-duckdb | `docs/sjira/v26.10.8/doc-hdit.receipts.jsonl` (durable doc `DOC-HDIT-CERTIFY-RECEIPT.md`) | `b19213a2e05b6e427a041c78b5068bddead9dee1efb1db7a47aeb2d394f55c20` | `15c6ffeb55df57dcf54b0157398ce6445238825032c5f505f5b462a9f431e5e1` |
| RCERT-CASTLE-26108@chainlink | castle | `docs/sjira/v26.10.8/doc-hdit.receipts.jsonl` | `6935d9c9cefdab9c88f24c08d37314270eefa48d8c5de23351215a2baee37d9a` | `b4acffb7e637c9ee7f7909434d68748079b716862db0e6dd105661f5fc8e12b7` |
| RCERT-ASHGRAPHLAW-26108@chainlink | ash_graphlaw | `docs/sjira/v26.10.8/ash_graphlaw.chain.jsonl` | `e95eb2f067812557a8281cf240b6649a99317c96d80f5d41ff7a56bf1ccec0bc` | `85ffd423cb0eb0ac8334dee4c2853e31ae35a279012ca3494a1733ff00fe5b1c` |
| RCERT-ASHSURF-26108@chainlink | ash_surface | `docs/sjira/v26.10.8/doc-hdit.receipts.jsonl` | `488a29bf638068d7b0bbb9a2b9336c82d1ba013f4ccb75b6c2279fcff3d5db9e` | `fe05e4a3bec2930ccb730f1e98549c2e0f9bec7fea6208058cf1bfc0d506f4f3` |

Subject/base SHAs per row are the owning-repo commit that last touched the
chain file and its parent, resolved by `git log`/`git rev-parse` in the owning
canonical checkout. Chain continuity: parent of the addendum = R60 head
`d0265c9bbdc141ac8cad21cd736c96ecf1c9d351721f133f239de250d6137508`; records
appended in campaign order (EX4PM → FROZEN-DUCKDB → CASTLE → ASHGRAPHLAW →
ASHSURF); CHAIN-HEAD.txt 83 → 88 lines; new campaign chain head
`fe05e4a3bec2930ccb730f1e98549c2e0f9bec7fea6208058cf1bfc0d506f4f3`
(RCERT-ASHSURF-26108@chainlink).
