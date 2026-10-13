# Cross-Repo High-Assurance Wave Receipt — 2026-10-13

**Wave**: cross-repo high-assurance wave, 2026-10-13.
**Coordinator subject**: ggen-marketplace @ `main`
`50a458f6081328f26b3d6080c418d9994892ac88` (+ in-flight hash-pack tree
edits, see §3).
**Format**: follows `SYNC-WAVE-RECEIPT.md` / `STRATA-BLOCKCHAIN-CLOSE.md`.
**Standing vocabulary**: UNKNOWN / PARTIAL_ALIVE / ALIVE / BLOCKED /
BUILD_BROKEN / UNSUPPORTED, plus typed `REFUSED:*`. Inspection and commit
existence are not execution; each ALIVE claim carries its court reference.

## 1. Landed surface (per repo)

### ggen-marketplace

| item | commit | note |
|---|---|---|
| net T3 attack-corpus fuzz + T4 admission gate | `0b8c7de64` | net hardening |
| governance constitutional-diff gate (T11) | `c5e0cf876` | castle candidate |
| valve real refusal-receipt derivation | `8210f1b24` | seam-29 closure, L13 |
| consensus fork sims + store crash corpus x10 + index sweep | `c3af04adc` | L20/L21/L22 |
| chain shared-KAT head court + diff to net/ledger | `f0278013d` | L9/L16 |
| ledger OCEL-v2 emission + PN64 surface (T2) | `00e0b086b` | |
| store atomic undo_to_fork + crash journal (T1) | `d66c8e6bb` | |
| corpus courts parametrized to 15-pack family | `d0bfe2c8d` | W4 |
| signer ML-DSA courts + Merkle domain-sep fix + how-to | `274039f55` | L24/L25/L29 |
| ledger witnessed-ledger-replay KAT court | `118d242f0` | L27 |
| tx fuzz + byte-mutation courts + unguarded pin | `bfe64efd8` | L44 |
| audit corpus refresh + pn64 fuzz target | `d0bf6d562` | S10, L28 |
| store rollback_to interleave guard | `76d9aebd6` | L47/L34, confirmed |
| tx total-coverage digest | `ea2cff11b` | L46, zero unguarded |
| refusal-vocabulary-pack crosswalk | `50a458f60` | L59, C14 precondition |
| mdBook nav regen — fixture-court chapter | `51aea5879` | L50 book/how-to |
| governance set-guard fixture update | `d47224753` | |
| pn64 transitionPost gated law comment | `c1892ef48` | L38 doc fix |

### affidavit

| item | commit | note |
|---|---|---|
| genesis seed frozen to deployed wasm generation | `dcba4e9` | fix(chain) |
| FM-CHAIN-009 fixture shared with graphlaw | `975b2e7` | seam 28 |
| refusal-receipt codec seam (hash-then-commit) | `7e8b582` | seam 29 |
| seam-29 v2: real sha256 refusal receipts | `acda559` | L26 |
| zero-dep FIPS 180-4 SHA-256 ChainHasher | `ad24a28` | L42 |

### graphlaw

| item | commit | note |
|---|---|---|
| npm scaffold + JS CI/publish workflows | `af3c169` | install claim gated `f598c67` |
| graphlaw-attest bin: sign/verify/pubkey | `cb707e7` | used by ash_a2a |
| FM-CHAIN-009 fixture to tests/fixtures | `8d6dce7` | seam 28 |
| vecgen corpus (B3) + meta drift guard (B2) + RDFC-1.0 (L2) | `9210de8` | |
| pn64 ABI differential (L4) + temprun fuel court (L6) | `d499d5c` | |
| wasm gate re-scope: rebuild-equality -> ABI-surface | `b473313` | L19 |

### ash_a2a

| item | commit | note |
|---|---|---|
| STANDING-RECEIPT signed via graphlaw-attest | `2d30b819` | |
| tasks/list pagination echo + historyLength (Y10) | `68e4724e` | merge `3df490b6` |
| authorize_task_list keeps page_size post-filter | `13622178` | Y10 class |
| hermetic freedom-gym OCEL e2e court (T9) | `4d9159ec` | + verifier lock |
| standing-receipt two-stage verifier task | `b52359f5` | L42/L1 |

### beam4pm

| item | commit | note |
|---|---|---|
| ontology admission via gated path; draft retired | `cdd6fd7e` | |
| ephemeral test ports + eight-vow conformance court | `9cf06362` | L37/L61 |

### castle

| item | commit | note |
|---|---|---|
| strata ggen-receipt/v2 ingest, chain-hash recompute | `2337b70` | L14 |
| untrack target/ + Cargo.lock sweep | `72fe5c8` | hygiene |
| trust-key enrollment + Replayed producer + RDF lift | `fea79b4` | L49/L62 |

### mfact

