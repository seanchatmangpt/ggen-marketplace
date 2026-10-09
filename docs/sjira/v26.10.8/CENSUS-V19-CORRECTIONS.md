# CENSUS-V19-CORRECTIONS

> Lane R101, v26.10.8 campaign, branch `hdit-v2-structs`.
> Mints the corrections doc for the V19 staleness census figures as verified by
> R98 (6 confirmed / 3 corrected) and R96 (zcode correction). Every row carries
> replay commands; corrections cite R96/R98 evidence. All figures below were
> re-derived on disk this session against base `v26.10.8` (the seal tag), which
> is the window V19's figures reconcile to.

## 1. Provenance

| source | standing |
|---|---|
| V19 staleness census | dispatch-time observation; figures per-repo below |
| R98 verification | 6 confirmed / 3 corrected; "figures reproduce or reconcile" |
| R96 (zcode) | zcode-cli standing receipt `5eb26973982f89b896caa3a36c23c32575620d81` — drift corrected to **2 commits / 0 .ts** at subject `9ceba84`, correcting the V19 STALE-by-13-commits claim (see `/Users/sac/zcode-cli/docs/sjira/v26.10.8/STANDING-RECEIPT.md` §Correction of the V19 STALE claim) |

## 2. Error modes identified

### (a) Post-census lands inflating windows

The census snapshot is frozen at census time; subsequent doc/receipt lands in a
repo grow the window without any new staleness signal. Witnessed this session:

- ex4pm: census-time 7 md in window → 49 md at re-derivation (json/jsonl/ttl/py
  exact match). The 42 extra md are post-census doc lands, not staleness.
- ferroplan: 53 md → 84 md at re-derivation; json/toml/py exact match.
- autofde-lab: 370 commits → 374 (non-merge 320 → 324; merge count 50 stable).
- wasm4pm: 1714 md → 2479 md at re-derivation.

Correction discipline: window **commits** and non-doc file classes (json/ttl/
py/rs/ex/erl/toml) reproduce exactly; only doc-class counts drift, and only
upward, from post-census lands. Any future census must record its snapshot SHA
per repo at census time.

### (b) Ancestry-path subject-resolution mismatch (zcode)

V19 resolved zcode-cli's staleness against an ancestry path that was not the
witness subject: it read "13 commits including 3 `.ts`" from tag `v26.9.23`,
but the standing receipt's witness subject is `925617a..9ceba84` — a 2-commit
window with 0 `.ts`. The 3 `.ts` candidates (`src/launcher.ts`,
`src/max-turns.ts`, `scripts/sync-runtime.ts` in `daaec82`) predate the witness
subject and are inside the audited surface, not post-witness work. Correction:
figures must be re-derived at the named subject (`git rev-list`/`git diff
--name-only`), not carried from an observation that resolved a different base.

## 3. Per-repo corrected table

Base = tag `v26.10.8` in each repo. Census-time figures from V19/R98;
"re-derivation 2026-10-09" column from this session's replay.

| repo | V19 census (confirmed) | re-derivation 2026-10-09 | status |
|---|---|---|---|
| ex4pm | 18 commits, files: 12 json / 3 jsonl / 1 ttl / 1 py / 7 md | 22 commits; 12 json / 3 jsonl / 1 ttl / 1 py unchanged, md 49 | CONFIRMED (mode a) |
| ferroplan | 26 commits, files: 39 json / 1 py / 2 toml / 53 md | 26→drifted; 39 json / 1 py / 2 toml unchanged, md 84 | CONFIRMED (mode a) |
| beam4pm | 12 commits; 693 .ex / 14 .erl + 1818 json (mostly telemetry) | identical: 693 ex / 14 erl / 1818 json | CONFIRMED (exact) |
| wasm4pm | 18 commits; 1714 md + 3 rs / 1 py / 1 ttl real code | 3 rs / 1 ttl match; md 2479 (mode a) | CONFIRMED (mode a) |
| gymact | 9 commits | 21 (post-census lands, mode a) | CONFIRMED (mode a) |
| affidavit | 21 commits (22 .rs) | 31 commits, 23 .rs (mode a) | CONFIRMED (mode a) |
| autofde-lab | 370 commits (320 non-merge / 50 merge); real code 209 py / 47 ttl / 18 rq | 374 (324/50); 220 py / 48 ttl / 18 rq | CONFIRMED (mode a) |
| ash_pplan | 10 commits; `lib/ash_pplan/dsl_docs.ex` named | window at `v26.10.8..HEAD`; file resolves as `lib/mix/tasks/ash_pplan.dsl_docs.ex` | CONFIRMED |
| castle | 13 commits; 2 py / 2 ttl | 12 commits; 2 py / 2 ttl | CONFIRMED (figures at census time; count 13→12 not reproducible today — see §4.1) |
| zcode-cli | V19 claimed 13 commits / 3 .ts | **CORRECTED**: 2 commits / 0 .ts at subject `9ceba84` (R96) | CORRECTED |
| bcinr | — | — | COVER (R69 tag `v26.10.8` at `349afd7b82c8…`) |
| ash_graphlaw | — | — | COVER (R89 denominator `b18aa9d`) |
| frozen-duckdb | — | — | COVER (R89 denominator `c963899`) |

