# WAVE-RECEIPT — v26.9.18 ggen-maximization wave, MARKETPLACE INTEGRATION (pack/wave-26918-integration)

Date: 2026-09-18/19 (integration session). Law: ~/.zcode/AGENTS.md (DfCM).
Scope: integrate the 5 agent branches of the ggen maximization wave (4
marketplace-side lineages + 1 igniter branch) into ONE merged pack branch,
prove it marketplace-side and consumer-side. Every claim below is an observed
execution this session. NO push — landing is the tree owners' (see Remaining).

## Standing

**ALIVE** for the merged marketplace branch as an integration artifact: observed
merges (4 × --no-ff, parents verified), pack gate sweep 16/16 PASS, planted
falsifiers fire, isolated qualification render exit 0, consumer render byte-proven,
family tests green against real engines.
**PARTIAL_ALIVE** for the consumer harness as a whole: the Tera leg (the leg that
renders the three wave families) is green; the igniter leg is **BLOCKED by
main's own pre-existing `--warnings-as-errors` debt**, empirically proven NOT
wave-introduced (details + repro below). The wave-introduced warnings that the
leg's strict compile surfaced were real pack template defects — fixed at
`825bd3aaa` and re-proven.

## Branch + SHAs

Base: marketplace main @ `800b8c6c5`. Branch: `pack/wave-26918-integration`
(worktree /Users/sac/ggen-marketplace-wt/integration).

| # | commit | content |
|---|---|---|
| 1 | `e795e88b787d1f989c8fc65a57460e97f36e6655` | merge --no-ff: G5 vendored defect-fix line `fix/hand-authored-manifest-templates-force-overwrite` @ `6750aa19f` (fetched from the wt-g5 submodule clone; base 7abe147e1 already in main) — ceilings 35→50 / 6→7 (f2ae5382e), force:true on hand-authored manifest templates (6a30fad72), GENERATED marker in JSON schema first 3 lines (0809e8f95), force:true on all four wasm-engine templates (6750aa19f). Resolution: pack.toml 0.1.19 → 0.1.20 with ONE dated ceiling-lineage paragraph |
| 2 | `09106da845833ea66a8ed9c7fd358f37e3198181` | merge --no-ff: G1 `pack/cli-bridge` @ `e6cec92af` — bpm:CliBridge family + template + gates 100/110 + consumer fixture block. pack.toml → 0.1.21 |
| 3 | `a77f4cd65d7bb91f6a86c51216203135c90e67bc` | merge --no-ff: G2 `pack/parity-qualification` @ `b17801f8e` — bpm:ParityCheck family + test template + gates + fixture block. pack.toml → 0.1.22 |
| 4 | `0808a55db9837280addf322889de941717505fba` | merge --no-ff: G3 `pack/port-bridge` @ `3d5009a70` — bpm:PortBridge family + lib/test templates + gate + echo fixture. pack.toml → 0.1.23 |
| 5 | `825bd3aaa` | fix(beam4pm-process-model-pack): port-bridge render defects the consumer's strict compile caught (0.1.23 follow-up) — see "Integration-time defect fix" |

Final head: see `git rev-parse pack/wave-26918-integration` after the receipt
commit (receipt commit is append-only docs).

## Version sequence table (the requested linearization)

| version | family / lineage | paragraph provenance |
|---|---|---|
| 0.1.19 | main baseline (v0.1.17 newest paragraph) | — |
| 0.1.20 | ceiling raise + manifest defect-fix lineage (G5) | paragraph AUTHORED at integration (house style, one dated paragraph) |
| 0.1.21 | bpm:CliBridge one-shot CLI bridge wrappers (G1) | G1's v0.1.20 paragraph, prefix renumbered only |
| 0.1.22 | bpm:ParityCheck cross-engine parity qualification (G2) | G2's v0.1.20 paragraph, prefix renumbered + gate refs updated |
| 0.1.23 | bpm:PortBridge persistent JSON-lines port-bridge clients (G3) | G3's v0.1.20 paragraph, prefix renumbered + gate ref updated |

All three agents had shipped `version = "0.1.20"` independently.

## Conflict resolutions

1. **pack.toml** (conflicted at merges 2–4): linear version sequence above.
   Description increments collapsed to ONE dated changelog paragraph per family,
   appended in house style. G1/G2/G3 paragraph text preserved verbatim except the
   `v0.1.20 (2026-09-18):` prefix and in-paragraph gate-filename references
   (updated to the renumbered gates). TOML validated with a tomllib-capable
   python at every step.