| item | commit | note |
|---|---|---|
| PN64 conservation witness, machine-checked | `bec0bc0b` | T2/X7-1 |
| fork-choice termination + head uniqueness | `45f06645` | T13 |

### erlmcp

| item | commit | note |
|---|---|---|
| jsx -> erlmcp_json wrapper + iodata fixes (F1) | `e9227a1c` | |
| `{doc, chunk}` in erl_opts (F16) | `5c861c43` | |
| maybe-expression refactor (F9) | `215f400b` | |
| otp27 json error-shape tests | `0f5f7c60` | |
| F18: residual verify_none TLS sites fixed | `cdcbcd6a` | |
| priority-queues merge | pre-window on this checkout | see §3 |

### chicago-tdd-tools

| item | commit | note |
|---|---|---|
| W50-W52: git2 ERC-delete, race fix, typed errors | `4357924`..`f455b1b` | 12 commits, pushed |

### mcp-mqtt-erl

| item | commit | note |
|---|---|---|
| gen_statem named event timers (F3), otp27 merge | `253f6ba` / `b767e87` | |
| first real eunit suite + quicer-free compile | `ffeb47c` | L56, local-only |

## 2. Real findings register

1. **Merkle domain-separation vulnerability** (hash-pack) — leaf vs node
   hashing shared a prefix; fix landed `274039f55`; hash-pack follow-up
   (ontology/template/generated) uncommitted in the working tree at
   receipt time.
2. **tx unguarded wire fields** — byte-mutation courts exposed fields not
   covered by the digest; fixed `ea2cff11b` (L46), zero remaining.
3. **store rollback_to interleave divergence** — CONFIRMED real and fixed
   with an interleave guard `76d9aebd6` (L47/L34).
4. **pn64 t04 mask** — transition-mask defect surfaced by conformance
   courts; gated law documented `c1892ef48` (L38).
5. **fire-law XOR doc hazard** — transitionPost comment imprecise about
   the gated clear-then-set law; corrected `c1892ef48`.
6. **iri.ex check_receipt presence-only gap** (ash_a2a) — receipt check
   verified presence, not content; addressed by the L42 standing
   verifier work `b52359f5`.
7. **mcp-mqtt-erl json iolist + is_list bugs** — fixed via the
   erlmcp_json wrapper migration `e9227a1c` (F1); the mcp-mqtt-erl
   checkout carries local fixes, unpushable (403).
8. **GallOcel category boundary** — OCEL event/object typing boundary
   clarified during castle/ledger lift; recorded in the innovation
   ledger, design-only.
9. **wasm non-reproducibility** (graphlaw) — byte-equality-of-rebuild
   unfalsifiable in practice; re-scoped to ABI-surface equality
   `b473313` (L19).
10. **vacuous-harness premise falsified fleet-wide** — the premise that
    the shared corpus harness could pass vacuously was falsified across
    the 15-pack parametrization (`d0bfe2c8d`, W4) and the ledger #44
    refresh (`b96489342`).

## 3. Standing table

### ALIVE (with court receipt)

| item | repo @ commit | court / receipt evidence |
|---|---|---|
| net T3/T4 gates | ggen-marketplace `0b8c7de64` | fuzz + admission gate courts |
| valve refusal-receipt derivation | ggen-marketplace `8210f1b24` | seam-29 closure court |
| fork sims / crash corpus / index sweep | ggen-marketplace `c3af04adc` | L20/L21/L22 court runs |
| chain shared-KAT head court | ggen-marketplace `f0278013d` | KAT court, family-wide |
| ledger OCEL-v2 + PN64 surface | ggen-marketplace `00e0b086b` | PN64 conformance court |
| store undo_to_fork + journal | ggen-marketplace `d66c8e6bb` | crash-recovery courts |
| signer ML-DSA courts | ggen-marketplace `274039f55` | L24 court run |
| ledger replay KAT | ggen-marketplace `118d242f0` | L27 KAT receipt |
| tx fuzz + byte-mutation courts | ggen-marketplace `bfe64efd8` | L44 courts |
| audit corpus refresh | ggen-marketplace `d0bf6d562` | S10 court |
| store rollback guard | ggen-marketplace `76d9aebd6` | divergence court, then fix |
| tx total-coverage digest | ggen-marketplace `ea2cff11b` | zero-unguarded court |
| refusal-vocabulary-pack | ggen-marketplace `50a458f60` | crosswalk court (C14) |
| Merkle domain-sep fix | ggen-marketplace `274039f55` | domain-sep court (L25) |
| governance constitution 9 | ggen-marketplace `f0278013d`/`c5e0cf876` | diff-gate courts |
| affidavit seam 28/29 + ChainHasher | affidavit `975b2e7`..`ad24a28` | sha256-pinned courts |
| graphlaw conformance courts | graphlaw `8d6dce7`..`d499d5c` | B2/B3/L2/L4/L6 courts |
| wasm gate re-scope | graphlaw `b473313` | ABI-surface court (L19) |
| ash_a2a pagination + e2e + verifier | ash_a2a `68e4724e`..`b52359f5` | T9 e2e, 2-stage verifier |
| beam4pm vows + ports + ontology | beam4pm `cdd6fd7e`, `9cf06362` | eight-vow court (L61) |
| castle ingest + trust chain + lift | castle `2337b70`..`fea79b4` | chain-hash court, L49/L62 |
| mfact Lean witnesses x2 | mfact `bec0bc0b`, `45f06645` | machine-checked (Lean) |
| erlmcp otp27/TLS hardening | erlmcp `e9227a1c`..`cdcbcd6a` | error-shape tests, F18 fence |
| chicago-tdd-tools W50-W52 | chicago-tdd-tools `f455b1b` | release-validate court |
| mcp-mqtt-erl eunit + compile | mcp-mqtt-erl `ffeb47c` | first real eunit run (local) |

