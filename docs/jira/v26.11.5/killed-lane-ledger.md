# Killed-Lane Ledger — 8 lanes killed pre-reboot (2026-11-05)

Standing: PARTIAL

Source enumerations: `docs/jira/v26.11.5/pre-reboot-inventory.md` (snapshot at
commit 1d42c69e0, 2026-11-05 15:39:31 PST) and the wave-2 registry
(`docs/jira/v26.11.5/pack-refactor-wave2-registry.md`). Every claim below was
re-derived on disk 2026-11-05 (post-reboot) via scoped `git status --porcelain`,
`git diff --stat`, and file existence checks. This ledger presents EVIDENCE ONLY
— the commit-or-discard decision per R11 is the coordinator's.

## Lane identity map (derived, not asserted)

The pre-reboot inventory lists dirty files, not lane ownership. Ownership below
is derived from `pack-refactor-wave2-registry.md` (G-lanes, one pack per lane)
and from F-receipt subjects:

- F1 shacl-projection-pack, F2 shacl-to-zod-pack, F3 supabase-pack,
  F4 census, F5 four-pack integration court (receipts F1–F5 landed).
  F6 = shadcn-ui-primitives-pack by elimination: F5's court covered exactly the
  four cmms-referenced packs (shacl-projection, shacl-to-zod, supabase,
  shadcn-ui-primitives); F1–F3 own the first three, and the dirty
  shadcn-ui-primitives-pack surface (v0.2.0→0.3.0 Field-family refactor) is the
  only remaining member of that four-pack set with no receipt. Cross-checked
  against the cmms repo's landed deep-research commit ef7bea8 ("shadcn registry
  format + Field-family forms") — same refactor object. F6 has NO entry in any
  registry or receipt — the F-wave registry never named it; this inference is
  the strongest available evidence, marked as inference.
- G-lanes: G01 nextjs-ai-sdk-pack, G09 sa2a-fastapi-pack, G11
  ash-pplan-igniter-pack, G13 fastmcp-pack, G14 typer-azure-pack, G16
  cargo-cicd-pack, G17 rmcp-pack (registry lines 16–32).

## Per-lane evidence

### F6 — shadcn-ui-primitives-pack (identity inferred; no receipt)

On-disk state (all present in working tree, none committed):
- Modified: `packs/shadcn-ui-primitives-pack/pack.toml` (0.2.0 → 0.3.0,
  description extended with Field family), `README.md` (+76 lines diff),
  `ontology.ttl` (+68 lines), `templates/060_lib_utils_ts.tmpl` (7-line change
  — CAUTION: F4's cross-lane hazard says lib/utils.ts body is shared with
  G03/G04 packs, "do NOT change its body"; a 7-line diff exists here).
- New (untracked): `gates/020_requires_dep_declared.rq`,
  `templates/field.tsx.tmpl`, `templates/use-form-hook.ts.tmpl`.
- No `receipts/F6.md` exists in `docs/jira/v26.11.5/receipts/` (F1–F5, G02–G18
  minus the killed set, P1–P4 only).
- Coherence: coherent work-in-progress toward a v0.3.0 Field-family release
  matching the landed cmms deep-research object; court/receipt absent, and the
  `060_lib_utils_ts.tmpl` body change conflicts with the wave's own
  do-not-change hazard rule. NOTE: this pack is FENCED per the wave registry
  (one of the four cmms-referenced packs), yet it carries a full refactor —
  the fence status itself needs coordinator adjudication.
- LAND/DISCARD evidence balance: substantive, near-complete-looking refactor;
  blocked on (a) court/receipt absence, (b) the utils-body hazard, (c) fence
  legality. Decision inputs flagged, decision not made.

### G01 — nextjs-ai-sdk-pack

On-disk state:
- Modified: `packs/nextjs-ai-sdk-pack/pack.toml` (26.7.24 → 26.11.5; new
  `[consumer_contract]` block, mechanically derived import table, +46 diff
  lines), `README.md` (new file, +35 lines — tracked-existence caveat: README
  is untracked `??` in git status, content present on disk).
