# pin-reconcile-2026-11-05

Standing: PARTIAL

Reconciliation of the pin-decision surface in ggen-marketplace as of 2026-11-05.
Read-only audit; no manifests edited. Every user-gated/coordinator decision is
REGISTERED here, not executed.

## 1. [ggen] execution pin — frozen v26.8.11 vs released v26.10.8

`marketplace.toml:32-35` pins:

```toml
[ggen]
version = "v26.8.11"
release_commit = "402cecdff8784767eb9f26e235d87c759610c066"
```

with four digest-pinned release assets (linux x86_64/aarch64, darwin
x86_64/aarch64) under `[ggen.assets.*]`. The repo itself has since released
**v26.10.8**, while the court identity remains frozen at v26.8.11 by design
(tag→commit binding verified; `install-ggen.sh` independently re-verifies the
tag identity and all four sha256 digests before accepting a release asset).

**Status: BLOCKED:pin-bump-user-gated** — annotated inline at
`marketplace.toml:27-30` ("2026-10-05: pin-bump requested and refused").
Companion note: `docs/context/ggen-pin-bump.pending.md` — itself marked
SUPERSEDED 2026-10-13 (its concrete steps targeted v26.10.5 artifacts that
never landed).

### What a lawful bump requires

1. **Explicit user authority** for the target version (the gate is
   user-gated, not lane-gated; a prior request was refused).
2. A fresh decision record, NOT the stale pending note: re-derive from the
   current `marketplace.toml` plus the actual target release artifacts.
3. Exact edits (4 keys + 4 digests): `version`, `release_commit` (the
   tagged commit sha), and sha256 for each of the four release assets
   (`ggen-{x86_64-unknown-linux-gnu,aarch64-unknown-linux-gnu,aarch64-apple-darwin,x86_64-apple-darwin}.tar.gz`).
4. Verification ladder in order:
   - `bash scripts/admit-config.sh marketplace.toml <admitted.json>`
   - version court via `scripts/qualify-marketplace.sh` with
     `GGEN_MARKETPLACE_ADMITTED_CONFIG` set (refuses `GGEN_VERSION_DRIFT`)
   - `bash scripts/install-ggen.sh` (tag→commit binding + 4 digests)
   - `python3 scripts/qualify_packs.py --report <report.json>` full corpus.
5. Precondition the pending note warns about: release assets must actually
   be published on the target tag — digests cannot be minted from a local
   tag.

**Drift caveat observed 2026-11-05**: the last committed baseline receipt
(git log `9d042c2cf`, ZD-65) states the 26.10.11 pin "can no longer run the
court — script hard-codes --skip-ea-admission" and re-projected under
`ggen 26.11.3`. The `marketplace.toml` v26.8.11 pin and the qualification
harness's effective ggen version are therefore already divergent surfaces;
a pin-bump decision must reconcile BOTH, not just the toml.

## 2. qualification/baseline.json — uncommitted re-pin 26.10.11 → 26.11.3

`qualification/baseline.json` has uncommitted working-tree changes (confirmed
`git status` + `git diff` 2026-11-05):

- `ggen_version`: `ggen 26.10.11` → `ggen 26.11.3`
- counts: ALIVE 338 → 330, WARN 9 → 17 (REFUSED 0, SKIPPED 1 unchanged)
- 17 packs reclassified ALIVE→WARN, each carrying a
  `ACCEPTED-WARN:<class>` annotation plus a `warn_class` ratchet field.

**Decision needed (user/coordinator): COMMIT or DISCARD.**

- **Commit** = admit the 26.11.3 court as the new baseline and accept the 17
  WARNs as ratcheted residue. Required by the ZD-65 receipt's finding that
  the old 26.10.11 pin can no longer execute the court at all.
- **Discard** = restore the 26.10.11 baseline, but then the qualification
  harness must be re-pinned to a ggen that can actually run it — the ratchet
  check fails on stale counts otherwise.

### The 17 reclassified WARN classes

By `warn_class` (from `git diff`):

| warn_class | count | annotation class(es) |
|---|---|---|
| environment-wedge | 10 | `cargo-build-check-timeout-syspolicyd-wedge` (cargo build timed out after 120s, manifest=consumer/Cargo.toml) |
| ratchet-residue | 7 | `missing-external-path-dependency` (5, failed to read `ggen-graph/Cargo.toml`), `missing-external-dependency` (1), `workspace-members-not-pack-outputs` (1) |
| harness-limitation | 1 | — |

Named packs observed in the diff: automatic-autonomic-operations-pack,
certification-assist-evidence-control-pack, certification-assist-pack,
clap-noun-verb-crate-pack, clap-noun-verb-schema-pack,
clap-noun-verb-zeroconfig-pack. (Full roster is in the working-tree diff of
`qualification/baseline.json`; the diff is the authoritative list until the
commit/discard decision lands.)

If COMMIT: the 17 annotations become the registered-divergence ledger per
[[testing-chicago-style]] SDK-parity law — each cell is pass /
registered-divergence / loudly-missing, never a silent skip. The
`ACCEPTED-WARN:*` strings are the close conditions; an `environment-wedge`
entry should be re-run on an unloaded machine before it is accepted as
permanent.

## 3. Machine-local pins (portability debt)

Three classes of absolute-path / layout-assumption pins found in-tree.

### 3a. Absolute /Users/sac path — kubernetes-workload-pack example

`packs/kubernetes-workload-pack/examples/minimal-secure-workload-fixture/ggen.toml:11`:

```toml
"kubernetes-workload-pack" = { path = "/Users/sac/ggen-marketplace/packs/kubernetes-workload-pack" }
```