### NOT verified (typed boundaries)

1. **chain-file format** — no court this wave; receipts cover in-memory
   chains only.
2. **re-mint flow** — unexercised; no witnessed run.
3. **castle nightly-only build** — landed castle commits have no green
   daytime CI witness.
4. **mcp-mqtt-erl unpushable (403)** — local commits `253f6ba`..`ffeb47c`
   verified only locally; remote refuses push, so no remote/CI evidence.
5. **TCK re-run pending** — ash_a2a v1.0 TCK re-run not executed against
   the Y10/L42 head.
6. **knhk merge user-blocked** — awaits user direction; no merge commit.
7. **hash-pack working-tree edits** — Merkle follow-up uncommitted; no
   court has run on the tree as-written.

## 4. What was NOT done

1. **knhk merge completion** — user-interrupted mid-merge, awaiting
   direction; knhk checkout has no wave commits.
2. **unibit fate** — owning lane still in flight; no decision recorded.
3. **C20 arbiter** (generator-plurality court) — design only; no
   implementation or falsifier run.

## 5. Standing drift — evening fleet state (2026-10-13, L102 ledger)

Source: L102 read-only fleet push ledger (`/tmp/fleet-push-ledger.md`);
SHAs re-read from `git log` at write time. Supersedes per-repo standing
above where it moved after L75 wrote this receipt.

### 5.1 Per-repo push classification (L102)

| repo | classification | push ff? |
|---|---|---|
| ggen-marketplace | AHEAD-1 (dirty: strata packs) | yes |
| graphlaw | SYNCED (dirty) | n/a |
| ash_a2a | SYNCED (dirty) | n/a |
| beam4pm | SYNCED (dirty: 615 files) | n/a |
| castle | AHEAD-4 | yes |
| mfact | SYNCED (dirty: 140, mostly `.agents/`) | n/a |
| affidavit | AHEAD-BRANCH `fix/freeze-genesis-seed`, unpushed | yes |
| insa | NO-REMOTE | n/a |
| erlmcp | AHEAD-BRANCH `otp27/ssl-followups`, unpushed | yes |
| cre | AHEAD-BRANCH `otp27/ssl-hardening`, unpushed | yes |
| chicago-tdd-tools | SYNCED (dirty) | n/a |
| mcp-mqtt-erl | BLOCKED (403, no push rights to emqx fork) | no |
| ggen-ecosystem | SYNCED | n/a |
| knhk | DIVERGED (431 ahead / 585 behind) | no |

### 5.2 Integration debt (L102) — current standing

1. **knhk** — 4,823+ dirty files plus 431/585 divergence. Still
   user-blocked: merge awaits user direction; not committable cleanly
   until a rebase-or-merge decision is made.