- No `receipts/G01.md`.
- Coherence: matches the house pattern exactly (version bump + consumer_contract
  + README); small surface, two files. Looks LAND-eligible pending court
  evidence (no court output recorded anywhere on disk for G01).
- Exact files: `packs/nextjs-ai-sdk-pack/pack.toml`,
  `packs/nextjs-ai-sdk-pack/README.md` (untracked).

### G09 — sa2a-fastapi-pack

On-disk state:
- Modified: `packs/sa2a-fastapi-pack/pack.toml` (+27 diff lines).
- New (untracked): `packs/sa2a-fastapi-pack/README.md`.
- No `receipts/G09.md`.
- Coherence: same house-pattern shape as G01/G13/G16/G17; court evidence
  absent on disk.

### G11 — ash-pplan-igniter-pack

On-disk state:
- Modified: `packs/ash-pplan-igniter-pack/pack.toml` (+40 diff lines).
- New (untracked): `README.md`, `ggen.toml`, `lib/mix/` (empty directory
  skeleton — `lib/mix/` contains no files, only directories; verified
  `ls -la`: total 0, only `mix/` subdir).
- No `receipts/G11.md`.
- Coherence: pack.toml/README/ggen.toml follow the house pattern; the
  `lib/mix/` tree is EMPTY — a lane-lease-style build-root lease or an
  incomplete template surface; per the fanout cleanup law, empty lease dirs
  are deletable at integration. Whatever the intent, `lib/mix/` empty skeleton
  is evidence of an incomplete state.

### G13 — fastmcp-pack

On-disk state:
- Modified: `packs/fastmcp-pack/pack.toml` (+28 diff lines,
  0.1.0 → 0.2.0, consumer_contract with `runtime = ["fastmcp"]`).
- New (untracked): `packs/fastmcp-pack/README.md`.
- Receipt EXISTS but untracked: `docs/jira/v26.11.5/receipts/G13.md`
  (Standing: PASS; its "Pip tier outcome" section records the pip-install
  court as **PENDING** — G13.md:81-83, "moved to background by the harness on
  the 300s timeout; result recorded here when it completed: **PENDING**").
  The receipt's diff summary and court commands are complete for the
  projection/compile tier (py_compile exit 0, import+list_tools exit 0,
  byte-stable re-projection); only the pip tier is PENDING.
- Coherence: strongest candidate — a real court ran on the landed pack's real
  output; the only gap is the PENDING pip tier. Note: the pip-tier result was
  "recorded here when it completed" but the receipt still says PENDING, so
  the promised backfill never landed before the kill.

### G14 — typer-azure-pack

On-disk state:
- Modified: `packs/typer-azure-pack/pack.toml` (26.10.22 → 26.11.5),
  `packs/typer-azure-pack/ggen.toml` (26.10.22 → 26.11.5).
- New (untracked): `README.md`, `consumer_contract.md`, `gates/` (4 files:
  `010_required_options.rq`, `020_typer_module.rq`, `run_gates.py`,
  executable `run_gates.sh`, mtimes 15:25–15:27 — pre-kill).
- No `receipts/G14.md` (checked `receipts/` — no G14.md).
- Coherence: the most complete surface of the killed G-lanes (contract doc +
  gates + runner scripts present on disk); court run evidence absent on disk.
  This is the only killed lane with an executable gate runner.

### G16 — cargo-cicd-pack

On-disk state:
- Modified: `packs/cargo-cicd-pack/pack.toml` (+24 diff lines).
- New (untracked): `packs/cargo-cicd-pack/README.md`.
- No `receipts/G16.md`.

### G17 — rmcp-pack

On-disk state:
- Modified:
  `packs/rmcp-pack/pack.toml` (+21 diff lines).
- New (untracked): `packs/rmcp-pack/README.md`.
- No `receipts/G17.md`.
- Coherence: minimal house-pattern surface (pack.toml bump + README), same
  class as G09/G16.

## Kafka-wire-pack fenced state (explicit)

`packs/kafka-wire-pack/**` dirty files (ontology.ttl, 6 templates, pass/fail
witnesses for 050_version_matrix_closure) are EXPLICITLY FENCED: pre-reboot
inventory line 2 and commit 1d42c69e0 both mark kafka-wire-pack as "other
session's work, never ours". The MK-1 receipt
(`docs/jira/v26.11.4/receipts/mk1-wip-finish.md`, Standing: PASS, untracked)
classifies the kafka change-set as one coherent served-version-matrix
correction (KD-190 / KD-HC-1 / KD-HC-3, 2026-11-04) belonging to the prior
crashed session. Action space is the other session's (or coordinator's), not
a killed-lane decision.

