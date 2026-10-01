# durability-capability-pack

THE qualified capability-contract pack for the **durability / replay / resume** family
(v26.9.30 capability-ecology wave, lane 5). Admits capability contracts as semantic
requirements — never implementations — for the `ash_pplan` v26.9.30
capability-resolution engine to resolve `AshPPlan.Provider` candidates against.

- Namespace: `dcap:` = `https://ggen.dev/ontology/durability-capability#` (wave-pinned, `docs/jira/v26.9.30/RESOLUTIONS.md`).
- Version: 0.1.0. Grants **no execution authority**: capability ≠ realization ≠ qualified ≠ actuated.
- Realization ground truth: every `dcap:inspected true` fact below was read from the
  real source this wave (2026-09-30); `dcap:inspected false` facts are hex-coordinate
  citations and say so.

## Capabilities (pinned IDs via `rdfs:label`, joined by `dcterms:identifier`)

| dotted ID | pinned | requires (properties) | requires (evidence) | outcomes | compensatable / reversible |
|---|---|---|---|---|---|
| `Durability.Checkpoint` | yes | durable, checkpointed | checkpoint_receipt | ALIVE, REFUSED_SUBJECT_MISMATCH | true / false |
| `Durability.Replay` | yes | deterministic | replay_receipt | ALIVE, REFUSED_DIGEST_MISMATCH | false / false |
| `Durability.Resume` | yes | resumable | continuation | ALIVE, REFUSED_VERSION_BOUNDARY, REQUALIFIED | true / false |
| `Workflow.Halt` | yes | durable, checkpointed | checkpoint_receipt | ALIVE, REFUSED_NO_AUTHORITY | true / false |
| `Workflow.Resume` | yes | resumable, isolated | admit_receipt | ALIVE, REFUSED_NO_AUTHORITY, REQUALIFIED | true / false |
| `Durability.Continuation` | minted sibling | durable, resumable | continuation | ALIVE, REFUSED_NO_CONTINUATION | true / false |
| `Workflow.Compensate` | minted sibling | idempotent, isolated | idempotency_receipt | ALIVE, REFUSED_COMPENSATION_INCOMPLETE | false / false |

Minted siblings are grounded, not decorative: `Durability.Continuation` names the
capture/restore pair (`AshPPlan.Continuation.capture/5` + `resume/4`; the evidence
atom `:continuation` is literally what `AshPPlan.Providers.Durability` declares);
`Workflow.Compensate` exists so the `COMPENSATABLE` flag every capability declares has
a capability that realizes it. No lane mints IDs in another family's namespace.

## Deep semantics encoded

- **Checkpoint identity is content identity.** A `dcap:Checkpoint` binds to its
  `dcap:WorkflowSubject` via `dcap:boundSubject` + a **`qce:closureDigest`** (64-hex
  state digest — COMPOSED from `qualified-capability-ecology`, not redefined) plus a
  40-hex `dcap:baseSha` and canonical urn identity. Mirrors `Xaas.Gall.Checkpoint`
  (content-addressed `graph_digest`, `:refused_subject_mismatch` refusal vocabulary)
  and `Xaas.Gall.CheckpointBinding.matches_checkpoint?/2` (stale-content
  falsification) — both opened in `~/xaas` this wave.
- **Replay determinism is the exact-SHA discipline.** A `Durability.Replay`
  realization must carry a `dcap:DeterminismContract`:
  `byteIdenticalRequired true`, evidence kind `replay_receipt`, receipt class
  **`qce:ReplayReceipt`** (composed). Receipt instances are runtime facts
  (`qualification/fixtures` exercises them with clearly-synthetic digests); a
  fabricated digest inside the pack graph would be fabricated evidence, so the pack
  graph carries only the contract.
- **Resume across a projection-version boundary has exactly two lawful endings**:
  the typed refusal `REFUSED_VERSION_BOUNDARY`, or `REQUALIFIED` with a real
  `qce:QualificationReceipt` carrying `qce:qualificationDigest`. A silent continue
  ("ALIVE" across a boundary) is refused by gate 050. Both lawful outcomes are in the
  positive fixture; the negative fixture is the unmodeled third option.