Sibling examples (e.g. `examples/high-assurance-workload/ggen.toml`) already
use the portable form `{ path = "../.." }` — the fixture example is the
outlier. **Close condition**: rewrite line 11 to `path = "../.."` and the
example re-syncs green from any checkout depth; falsifier is a fresh clone
at a different absolute path running the fixture sync.

### 3b. Sibling-layout assumption — chicago-xaas-surface-pack consumer

`packs/chicago-xaas-surface-pack/consumer/ggen.toml:22-64` assumes the
consumer repo is checked out as a SIBLING of `ggen-marketplace`: every
source/query/template path is `../ggen-marketplace/packs/chicago-xaas-surface-pack/...`
(8+ path references across lines 22-64). **Close condition**: either (a)
parametrize via a `[packs]` path dependency (as the kubernetes examples do)
so ggen resolves pack-internal paths through the dependency, or (b) document
the sibling-checkout contract in the pack README AND add a setup check that
refuses loudly when `../ggen-marketplace` is absent — currently the failure
is a silent file-not-found at sync time.

### 3c. External-repo consumers — affidavit-trust-plane-pack, chicago-graphlaw-court-pack

- `packs/affidavit-trust-plane-pack/ggen.toml:4` — header comment names the
  consumer as `/Users/sac/affidavit ggen.toml` merging this pack's ontology.
  The pack-local file is a self-proof project profile; the real consumer
  manifest lives in another repo, unversioned here.
- `packs/chicago-graphlaw-court-pack/consumer/ggen.toml:1,11-37` — "install
  as /Users/sac/graphlaw/ggen.toml (coordinator-owned there)"; body paths
  `../ggen-marketplace/packs/chicago-graphlaw-court-pack/...` (ontology,
  cases/a.ttl, cases/b.ttl, queries, templates) — same sibling-layout
  assumption as 3b, deployed cross-repo.

**Shared close condition**: each external consumer manifest should either
live in the consumer repo with a recorded SHA receipt (the manifest here
becomes a template, not the live surface), or carry a setup/doctor check.
Until then each is UNPORTABLE-by-design with a named owner ("coordinator-owned
there") — acceptable as registered divergence, unacceptable as undocumented
divergence. Register each in the pack README with the consumer repo + commit.

## 4. Dual ggen.toml + pack.toml manifests — 74 packs, ambiguity risk

Counted 2026-11-05: 349 entries under `packs/`; 50 `pack.toml` files
reference `ggen.toml`; **26 packs carry BOTH `ggen.toml` and `pack.toml` at
top level** (sampled census: 5-pack spot check + repo-wide reference count;
a per-pack exact roster needs one more pass — figure is bounded between the
26 dual-manifest confirmed set and the 50 referencing set, and the task
brief's "74" was not independently reproduced).

### Convention inferred from 5 sampled packs

| pack | ggen.toml role | pack.toml role |
|---|---|---|
| a2a-conformance-pack | absent | pack identity/description/version metadata |
| affidavit-pack | absent | pack identity metadata (+ DEPRECATION.md) |
| sa2a-spark-dsl-pack | absent | pack identity metadata |
| adapter-family-matrix | absent | pack identity metadata |
| xaas-ash-core-pack | `[project]` ggen sync contract (name/version/description + generation config) | pack identity metadata |
| affidavit-consumer-pack | self-proof render profile (`generated/` projection) | identity metadata |
| aaif-vanilla-pack | DeclarativeRules generation contract | identity metadata |

**Convention**: `pack.toml` = marketplace PACK IDENTITY (name, version,
description — what the marketplace registry reads); `ggen.toml` = ggen SYNC
CONTRACT (how `ggen sync` projects output — ontology sources, packs deps,
generation rules). They are not duplicates; they are two different machines'
manifests that happen to share a name field.

**Proposal**: declare `pack.toml` canonical for IDENTITY (version bumps,
descriptions, registry enumeration) and `ggen.toml` canonical for
GENERATION. Never hand-edit `ggen.toml` fields that mirror `pack.toml`
without syncing the pair — the `name`/`version` fields currently drift
independently (e.g. affidavit-consumer-pack ggen.toml version `26.9.30`
vs pack.toml `0.1.0`-style). A lint gate asserting
`pack.toml.name == ggen.toml.[project].name` across all 26 dual-manifest
packs is the mechanical enforcement; until it exists, the ambiguity risk is
a consumer syncing with stale identity metadata.

## Decision queue (all user/coordinator-gated; registered, not executed)

1. Pin bump v26.8.11 → target: BLOCKED:pin-bump-user-gated (needs authority
   + published artifacts; must reconcile the 26.11.3-effective qualification
   harness drift per §1 caveat).
2. baseline.json re-pin: COMMIT (admit 26.11.3 baseline + 17 ACCEPTED-WARN
   rows) or DISCARD (re-pin harness) — pick one; leaving it uncommitted is
   the current silent-drift state.
3. Portability fixes §3a-3c — lane-executable except the cross-repo
   registrations in 3c, which need the consumer repos' coordinators.
4. Manifest canonicity §4 — adopt the identity-vs-generation split + name
   lint; needs a decision to make it law before the lint lands.

## Receipt

- Subject: `/Users/sac/ggen-marketplace` (canonical checkout, branch main).
- Commands run: `git status`, `git diff qualification/baseline.json`,
  manifest reads (marketplace.toml, 5 sample packs, 4 named pin files),
  pack census (`ls packs | wc -l`, pack.toml reference grep, dual-manifest
  count loop).
- Files created: this document only (OWNED FILES honored; no manifest edits,
  nothing committed).
- Standing: PARTIAL — all four surfaces materialized and registered; the
  §4 dual-manifest count (26 confirmed dual vs task-brief's 74) and the full
  17-pack WARN roster (diff is authoritative) are the two figures needing a
  second mechanical pass before they are cited as final.
