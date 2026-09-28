# WAVE-RECEIPT — G2, parity-qualification pack (beam4pm-process-model-pack v0.1.20)

Date: 2026-09-18/19. Agent: G2 (ggen maximization wave). Law: ~/.zcode/AGENTS.md (DfCM).

## Standing

BLOCKED -> **ALIVE** (observed renders + green runs, this session, exact subjects below).

## What shipped (pack authorship, 法面)

Branch `pack/parity-qualification` @ `~/ggen-marketplace-wt/g2`, on top of `800b8c6c5`:

- `packs/beam4pm-process-model-pack/pack.toml` — version 0.1.19 -> **0.1.20**, dated v0.1.20 description increment appended.
- `packs/beam4pm-process-model-pack/ontology.ttl` — new vocabulary: `bpm:ParityCheck` (checkName/checkDoc/checkOrdinal/testPath/testModule, leftCommand+rightCommand as human-witnessed strings, leftDomain/leftSolver, consentLaw, tamperFalsifier + tamperFind/tamperReplace/tamperCorpusOrder), `bpm:ParityCorpus` (corpusPath/corpusSha256/corpusOrder), `bpm:ParityDigestPin` (pinKey/pinValue — the P10 flip-ledger rows), `bpm:ParityExpectedStep` (stepOrder/stepAction — the SHARED verdict ladder = the parity contract), `bpm:QualificationFixture` (fixturePath/fixtureSha256/fixtureDoc — graph-level existence), closed `bpm:ParityCommandKind` (lab_fabric_solve, beam_hddl_solve). ALSO: the integration wave's ceiling splice (hand_authored_qualification 35 -> 50, native_engine_facade 6 -> 7) applied text-identical to `fix/hand-authored-qualification-ceiling-35-wave-26918` @ f2ae5382e — gate 070 refused the proof sync (36 > 35) and the remediation is the pack-side ceiling, so the same edit lands here; merge with integration is text-identical.
- `packs/beam4pm-process-model-pack/templates/beam4pm_parity_check_test.exs.tmpl` — Tera, `for_each: parity_checks`, output path from `bpm:testPath`, per-check fan-out with `filter(attribute="check_name", ...)`: corpus exists-on-disk + sha256 pins, left-leg SOLVED + exact expected ladder + digest pins, right-leg solved + decompose/exec vocabulary covering the same ladder, tamper falsifier on a TEMP COPY. Two command-kind arms rendered conditionally; a new kind = one vocabulary member + one template arm (EngineOpKind discipline).
- `packs/beam4pm-process-model-pack/gates/100_parity_corpus_admitted.rq` — THE ticket gate: refuses any `bpm:ParityCheck` corpus entry whose `bpm:corpusPath` is not a consumer-admitted `bpm:QualificationFixture` `bpm:fixturePath` (graph-level existence).
- `packs/beam4pm-process-model-pack/gates/110_parity_check_required.rq` — refuses a check/corpus/pin/step/fixture missing any renderer-consumed field (22 UNION arms).
- `packs/beam4pm-process-model-pack/gates/120_parity_vocab_admitted.rq` — anti-joins un-admitted command kinds; refuses duplicate checkName/testPath/corpusOrder/fixturePath.
- `packs/beam4pm-process-model-pack/qualification/consumer.ttl` — one synthetic check exercising every enforced predicate (house style).

## Proof (observed, proof worktree `/Users/sac/beam4pm-worktrees/wt-g2-proof` @ 27ff280, branch scratch/g2-proof, NOTHING pushed, consumer edits uncommitted)

Environment: submodules re-pointed at local clones and init'ed (vendor/ggen-marketplace @ 7abe147, native/ferroplan @ e90928d, vendor/rust4pm-powl @ 2803959); deps fetched; ferroplan wasm artifact (sha256 69e92296...) placed at native/ferroplan/target/wasm32-wasip1/release/ (copied byte-identical from the integration worktree build of the SAME submodule pin); uncommitted `config :beam4pm, ocel_ingest_port: 4331, a2a_port: 4332`; uncommitted ggen.toml repoint of beam4pm-process-model at the g2 pack worktree; ggen.lock deleted to intentionally re-lock (FM-PACK-008 remediation).