## Adjacent dirty surfaces NOT owned by the 8 killed lanes

For completeness (coordinator triage; not lane-owned):

- `packs/github-actions-pack/**` (README, pack.toml, 2 templates modified):
  G15 has a LANDED receipt (`receipts/G15.md`, Standing: PASS) yet its pack
  files remain dirty — the G15 commit (v0.4.0) has not landed. Receipt exists,
  commit does not. This is the receipt-without-commit inverse of the killed
  lanes' commit-without-receipt problem.
- `packs/shadcn-ui-primitives-pack/**`: see F6 above; also fenced-pack
  legality.
- `packs/smalt-substrate-pack/ontology.ttl`: 1-line change
  (st-smalt_eh_checkpoints persisted false→true) — MK-1 receipt scope
  ("kafka-wire-pack + smalt-substrate-pack"). MK-1's, not a killed lane's.
- `packs/qri-consumer-binding-pack/ggen.lock`: blake3 content_hash updated —
  S-8 receipt scope (untracked, Standing: PARTIAL_ALIVE).
- `qualification/baseline.json` (+79 diff lines, typed WARN annotations) —
  WARN-1 receipt scope (untracked, Standing: PARTIAL_ALIVE).
- `scripts/verify_enterprise_kudzu_profile.py`,
  `scripts/verify_msct_profile.py`: modified, no lane receipt found.

## v26.11.4 untracked-receipts issue

`docs/jira/v26.11.4/` (receipts mk1-wip-finish.md, s8-tag-reverify.md,
warn1-baseline-reconcile.md) is entirely untracked. Internal cross-references
observed: warn1-baseline-reconcile.md:19 cites s8-tag-reverify.md; both cite
the v26.11.3 zd-52 typed baseline; s8 cites ggen SEED.md:93-94/:124/:49.
CHANGELOG reference status: I could NOT verify the claim that CHANGELOG.md
references these three receipts — `grep 'mk1\|s8\|warn1' CHANGELOG.md` at HEAD
returns zero hits, and the latest CHANGELOG-touching commit (8d626dece,
"CHANGELOG wave entry") mentions v26.11.4 in its message but adds no receipt
paths. Recorded as UNVERIFIED-CLAIM: either the reference lives in an
uncommitted CHANGELOG edit (none dirty in git status) or in a file outside
this repo; nothing on disk here substantiates it. If the coordinator's
citation is correct, the reference must live somewhere I did not find; as
observed, the only dangling-reference risk is intra-dir (warn1 → s8).

## Verification receipt (this ledger's own)

Commands executed 2026-11-05, all exit 0 unless noted:
- `git status --porcelain` (full tree)
- `git diff --stat` scoped to all named packs + baseline.json
- `ls docs/jira/v26.11.5/receipts/ docs/jira/v26.11.4/receipts/`
- `git log --oneline -5`, `git show 1d42c69e0 --stat`,
  `git show 8d626dece --stat`
- `sed -n '70,95p' docs/jira/v26.11.5/receipts/G13.md`
- `ls -la packs/ash-pplan-igniter-pack/lib/ packs/typer-azure-pack/gates/
  packs/shadcn-ui-primitives-pack/gates/`
- `git diff packs/smalt-substrate-pack/ontology.ttl
  packs/qri-consumer-binding-pack/ggen.lock packs/typer-azure-pack/ggen.toml`
- `grep 'mk1\|s8\|warn1' CHANGELOG.md` (zero hits)

F6 lane identity is INFERENCE (elimination + object match), not registry fact
— first item for coordinator confirmation.