- **Halt/resume with a human-approval gap.** `Workflow.Halt` is declared
  `suspendsAuthority true`: from `haltedAt` until a conforming resume, NO execution
  authority exists (ProviderAvailable ≠ Authorized). `Workflow.Resume` must re-bind
  FRESH authority: `dcap:authorityEnvelope` → `qce:AuthorityEnvelope` with its own
  `qce:authorityDigest` (gate 060). Grounded: `Xaas.Sa2a.Execution` re-derives
  authority per execution (single exact-subject system actor behind a deny-by-default
  floor); `AshPPlan.Providers.Steps.Checkpoint` implements the halt/resume pair as
  one module's two paths.
- **Idempotency keys.** `dcap:IdempotencyContract` with the real formula
  `sha256(work_order_digest|query|plan_hash)` and its uniqueness scope
  (`sa2a_executions.idempotency_key`, a unique identity) — from
  `Xaas.Sa2a.Execution`, opened.
- **COMPENSATABLE ≠ REVERSIBLE** as distinct typed properties: every capability
  independently declares `dcap:compensatable` AND `dcap:reversible` (gate 010
  refuses a capability that omits either — neither may be defaulted).
  `UNKNOWN ≠ REVERSIBLE`: unproven restoration is declared `false`.
- **Invariants carried, not restated**: Plan ≠ Execution (`Xaas.Ultracode.RecoveryPolicy`
  selects under an ash_pplan-admitted FOND policy while dispatch flows through the
  lease kernel); Policy ≠ Authority (same module: "Authority: selecting the next tick
  is SELECT over admitted structure... carries no actuation authority");
  ProviderAvailable ≠ Authorized (gate 060 + `qual-sa2a-execution-authority`);
  Projection ≠ Source (`capturedProjectionVersion` vs `projectionVersion` is exactly
  the drift gate 050 polices); Generated ≠ Admitted (`qual-fond-replay-bundle`: a
  replay bundle is evidence input for a court, not proof the court executed).

## Realizations (provider metadata only; never the capability identity)

| realization | realizes | provider | inspected | pin policy |
|---|---|---|---|---|
| `Xaas.Gall.Checkpoint` | Checkpoint | `xaas` `lib/xaas/gall/checkpoint.ex` | true | repo HEAD at admission |
| `Xaas.Sjira.Checkpoint` | Checkpoint | `xaas` `lib/xaas/sjira/checkpoint.ex` | true | repo HEAD at admission |
| `AshPPlan.Providers.Steps.Checkpoint` | Checkpoint, Halt | `ash_pplan` `lib/ash_pplan/providers/steps/checkpoint.ex` | true | path dep |
| `Xaas.Sa2a.Bridge` (replay/2) | Replay | `xaas` `lib/xaas/sa2a/bridge.ex` | true | repo HEAD at admission |
| `Xaas.Fabric.Capability` (replay/2 callback) | Replay | `xaas` `lib/xaas/fabric/capability.ex` | true | repo HEAD at admission |
| `AshPPlan.FOND.Replay` | Replay | `ash_pplan` `lib/ash_pplan/fond/replay.ex` | true | path dep |
| `Xaas.Gall.CheckpointBinding` | Resume | `xaas` `lib/xaas/gall/checkpoint_binding.ex` | true | repo HEAD at admission |
| `AshPPlan.Providers.Durability` | Resume, Continuation, Workflow.Resume | `ash_pplan` `lib/ash_pplan/providers/durability.ex` | true | path dep |
| `Xaas.Sa2a.Execution` | Workflow.Resume | `xaas` `lib/xaas/sa2a/execution.ex` | true | repo HEAD at admission |
| `Reactor` step undo/compensation | Compensate | `hex:reactor` (NO local checkout) | **false** | hex coordinate |

Every realization carries ≥1 `dcap:QualificationCondition` (gate 070) — including
`qual-reactor-undo-uninspected`, which records the hex-only grounding as UNSUPPORTED
this wave and names the flip condition (open the source, set `inspected true`).

## Gates and their witnessed refusals (anti-vacuity)

`qualification/verify.py` is the deterministic court: the pack graph AND the positive
fixture must be gate-clean; each negative fixture must fire EXACTLY its declared
gates. Run: `python3.11 packs/durability-capability-pack/qualification/verify.py`
(exit 0 = ALIVE; last stdout line is a JSON standing payload).

| gate | refuses | firing negative fixture (`qualification/fixtures/`) |
|---|---|---|
| `010_required.rq` | missing identity/property completeness; out-of-enum `resumeOutcome` | `negative-missing-required-fields.ttl`, `negative-resume-outcome-enum.ttl` |
| `020_capability_without_realization.rq` | capability no realization realizes | `negative-capability-without-realization.ttl` (and `negative-missing-required-fields.ttl`) |
| `030_checkpoint_without_subject_digest.rq` | checkpoint without bound subject + 64-hex `qce:closureDigest` | `negative-checkpoint-without-subject-digest.ttl` |
| `040_replay_without_determinism_evidence.rq` | `Durability.Replay` realization without a byte-identical `DeterminismContract` naming `qce:ReplayReceipt` | `negative-replay-without-determinism-evidence.ttl` |
| `050_resume_across_version_without_requalification.rq` | version-boundary crossing without typed refusal or receipted requalification | `negative-resume-version-boundary.ttl` |
| `060_authority_gap_unmodeled_on_halt.rq` | resume across a halt gap without a fresh `qce:AuthorityEnvelope` + `qce:authorityDigest` | `negative-authority-gap.ttl` |
| `070_realization_without_qualification_conditions.rq` | realization with zero qualification conditions | `negative-realization-without-qualification.ttl` |

Pytest wiring: `tests/test_durability_capability_pack.py` (court subprocess, per-fixture
exactness, adversarial in-memory mutations).

## Failed edges (custom terms vs the public set — recorded, none silent)

1. **`dcap:Capability` / `dcap:Realization` classes** — public `prov:` has
   Entity/Activity but cannot type the semantic-requirement-vs-implementation
   distinction or its authority discipline; `qce:` types the qualification lifecycle
   of one capability version, not the requirement/realization split. Failed edge:
   modeling realizations as bare `prov:Entity` loses the `realizes` direction the
   resolver joins on.
2. **`qce:closureDigest` / `qce:ReplayReceipt` / `qce:QualificationReceipt` /
   `qce:AuthorityEnvelope` REUSED, not redefined** — composition per the wave
   resolutions; no custom digest/receipt vocabulary was minted. (Positive reuse
   note, recorded to show the alternative was taken, not silently pruned.)
3. **`dcap:resumeOutcome` as closed-string enum** instead of `aps:` standing IRIs —
   `https://w3id.org/chatman/aps#` carries standing-level individuals (ALIVE,
   PARTIAL_ALIVE, REFUSED_*…), but `REFUSED_VERSION_BOUNDARY` / `REQUALIFIED` are
   capability-fine-grained outcomes with no aps individual, and the ecosystem's own
   typed-refusal vocabulary is string/atom-shaped (`Xaas.Gall.Checkpoint`
   `refusal_reasons/0`). Mapping documented on the property (`ALIVE` → aps:ALIVE);
   minting cross-family standing individuals was refused.
4. **Execution properties and evidence kinds as `skos:Concept`** (public), with
   `skos:prefLabel` values aligned to the consumer's atoms (`durable`, `resumable`,
   `checkpointed`, `continuation`, …). A custom `dcap:Property` class failed against
   skos: it would add nothing the concept scheme lacks.
5. **`dcap:compensatable`/`dcap:reversible` as plain xsd:boolean pairs** — OWL
   cardinality/keys were considered and failed the gate use case: SPARQL gates query
   stated triples; inferenced closures would weaken the "both must be STATED" law.

## Verification

```bash
python3.11 scripts/marketplace.py check durability-capability-pack   # real ggen, scoped
python3.11 packs/durability-capability-pack/qualification/verify.py  # anti-vacuity court
python3.11 -m pytest tests/test_durability_capability_pack.py        # pytest wiring
```

Consumption (planned, `ash_pplan` v26.9.30): the capability catalog here is static
pack fact; `Checkpoint` / `HaltClaim` / `ResumeClaim` / receipts are runtime
individuals the resolver and its providers mint and gate against.