1. Lab leg observed: `~/autofde-lab/.venv/bin/python3 -m autofde_lab.cli fabric solve HTNDomain --solver Astar --domain-arguments '{"domain_path": "qualification/fixtures/dfcm/dfcm.hddl", "problem_path": "qualification/fixtures/dfcm/dfcm-abcx.hddl"}'` (cwd = repo root), exit 0, SOLVED, 8 steps, digests DETERMINISTIC across 2 runs: input_sha256 77ac0269..., receipt_sha256 ab8521ed..., trajectory_sha256 6a74bca2...
2. Ferroplan leg observed (`mix run -e`): `BeamPM.Ferroplan.start()` then `hddl_solve(domain, problem)` -> solved true, planning_type "fond", notes ["strong FOND fixed point"], 9 policy entries = 1 htn:decompose + 8 htn:exec carrying the same 8 phases.
3. Tamper falsifier observed BEFORE authoring the facts that pin it: temp-copy rename preserve-known-options -> tampered-known-options; lab step-1 action flips, trajectory_sha256 6a74bca2 -> c569547f; ferroplan policy exec p1 flips to the tampered token. Same-corpus verdict flip witnessed by BOTH engines.
4. Rendered from facts only: consumer admits 2 `bpm:QualificationFixture` individuals + 1 `bpm:ParityCheck` individual (78 lines of instance data) -> `ggen sync run --dry-run` reported EXACTLY ONE changed output (the new test); every other template re-render byte-identical. `ggen sync run` wrote `test/beam4pm_parity_ferroplan_hddl_solve_vs_lab_fabric_solve_test.exs` (268 lines, GENERATED header).
5. GREEN: `mix test test/beam4pm_parity_ferroplan_hddl_solve_vs_lab_fabric_solve_test.exs` -> **4 tests, 0 failures**, three consecutive runs (random seeds 778805-adjacent, 518946, and one more; async false).
6. Gate refusal (the ticket's named proof): planted `bpm:parity_corpus_planted_bad_path` (qualification/fixtures/dfcm/never-admitted.hddl) linked to the check via `bpm:hasCorpus` -> `ggen sync run` exits with **FM-PACK-013, gate `100_parity_corpus_admitted.rq` refused the sync**, first row naming the planted path and subject. Plant reverted; re-sync clean (0 errors). (An ORPHANED corpus individual is correctly not a gate-100 row — the gate refuses checks whose corpusPaths are unadmitted, per ticket.)
7. Disk-level half of the two-layer existence: moving dfcm-abcx.hddl away makes the rendered corpus test fail with "corpus file missing: qualification/fixtures/dfcm/dfcm-abcx.hddl (graph admits it, disk does not)"; restored, sha256 re-matches pin b337e94f...

## Falsifiers attempted on my own output (all caught and fixed before green)

- ExUnit 255-char test-name SystemLimitError (falsifier claim as test name) -> bounded name, claim moved to comment.
- `:binary.index_of/2` undefined (OTP stdlib 6.2) -> `:binary.match/2`.
- Tamper arm `{:error, {:engine_not_started, ...}}` under random test order -> idempotent `Ferroplan.start/0` inside the tamper arm.
- SPARQL integers arrive TYPED in the Tera context (numbers, not plain strings as the 0.1.13 oxigraph note suggested for literals) -> corpus order selection via `first`/`last` instead of string-equality filter.
- FM-WRITE-005 on docs/reference/beam4pm_hand_authored_source.md: stale committed render vs new ceilings -> deleted stale copy, renderer wrote the fresh consequence.

## 比 (honest)

- The retired hand-written class costs ~213–282 imperative lines PER check (fabric 213, P2 227, P10 281).
- THIS check's delivered test file: 268 lines, 100% rendered, **0 hand-written test lines** (産面 test code 268/0 rendered/hand).
- Consumer-side cost per NEW check going forward: 78 lines of declarative admission (instance data in the consumer's own ontology — the designed consumer role), zero test code.
- One-time pack investment this wave (law-side authorship that multiplies): template 301 + gates 124 + ontology block ~107 (incl. ceiling splice) + synthetics 58 ≈ 590 lines.
- NOT counted as manufactured: the fixture copy dfcm-abcx.hddl into the proof worktree (copied from the integration branch — corpus bytes, not code); the 78 admission lines stay hand-authored instance data by design.

## Coverage honesty (template vs facts vs hand)

- TEMPLATE (shared, like the engine facades): the two command-kind arms (lab subprocess + envelope extraction, wasm call), assertion skeleton, skip-tag environment resolution, tamper mechanics.
- FACTS (per check): corpus paths + sha256 pins, receipt digest pins, expected ladder, human-witnessed commands, consent law, falsifier claim + parameters, output path + module name.
- STAYED HAND (consumer instance data): the admission of the check individual + 2 fixture individuals (78 lines). NOT yet retired: the actual P2/P5/P10 files (their legs need more command kinds — RF3Ocel run_opts, dual-corner graphlaw — before they can render from facts).

## Commands + exits (summary)

ggen sync run (render) exit 0 x4; mix test (new file) exit 0 x3 [4 tests, 0 failures each]; planted-gate ggen sync run -> exit non-zero, FM-PACK-013/gate 100; disk-falsifier mix test -> exit 2 with the named missing-file message; all raw logs referenced in session transcript.

## Remaining

- Retire P2/P5/P10 by admitting their checks (needs 2-3 more command kinds; their hand-written files stay admitted debt until then).
- The ceiling splice here and integration f2ae5382e are text-identical — whoever merges second is a no-op.
- Nothing pushed; no PR (wave law: no push).
