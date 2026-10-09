# Refusal Triage Round 1 — ADMISSION-LEDGER.jsonl (v26.10.8)

Triage of all 28 refused rows in `ADMISSION-LEDGER.jsonl` (78 rows, 50 admitted).

## Method

Every refused row was classified by its typed refusal, then each re-admission
claimed by a later ledger row was **replay-verified**: the real admitter was
re-run in this session on the exact candidates file the ledger row cites, and
its output digests compared byte-for-byte against the ledger's
`work_order_digest` values. No ledger row was hand-edited; the ledger is
append-only and was not modified this round (see Ledger consistency).

Gate command (all runs, cwd `/Users/sac/ggen_igniter`,
`MIX_BUILD_ROOT=_build-lanecourt`):

    mix semantic_jira.admit_candidates --candidates <candidates file>

## Admitter replay receipts (exit 0, summary line cited per file)

| candidates file | result | digest match vs ledger |
|---|---|---|
| ggen-marketplace `candidates.jsonl` | admitted=4 refused=0, exit 0 | V8-002/003/005/006: byte-match |
| ggen-marketplace `candidates-v2.jsonl` | admitted=3 refused=0, exit 0 | V8-004A/B/C: byte-match |
| ash_a2a `candidates.jsonl` | admitted=4 refused=0, exit 0 | G1-TCK, G2-W608, G3-SelfCard, G4-ReleaseBump: byte-match |
| ash_pplan `v26.10.8-1/candidates.jsonl` | admitted=5 refused=0, exit 0 | DOCS-* x3, VENDOR-REPIN, VERSION-FIXFORWARD: byte-match |
| ex4pm `candidates.jsonl` | admitted=5 refused=0, exit 0 | wo-archive-cleanup, wo-boundary-law-doc, wo-campaign-receipt, wo-family-xrefs, wo-version-bump: byte-match |
| beam4pm `candidates.jsonl` | admitted=5 refused=0, exit 0 | residue-vendor-submodule, wo-diataxis-expansion, wo-erc-batch-c, wo-family-xrefs, wo-regen-wave: byte-match |
| ash_surface `candidates.jsonl` | admitted=1 refused=0, exit 0 | ASHSURF-26108-2: byte-match |

All 27 re-admission rows (24 round-2, 3 round-3 split orders) carry the same
`origin_digest` (sha256:310e14f1e30a...c72c) as the fresh runs; 22 replayed
verdicts byte-match the ledger digests; the beam4pm five were
mis-attributed to `repo: ex4pm` in an earlier reading and were re-verified
against `/Users/sac/beam4pm/docs/sjira/v26.10.8/candidates.jsonl`.

## Classification (28 refusal rows)

### Class A — `{:invalid_sha, :base_sha, <9-char>}` (5 rows)

Orders: SJIRA-V8-002, V8-003, V8-005, V8-006, ASHSURF-26108-2.
Root cause: mechanically-fixable extraction truncation (9-char SHAs authored
in an earlier workgraph revision). `valid_sha?/1` requires 40 hex chars
(`lib/ggen_igniter/semantic_jira.ex:1387`).

Outcome: RE-ADMITTED. Current WORKGRAPH.ttl / candidates files carry full
40-char SHAs; each order has a later round-2 admitted row whose
`work_order_digest` was replay-verified above.

### Class B — `{:invalid_repository, cross-repo ...}` (2 rows, SJIRA-V8-004)

Genuine structural refusal: a single candidate naming multiple repositories
fails `@repo` (`owner/name`) regex
(`lib/ggen_igniter/semantic_jira.ex:1379`). Not mechanically fixable in one
candidate — correctly resolved by splitting into per-repo orders
SJIRA-V8-004A/B/C (candidates-v2.jsonl), all three replay-verified admitted.
The V8-004 refusal rows stand as historical record, superseded by the split.

### Class C — `{:missing_required_field, "base_sha"}` (4 rows)

Orders: G1-TCK, G2-W608, G3-SelfCard, G4-ReleaseBump (ash_a2a).
Root cause: mechanically-fixable extraction gap (candidates built without
`base_sha` populated). Rebuilt candidates at
`/Users/sac/ash_a2a/docs/sjira/v26.10.8/candidates.jsonl` admit; digests
byte-match ledger rows 53-56.

### Class D — `{:unsupported_projection_type, "workgraph"}` (5 rows)

Orders: DOCS-DIATAXIS-WIRING, DOCS-PINNING-REF, DOCS-SCAFFOLD-SKELETONS,
VENDOR-REPIN-V26108, VERSION-FIXFORWARD-26108-1 (ash_pplan v26.10.8-1).
Root cause: mechanically-fixable vocabulary error — `"workgraph"` is not in
`@projection_types` (`semantic_jira.ex:24`); corrected candidates use the
canonical `["jira", "receipt"]` pair. All five admit; digests byte-match
ledger rows 57-61.

### Class E — `{:missing_required_field, "acceptance"}` (10 rows)

Orders: wo-archive-cleanup, wo-boundary-law-doc, wo-campaign-receipt,
wo-family-xrefs (x2 refusal rows), wo-version-bump, residue-vendor-submodule,
wo-diataxis-expansion, wo-erc-batch-c, wo-regen-wave.
Root cause: mechanically-fixable extraction gap. Rebuilt candidates
(ex4pm x5, beam4pm x5) admit; digests byte-match ledger rows 62-71.

### Class F — `no_workgraph` (2 rows, castle-goal)

Genuine BLOCKED: no `docs/sjira/v26.10.8*/WORKGRAPH.ttl` exists and no
`/Users/sac/castle-goal` checkout exists on disk (verified this session:
`ls: /Users/sac/castle-goal: No such file or directory`). Cannot be
re-admitted without the repository checkout; refusal stands.

## Outcome summary

| class | rows | outcome |
|---|---|---|
| A invalid_sha | 5 | re-admitted (round 2, replay-verified) |
| B invalid_repository | 2 | superseded by per-repo split V8-004A/B/C (replay-verified) |
| C missing base_sha | 4 | re-admitted (round 2, replay-verified) |
| D unsupported projection | 5 | re-admitted (round 2, replay-verified) |
| E missing acceptance | 10 | re-admitted (round 2, replay-verified) |
| F no_workgraph | 2 | BLOCKED — stands (no checkout on disk) |

- 26 of 28 refusal rows: closed by replay-verified re-admission or split.
- 2 of 28 refusal rows (castle-goal `no_workgraph`): standing BLOCKED.
- 0 rows required hand-editing; the admitter's typed refusals were honored.

## Ledger consistency

Ledger unchanged this round: 78 rows, 50 admitted, 28 refused. Every
mechanically-fixable refusal already had an append-only re-admission row from
a prior real admitter run; this round's contribution is the independent
replay verification (7 admitter invocations, all exit 0, all 22 candidate
verdicts byte-matching ledger digests) plus this triage document. No duplicate
re-admission rows were appended — the kernel refuses a duplicate admitted
`work_order_digest` within a batch (`{:refused_candidate, {:duplicate, ...}}`)
and appending no-op rows would erode the ledger's identity model.