2. **beam4pm** — 615 dirty files (610 receipts/engine_ops). RESOLVED:
   bulk-committed and pushed as `a6f3a212`
   ("chore(receipts): commit engine_ops evidence trail from the
   2026-10-13 wave (L102 debt #2)"). `origin/main` == `a6f3a212`,
   ahead 0 / behind 0 at write time.
3. **ggen-marketplace (this repo)** — strata pack edits + insa-law-pack
   + RECEIPT-INDEX. RESOLVED: committed in `52feb96f1` (insa-law-pack),
   `0c7c9e594` (sabotage corpus + consensus u128), `8f98a4c49` (valve
   WindowCapacityRefusal), `eb697b8a2` (receipt-index). Residual:
   strata-cas/ledger generated files still dirty; push not executed
   by this lane.

### 5.3 Standing table updates (SHA re-read from git log)

| item | old standing | new standing |
|---|---|---|
| beam4pm engine_ops receipt corpus | uncommitted (debt #2) | committed + pushed `a6f3a212` |
| consensus u128 work accumulator | open lane | ALIVE `0c7c9e594` |
| sabotage-corpus totality court | open lane | ALIVE `0c7c9e594` |
| valve WindowCapacityRefusal family | open lane | ALIVE `8f98a4c49` (L86) |
| insa-law-pack eight-vow typestate | untracked | ALIVE `52feb96f1` (L84) |
| receipt-index row for this receipt | missing | landed `eb697b8a2` (L98) |
| strata ledger GALL projection | unpushed commit | still `457c3b338` (now tip-adjacent) |

Standing is as-of 2026-10-13 evening; re-verify before citing as
current.

---

**Receipt identity**: written 2026-10-13 by lane L75 (docs) from read-only
`git log` across 10 repos. SHAs re-read at write time. Standing is
as-of this receipt; re-verify before citing as current.

## 6. Closing state — 2026-10-14 (post-wave-9)

Written read-only by lane L202 from `git branch -vv` / `git status -sb`
per repo, re-derived 2026-10-14. SHAs as observed at write time.

### 6.1 Final fleet push-state

| repo | branch | local vs origin | head |
|---|---|---|---|
| castle | main | ahead 12 (push not landed) | `f8f94f7` |
| mfact | main | synced | `0e4c1cb68b` |
| graphlaw | main | synced | `7bfe411` |
| ash_a2a | main | synced | `f71b4d0e` |
| beam4pm | main | synced (engine_ops corpus pushed `a6f3a212`) | `5fe8daa2` |
| affidavit | fix/freeze-genesis-seed | unpushed branch (main synced `eed7c40`) | `50879a8` |
| erlmcp | main | synced `e4d00431`; work on `otp27/ssl-followups` | `070f744d` |
| erlmcp | otp27/ssl-followups | unpushed branch | `070f744d` |
| cre | master | synced `9c69220c`; work on `otp27/ssl-hardening` | `fe3db7b6` |
| cre | otp27/ssl-hardening | unpushed branch | `fe3db7b6` |
| chicago-tdd-tools | main | synced | `f455b1b` |
| ggen-ecosystem | main | synced | `1c67bf0b` |
| insa | main | NO-REMOTE (local-only) | `6986dd6` |
| mcp-mqtt-erl | main | ahead 5; push 403 (patches exported) | `62c0ce3` |
| knhk | main | DIVERGED 431 ahead / 585 behind | `30745c8e` |
| wasm4pm | main | ahead 72; push BLOCKED (transport) | `57fcd9bd` |
| ggen | main | ahead 1 (Tera fix `01c8d5fb` still local) | `01c8d5fb` |
| ggen-marketplace | main | synced `618bb415` | `618bb415` |

### 6.2 Final counts (re-run / re-read at write time)

- marketplace validate: `packs=326 manifests=326 ontologies=541
  templates=1873 native_gates=1914 verifier_gates=21` (exit 0).
- 326 packs confirmed; both wave packs indexed (PACK-INDEX `d026b64e4`).
- Witnessed KATs: every major law carries a known-answer test —
  store (content-address), consensus (u128 work-sum), hash/temprun
  + constitution 17 constants (`1a7741b2a`).
- Sabotage twins: ledger last receipted 13/16 (`e1ee25fa2`); brief's
  14/16 not re-derived — re-verify before citing.
- Lean witnesses: 6 (mfact theorem corpus incl. MerkleCompleteness
  `0e4c1cb68b`).
- Cross-runtime crosswalks: erlmcp <-> ash_a2a <-> strata-valve with
  A2A wire column (L142/L152 differential court, graphlaw `7bfe411`).
- Standing fleet KATs landed across strata/insa/valve packs
  (waves 8-9, `1a7741b2a`, `618bb415`).

### 6.3 Structural additions this session

- **insa-law-pack** — eight-vow typestate (`52feb96f1`).
- **refusal-vocabulary-pack** — 3 crosswalk columns.
- **fork-choice arbiter** — divergent-head selection.
- **lean-witness pipeline** — producer -> castle Replayed.
- **DETS task store** — erlmcp durable task surface.
- **conformance runner** — one command -> verdict report.
- **gate-engine differential court** — two engines must agree
  (graphlaw `7bfe411`).

### 6.4 Still-open ledger

1. knhk merge — user-blocked (431/585 divergence unchanged).
2. castle / wasm4pm pushes — transport-blocked.
3. sa2a receipt re-cut — pin bump pending.
4. AIRo de-orphaning — R2 open.
5. temprun fuel <-> rate-limit composition — design.
6. castle negative-evidence channel — design.
7. erlmcp ~250 never-implemented API tests — build-out.
8. TCK baseline — unchanged at 79%.

---

**Receipt identity (section 6)**: lane L202 (docs), 2026-10-14,
read-only re-derivation. Re-verify push-state before citing as
current.