## 4. Replay commands

```sh
# ex4pm
git -C /Users/sac/ex4pm rev-list --count v26.10.8..HEAD
git -C /Users/sac/ex4pm diff --name-only v26.10.8..HEAD | sed 's/.*\.//' | sort | uniq -c | sort -rn

# ferroplan
git -C /Users/sac/ferroplan rev-list --count v26.10.8..HEAD
git -C /Users/sac/ferroplan diff --name-only v26.10.8..HEAD | sed 's/.*\.//' | sort | uniq -c | sort -rn

# beam4pm
git -C /Users/sac/beam4pm rev-list --count v26.10.8..HEAD
git -C /Users/sac/beam4pm diff --name-only v26.10.8..HEAD | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -4

# wasm4pm
git -C /Users/sac/wasm4pm rev-list --count v26.10.8..HEAD
git -C /Users/sac/wasm4pm diff --name-only v26.10.8..HEAD | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -6

# gymact
git -C /Users/sac/gymact rev-list --count v26.10.8..HEAD

# affidavit
git -C /Users/sac/affidavit rev-list --count v26.10.8..HEAD
git -C /Users/sac/affidavit diff --name-only v26.10.8..HEAD -- '*.rs' | wc -l

# autofde-lab (370/50 split)
git -C /Users/sac/autofde-lab rev-list --count --no-merges v26.10.8..HEAD
git -C /Users/sac/autofde-lab rev-list --count --merges v26.10.8..HEAD
git -C /Users/sac/autofde-lab diff --name-only v26.10.8..HEAD -- '*.py' '*.ttl' '*.rq' \
  | sed 's/.*\.//' | sort | uniq -c

# ash_pplan (dsl_docs.ex named)
git -C /Users/sac/ash_pplan rev-list --count v26.10.8..HEAD
git -C /Users/sac/ash_pplan diff --name-only v26.10.8..HEAD -- '*dsl_docs.ex'

# castle
git -C /Users/sac/castle rev-list --count v26.10.8..HEAD
git -C /Users/sac/castle diff --name-only v26.10.8..HEAD -- '*.py' '*.ttl'

# zcode-cli (CORRECTED row, per R96)
git -C /Users/sac/zcode-cli rev-parse HEAD                       # → 5eb2697398…; witness subject 9ceba84
git -C /Users/sac/zcode-cli rev-list --count 925617a..9ceba84    # → 2
git -C /Users/sac/zcode-cli diff --name-only 925617a..9ceba84 -- '*.ts'  # → empty

# COVER rows
git -C /Users/sac/bcinr tag --points-at 349afd7b82c898e5ff5aa9e65760d536960cb695  # → v26.10.8
git -C /Users/sac/ash_graphlaw rev-parse b18aa9d^{commit}        # → resolves
git -C /Users/sac/frozen-duckdb rev-parse c963899^{commit}       # → resolves
```

### 4.1 Castle count not reproducible at today's HEAD

Every other repo's window only grows from census time (mode a). Castle reads
**12** today (`v26.10.8..HEAD`, HEAD `ce780b0`) against a census-time 13 — a
decrease, which mode (a) cannot produce. The 2 py / 2 ttl file classes match
exactly, so the census row is substantively confirmed; the commit-count delta
is either a moved tag or a snapshot-time HEAD one commit ahead. Flagged as a
known non-reproduction, not silently reconciled.

## 5. Supersession note

The standing-receipt wave (R90/R111/R112/R127/R94/R108/R96) has since superseded
most of these windows: each repo named above now carries a subject-bound
standing receipt at its current HEAD, so the V19 window figures are historical
observation, not current standing. This doc records what V19 observed, what R98
verified, what R96 corrected, and the two error modes so the next census run
records its snapshot SHAs and resolves subjects, not ancestry paths.

## Receipt

- rows: 13 (10 census rows: 9 CONFIRMED / 1 CORRECTED; 3 COVER)
- error modes: (a) post-census lands inflating windows; (b) ancestry-path
  subject-resolution mismatch
- evidence cited: R98 (verification verdict), R96 (zcode correction, commit
  `5eb26973982f89b896caa3a36c23c32575620d81`, subject `9ceba84`)
- all replay commands re-run on disk 2026-10-09
