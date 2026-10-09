# SEAL-RECEIPT — backlog [81] Phase-4 attestation closure — v26.10.8

Sealed 2026-10-08 by lane `seal-harness` per `SEAL-RUNBOOK.md` §2–§5
(ccbf58273). Both seal surfaces executed over the full 78-row
`ADMISSION-LEDGER.jsonl` (50 admitted / 28 refused).

## Artifacts (this directory + seal/)

- `seal/build_drafts.py` — §2 adapter: ledger row -> SjCampaignDraft wire row.
- `seal/drafts.jsonl` — 78 drafts (byte-exact adapter output).
- `seal/<ORDER>.sj-record.json` ×78 — sealed `SjRecord` wire forms.
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
   /tmp/seal2/records < /tmp/seal2/drafts.jsonl` → **sealed 78 records**; each
   record re-verified in-process via `SjRecord::from_json(&json).verify()` —
   78/78 OK, zero refusals.
4. osx-clnr @78f3aea: temporary harness `examples/seal_campaign.rs` (untracked,
   removed after run): RReceipt JSONL (projected from the sealed records) →
   `from_r_receipt` → `seal_sj_record` → **osx-clnr sealed 78 records**.
5. Independent verification output: per-record `OK` with chain head, e.g.
   final record SJIRA-V8-004C, campaign chain head
   `76305b343d47889cdc9e9eb2a5f4d36150c811dc0d3864034c8218c56b108fca`.

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
  `<ORDER>@roundN` in drafts and records.
- The two `castle-goal` rows have `order: null`; drafted as
  `UNSCOPE-castle-goal-<ts>` (repo resolved to `/Users/sac/castle` per
  ADMISSION-CONTEXT.md), standing REFUSED, broken_term MuOnO.
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