2. **ontology.ttl**: the ceiling splices carried by G1/G2/G3 (their cherry-picks
   of the reviewed raise) are TEXTUALLY IDENTICAL to G5's f2ae5382e — git merged
   them to ONE ceiling state. Verified post-merge: `bpm:debtCeiling 50` ×1,
   `bpm:debtCeiling 7` ×1, `35`/`6` absent, `44 -> 50` doc present ×1. The three
   family blocks appended at EOF conflicted (all-append-at-same-position) —
   resolved as union in merge order CliBridge → ParityCheck → PortBridge; no
   line authored.
3. **gates/**: main ships 010–090. G1 kept its 100/110 (next free slots). G2's
   100/110/120 renumbered → **120/130/140**; G3's 100 renumbered → **150**.
   Content byte-preserved (`git mv` only). Re-proven after renumbering (below).
4. **qualification/consumer.ttl**: three synthetic fixture blocks appended at EOF
   — union resolution, plus G2's in-block comment gate refs updated to
   gates/120/130/140.
5. **WAVE-RECEIPT.md** add/add collisions: agent receipts preserved as
   `WAVE-RECEIPT-g1.md` / `-g2.md` / `-g3.md`; the root path is this
   integration receipt.
6. No other file-level collisions (templates, echo fixture, python fixture all
   disjoint adds).

## Integration-time defect fix (825bd3aaa)

The consumer harness's strict compile (`--warnings-as-errors`) surfaced two
defects in G3's `beam4pm_port_bridge.ex.tmpl`:
- `port_command(root)`: the no-checkout-root arm never uses `root` → template
  now emits `defp port_command(_root)` in that arm (warning: unused variable).
- `dispatch_reply/2`: the `{head, rest} ->` clause head matched BOTH
  `:queue.out/1` result shapes, so the `{:empty, _}` arm was DEAD CODE and an
  unsolicited bridge line with empty waiters would raise MatchError instead of
  logging — a real latent bug, caught by "this clause cannot match" warning.
  Clause head is now `{ {:value, {from, timer_ref}}, rest} ->` (single leading
  space: `{{` would open a Tera expression — first edit attempt broke Tera
  parsing, FM-TPL-017, falsified and corrected within the commit).

Fix is template-side (the pack owns the mutation); rendered files are
consequences and were re-rendered.

## Marketplace gates (observed this session)

| gate | command (tree = integration worktree) | exit | evidence |
|---|---|---|---|
| Pack gate sweep | all 16 `gates/*.rq` via pyoxigraph (python3.13) over the merged graph ontology.ttl + qualification/consumer.ttl | 0 rows each, ALL PASS | re-run after 825bd3aaa, still ALL PASS |
| Gate falsifiers | in-memory plants: BridgeOp w/o replyShape → gate 150 = 4 rows; un-admitted ParityCorpus (full `a ParityCheck; checkName; hasCorpus → corpusPath` shape) → gate 120 = 1 row; CliCommand w/o bridge → gate 100 = 8 rows | all refuse | 2 naive wrong-shape plants correctly did NOT fire first (gate joins are specific) — recorded |
| Isolated qualification render | scratch project /tmp/gint-pack-qualify: ggen.toml → integration worktree pack path, `consumer.ttl` (the pack's merged fixture graph) as `[ontology].source`; `ggen sync run` | 0 | renders the full pack surface incl. all three families; receipt standing Green; closure binds all 16 gate hashes |
| Rendered-artifact compile | `elixirc` (1.20.3-otp-28) on the isolated renders: beam4pm_cli_frobnicate.ex, beam4pm_echo_bridge.ex, echo test | 0 | **0 warnings** post-fix (2 template warnings before the fix — the falsifier that found them) |
| Shell | only shell file on any proof path: priv/bin/autofde trampoline → `bash -n` OK; marketplace branch changed NO .sh files | 0 | echo_port_bridge.py → py_compile OK |
| TTL sanity | pyoxigraph parsed ontology.ttl + consumer.ttl (load errors would abort the sweep) | 0 | plus tomllib parse of pack.toml |

## Consumer proof (worktree /Users/sac/beam4pm-worktrees/wt-gint, branch scratch/gint)

Setup: worktree from beam4pm main @ `27ff280`; submodule vendor/ggen-marketplace
fetched from ~/ggen-marketplace and checked out at THIS wave branch
(`825bd3aaa`, local branch wave-26918-integration); **ggen.toml unedited** (main
already wires the process-model pack via the submodule). Proof state committed
on scratch/gint @ `a43f6b1` (clearly marked NOT-the-cutover) so the proof is
inspectable; nothing pushed.

Uncommitted-by-convention consumer edits (lifted verbatim from the agents'
proof trees):
- ontology.ttl admissions: wt-g1-proof's autofde CliBridge + witnesses (140 l),
  wt-g2-proof's ferroplan-vs-lab ParityCheck + fixture admissions (78 l),
  wt-g3-proof's echo PortBridge (96 l) with the fixture path re-pointed from the
  g3 worktree to `vendor/ggen-marketplace/.../qualification/echo_port_bridge.py`.
- qualification/fixtures/dfcm/{dfcm.hddl,dfcm-abcx.hddl}: sha256 match the
  admitted pins exactly (0060c0e6…, b337e94f…).
- priv/bin/autofde trampoline (bash -n OK) from wt-g1-proof.

| # | command (tree = wt-gint) | exit | evidence |
|---|---|---|---|
| 1 | `ggen sync run` (Tera leg) | 0 | first run correctly refused FM-PACK-008 (lock pins pre-merge pack) → prescribed re-lock taken; re-run exit 0, receipt standing_ceiling Green. Renders: lib/beam4pm_cli_autofde.ex (208 l, **sha256 ee0fa5cd… — byte-identical to G1's receipted render**), lib/beam4pm_echo_bridge.ex (387 l), test/beam4pm_echo_bridge_test.exs (139 l), test/beam4pm_parity_ferroplan_hddl_solve_vs_lab_fabric_solve_test.exs (268 l, matches G2's receipted 268), docs/reference/beam4pm_hand_authored_source.md re-rendered with ceiling **50** (the force:true fix proven end-to-end over the drifted copy) |
| 2 | `mix test test/beam4pm_echo_bridge_test.exs` | 0 | **8 tests, 0 failures** — incl. real kill -9 (status 137) of the interpreter + lazy-restart recovery |
| 3 | `AUTOFDE_LAB_ROOT=$HOME/autofde-lab mix test test/beam4pm_parity_ferroplan_hddl_solve_vs_lab_fabric_solve_test.exs` | 0 | **4 tests, 0 failures, NO skips** — real `autofde fabric solve` (venv) vs real `BeamPM.Ferroplan.hddl_solve` over wasm e90928d (built this session: `git submodule update --init --recursive native/ferroplan` + scripts/ferroplan_wasm_build.sh, exit 0); first run honestly 4/4 SKIPPED until the wasm was built |
| 4 | CLI bridge resolution-ladder suite (`mix run -e`): real fabric_cache_stats run → env-rung missing-binary typed refusal → default-rung restore → real run again | 0 | ALL GREEN (real lab counters observed: entries 9, hits 42, hit_rate 0.7) |
| 5 | `mix compile` | 0 | 2 warnings total, both in main's own pre-existing files (see below); 0 from any wave-rendered file |
| 6 | igniter leg: `source scripts/env/rust4pm_reactor_env.sh && bash scripts/igniter_sync.sh` | 1 (BLOCKED, pre-existing) | run 1 failed on the TWO WAVE-INTRODUCED port-bridge warnings → fixed at 825bd3aaa. Runs 2–3 fail at the task's terminal `:verify` step (`mix compile --warnings-as-errors`) on **main's own** warnings: lib/beam4pm_dfcm.ex:179 (AshAutofde.CascadeAllocator undefined-if-not-loaded) and lib/mix/tasks/eds.ledger.ex:1 (module redefinition vs dep ash_a2a). Empirical pre-existence proof: both files byte-identical to main @ 27ff280 (git status empty); `touch` them alone + `mix compile --warnings-as-errors` → fails with exactly those two warnings, zero wave files involved. The igniter sync's own renders force an app recompile every run, so this is deterministic on any tree carrying those warnings. NOT wave-introduced; fix belongs to the tree owner (see Remaining) |

Ports 4341/4342: verified free; unreferenced by this wave's tests/fixtures.

## Igniter side (G4) — no integration needed

`feat/hand-authored-admit-task` @ `9858ac0` (~/ggen_igniter-wt/g4): committed,
clean tree, base = ggen_igniter main @ `15305ce`. Standalone
(ggen_igniter.hand_authored admit/list/check task). Lands via its own ticket's
procedure; unaffected by the igniter-leg BLOCK above (that debt is in beam4pm,
not ggen_igniter).

## 比

- Wave content delivered by the merged branch: 2,439 pack insertions + 369
  receipt lines — all agent/pack-manufactured per the per-agent receipts
  (G1/G2/G3 facts+templates+gates+fixtures; G5 reviewed fix line).
- Integration-session hand-writing: ONE dated changelog paragraph in pack.toml
  (1 physical line, authored), the two-line dispatch_reply clause-head fix and
  the conditional port_command head inside G3's template (the 825bd3aaa defect
  fix, template-side), gate/receipt renames + block unions (mechanical, zero
  authored lines), commit messages, and this receipt. Zero hand-written lines on
  any rendered or consumer-runtime artifact: every rendered file is ggen output
  (the cli bridge is byte-identical to the agent's receipted render —
  determinism proven, not asserted).
- Consumer proof tree: admissions = verbatim agent-authored instance data
  (314 lines); renders = ggen output; fixtures = copies with digest pins
  verified.

## Remaining / landing steps (tree owners — NOTHING pushed)

**Marketplace (operator):**
1. Review + push `pack/wave-26918-integration` (head = receipt commit) to the
   marketplace origin; land via the marketplace's own PR/fast-forward law.
2. After push, the G5 lineage
   (`fix/hand-authored-manifest-templates-force-overwrite` @ `6750aa19f`) becomes
   reachable from origin; the fix commits are contained in the merge, so the
   worktree-only branch can be retired.

**beam4pm (tree owner):**
1. Land the parity wave integration per WAVE-RECEIPT §Landing of
   `parity/integration` @ `70e2662` (stash-in-flight → `git merge --no-ff
   parity/integration` → gates → restore), with ONE change: step 2's vendored
   pack checkout lands THIS branch (`pack/wave-26918-integration` @ 825bd3aaa,
   supersedes f2ae5382e — it contains it as an ancestor) instead of the bare
   fix branch, then commit the submodule gitlink bump.
2. Land `chore/ggen-consumption-max` @ `35f6c73` (G5's beam4pm branch; verified
   fast-forward descendant of main @ `27ff280`).
3. Consumer cutover (retires the wave's hand-written class): admit the three
   families' instances for real (source blocks: scratch/gint @ `a43f6b1` and the
   agents' proof worktrees wt-g1/wt-g2/wt-g3-proof), commit the fixtures +
   re-lock, re-run gates + the three family suites. The parity-class ceiling
   headroom warning from G5 applies: parity merges land AT the 50/7 ceilings.
4. NEW TRIPWIRE (pre-existing, needs its own ticket): any fresh-tree run of
   `scripts/igniter_sync.sh` / any `mix ggen_igniter.sync` (terminal
   `:verify = mix compile --warnings-as-errors`) fails on main's own
   lib/beam4pm_dfcm.ex:179 + lib/mix/tasks/eds.ledger.ex:1 warnings; repro in
   the consumer-proof table row 6. Fix = silence the two warnings lawfully
   (admit or restructure) or pin the harness's verify policy; until then the
   igniter leg is BLOCKED on any freshly-built tree.

## Falsifiers attempted

- First consumer sync expectedly refused FM-PACK-008 (lock hash mismatch) —
  prescribed re-lock taken, not bypassed.
- Port-bridge template falsified by the strict consumer compile (build_broken);
  first fix attempt itself falsified by FM-TPL-017 (Tera `{{` parse) and
  corrected inside the same commit; re-proven (gates, isolated render, elixirc
  0 warnings, consumer suites).
- Parity suite honestly observed 4/4 SKIPPED before the wasm was built; built
  the wasm, re-ran, 4/0 no skips — the named-skip path itself witnessed working.
- Gate-join specificity probed: 2 wrong-shape plants (no fire) then 3
  correct-shape plants (all fire) on gates 100/120/150.
- Determinism falsified by byte-comparison: re-render sha256 == G1's receipted
  sha256 (ee0fa5cd…).

## What the operator did NOT have to write

All four merges + conflict unions, the gate renumbering, the template defect
fix, the pack paragraph, every rendered line in the proof tree (1,002 lines of
family artifacts + manifest/docs), and both proof commits.
