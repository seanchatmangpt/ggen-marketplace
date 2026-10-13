# Innovation Ledger — ERRC cross-product wave (2026-10-13, lanes X1–X20)

20 Explore lanes × ~3 candidates each (~59 total), cross-producting the
portfolio against the landed strata S1–S10 slices. Full candidate files:
/tmp/x{1..20}-innov.md. Ranked below by (leverage × grounding) — falsifiers
are the kill conditions, not implementation plans.

## Tier 1 — highest leverage, grounded in shipped code
1. **RDF-native fork states** (X2) — ledger state IS a graphlaw LawState; reorg = ancestor replay; S6 rollback machinery ELIMINATED structurally. Falsifier: heavier branch refusing under the LawState projection.
2. **Lean conservation witnesses** (X7) — mfact's proved Murata/P-invariant theorems × PN64 masks; `lake build` as a sync gate; `decide`-checkable ledger laws. Falsifier: wrong t05 mask fails admission.
3. **OCEL conformance receipts** (X4) — wasm4pm alignments × consensus behavior per block, chained conformance receipts feeding S10. Falsifier: alignment cost on S4-accepted traces.
4. **Attack-case fuzzing of S9 hardening** (X18) — mutate S10's known-attack seeds into corpus families against the S9 valve paths; sabotage-twin must discriminate. Closes S10's one open surface.
5. **Admission-time conservation pre-check** (X18) — S4 law at the S7 mempool wire boundary; eliminates block-time discovery of doomed txs.

## Tier 2 — strong, moderate integration cost
6. Constitutional-diff gate over consensus constants (X5 castle)
7. OCEL admission-chain log replacing markdown receipts (X5)
8. Config-as-chain-law + layered per-network profiles (X9 star-toml)
9. Hermetic multi-node gVisor network gym (X16 clnrm)
10. Doc-drift courts + living wiki (X15 deepwiki-rs)
11. SPARQL-queryable chain state (X10 unrdf kgc-4d)
12. Advected peer reflex / sync-as-replay (X6 insa; sub-200ns hot path)
13. Roadmap-as-spec-of-specs + consensus-law TTL (X14 spec-kit)

## Tier 3 — novel, higher integration cost
14. Actuated mempool / chain-validating reactor (X1 xaas Ash)
15. Lean fork-choice termination witness (X7)
16. POWL-script tx payloads (X4)
17.BUSL-safe unibit projections: ReceiptGate/BitFenwick/TierEscalation/ConsensusProgram (X3)
18. HTN reorg-recovery synthesis + block building (X8 koala-planner)
19. RedStrata adversarial gym / PartitionGym / ProcessMempool (X12)
20. Admitted peer reflex / attributed proposer identity (X6 insa)
21. TierLaw K8s + shared-query multi-language manufacture (X13 storehouse)
22. Lawful scaffold projection + standards upgrade protocol + release receipt chain (X20 praxis)
23. Gate-stalemate detector (X15)
24. GnoLedger / AdmissionDelta / AdmitOnCommit (X19 gno/gymact)
25. erlmcp strata-MCP server / sup-tree / evidence-reputation (X11)
26. LSP config-authoring courts (X9)
27. Plan-bound chain-state pruning (X17 oclnr)

## Dispositions
Next ticks: finish Tier-1 candidates in order (each is a bounded pack/lane
per the established pattern), re-certify, merge. This ledger is the
candidate pool; candidates die by their falsifiers, not by decree.

## Tier 1 addendum — cross-cluster seams (Y6, verified file:line)
28. **FM-CHAIN-009 shared fixture** — ~~golden fixture hand-transcribed in affidavit AND graphlaw; no shared artifact, no pin.~~ **LANDED (Y6 close-out)**: shared golden fixture committed at graphlaw `tests/fixtures/fm_chain_009.json` (sha256 `b5eccba4…`) with the affidavit pin copy matching byte-exact; cross-repo drift meta tests run in both repos (graphlaw 5 passed, affidavit 6 passed). Supersedes #37's hand-copied state.
29. **graphlaw RDFC-1.0 → wasm export** — ash_a2a's canonical_graph uses RDF.ex RDFC-1.0; graphlaw has the real RDFC-1.0 unwired (native/graphlaw_host unbuilt, test skips). Glue: wasm export + digest-equality court incl. blank-node relabelings.
30. **affidavit wasm ABI contract test** — available?/0 checks only function_exported?; never consumes abi_meta inventory/ABI version. Glue: contract test pinning assemble→verify round trip.
31. **strata↔affidavit receipt codec** — ~~strata's 3381-byte ML-DSA-65 AttestationReceipt vs affidavit's 352-byte CTRT: unrelated formats, zero cross-refs.~~ **LANDED (Seam 29 close-out)**: hash-then-commit codec landed in affidavit-core `tests/strata_refusal_seam.rs`; raw passthrough structurally refused (`ZeroCommitment`); 5 passed.
32. **sa2a vocabulary unification** — sa2a triplicated across graphlaw bins, affidavit ontology falsifiers, ash_a2a courts/state machine. Glue: one committed sa2a TTL all three consume; falsifier: receipt-not-success fires against a real standing_receipt.json.

**Cross-cutting pattern (Y6)**: every seam is a one-way hand-maintained
reference — affidavit names graphlaw/strata; ash_a2a names graphlaw/
affidavit; strata names nobody. Rigor exists within each repo, none
between them. Seams 28–32 are the loop's next finishing targets.

## Tier 1 addendum 2 — cross-cluster seams deep-dive (Y6 relaunches ×2, file:line verified)
33. **affidavit ↔ strata: STRATA context split** — affidavit's deontic.rs FR-PQC-06 uses b"STRATA:" context + refs/notes/strata-dossier + 352B WireCtrt; strata_protocol's signer uses disjoint b"strata-clap-attest-v1"; no producer/consumer of the CTRT or dossier ref exists in strata. Glue: CTRT-decoding note consumer + unified context.
34. **ash_a2a vendored wasm stale vs affidavit 26.10.6** — deps/ash_affidavit is 26.10.1, predating 352B CTRT / machine codes 0xE001–0xE402; ash_a2a receipts are plain core/v1 chains, not sovereign CTRT envelopes. Glue: re-vendor version-matched wasm.
35. **graphlaw wasm ABI duplication** — ash_a2a pins praxis_graphlaw.wasm v26.7.5 (string ABI, built from /Users/sac/praxis) while graphlaw/wasm is an unbuilt JSON-over-linear-memory ABI "for hosts such as Elixir" — two divergent ABIs, one unbuilt. Glue: build + pin + one cross-runtime parity court.
36. **Conformance vector corpora unpinned** — graphlaw/conformance/sa2a/ and ash_a2a/priv/sa2a_conformance_vectors/ are independent corpora, no shared pin or cross-runtime parity test.
37. **bcinr golden fixture hand-copied** (supersedes #28's half-done state — T10 ported the RULE; the fixture hex remains hand-copied both sides). Glue: shared committed fixture + fixture-hash meta tests both sides.
38. **strata temprun ↔ graphlaw receipt framing** — temprun Cargo.toml cites "../graphlaw precedent"; receipt_chain.rs is a verbatim bcinr-powl-receipt 26.7.28 port; temprun receipts never chained into graphlaw's framing despite shared ancestry.
39. **graphlaw ABI ↔ ggen-marketplace rust-wasi-wasmex-pack** — docs link into the pack, pack mentions graphlaw artifacts, no pinned-ABI conformance test between src/abi.rs and the rendered FFI.

**Meta-pattern (both Y6 passes)**: spec-bearing repos publish pinned
surfaces; consumers cite them in comments/manifests but link stale or
parallel artifacts. One digest-pinned artifact + one cross-language
parity court per pair closes the class.

## Landed wave receipts — 2026-10-13 (coordinator-verified SHAs)

- **Seam 28 — FM-CHAIN-009 shared fixture: LANDED.** Shared golden fixture at
  graphlaw `tests/fixtures/fm_chain_009.json` (sha256 `b5eccba4…`) + affidavit
  pin copy; cross-repo drift meta tests both repos (graphlaw 5 passed,
  affidavit 6 passed). Closes #28/#37.
- **Seam 29 — strata↔affidavit refusal-receipt codec: LANDED.**
  `affidavit-core/tests/strata_refusal_seam.rs`; hash-then-commit codec, raw
  passthrough structurally refused (`ZeroCommitment`); 5 passed. Closes #31.
- **Y8/genesis freeze: LANDED.** Affidavit seed frozen to
  `affidavit-v26.9.28-genesis`; version-independence proven by temp version
  bump. Merge `f2c9f84`.
- **T3/T4 strata-net (Tier-1 #4, #5): LANDED.** Commit `0b8c7de64` —
  admission conservation gate (typed `ConservationRefusal`, admit-time;
  4 courts + 500-entry fuzz) + 4×1000 attack-corpus fuzz, sabotage twin
  caught 498/1000.
- **T11 castle gate (Tier-2 #6): LANDED.** Commit `c5e0cf876` —
  constitutional-diff gate over consensus constants (X5).
- **Y10 ash_a2a pagination: LANDED.** ash_a2a main `13622178` — echo-of-request
  `page_size`; `historyLength` honored on `tasks/get` only. Adjacent same-class
  fix in `plug.ex` `authorize_task_list`.
- **L5 audit correction (catalog): sa2a U/V/W "empty husk" claims STALE.** All
  three packs revived to ALIVE — spark-dsl 0.2.0, chicago-court 0.2.0,
  governed-process semantic-by-design. `composition-space.ttl` refresh in
  flight (projection pending).
- **Castle integration design: PARTIAL_ALIVE by design.** Strata receipts
  ingest as O* evidence via `OcelEvent` lift; native `ReceiptV2`/
  `DurableEvidenceRecord` path BLOCKED by TrustStore + BRCE-completeness
  invariants. Implementation lane in flight.

Standing vocabulary unchanged: LANDED entries carry exact SHAs above; the
composition-space refresh and castle implementation lane are IN FLIGHT, not
admitted.

## X-lane cross-cluster seam designs — 2026-10-13 wave 2

Five completed X-lane Explore receipts (read-only, file:line verified at
time of design; construction lanes noted per entry). Same ranking
discipline: candidates die by their falsifiers, not by decree.

39. **graphlaw×castle: canonical-hash unification (L30)** — rank 1. Unify
    castle-ggen-rdf `state_hash` with graphlaw `LawState::id` so both
    projects hash the same canonical form of the same TTL graph. Effort S.
    Falsifier: the same TTL input yields different hex on the two sides.
    Construction lane L41 in flight.
40. **insa×castle: SyncTrace → EvidenceInput (L32)** — rank 1: insa's
    `SyncTrace` lifts into castle `EvidenceInput` as a Replayed-class event
    (insa board.rs L164/L396, ~100 LOC). Rank 2: shared-KAT head as a
    castle admission gate. Falsifier: a replayed trace admitted without its
    KAT head.
41. **affidavit×ash_a2a: standing-receipt chain-hash event-link (L33)** —
    rank 1: chain head attested, not doc bytes; falsifier: an edited doc +
    fresh valid signature must be refused. MEASURED GAP:
    `iri.ex` `check_receipt` (`lib/ash_a2a/semantic/iri.ex:684`, called at
    :313/:404) is a presence-check only — a forged fingerprint passes
    today. Precondition: SHA-256 `ChainHasher` (Fnv256 is non-crypto).
    Construction lane L42 in flight.
42. **mfact×strata: Lean core candidates (L34)** — 5 candidates ranked.
    STRONGEST FLAG: tx round-trip FALSE for non-empty payload — decode
    drops payload and digest covers only counts; corroborated + pinned by
    the L44 byte-mutation court (strata-tx-pack, commit `bfe64efd8`); fix
    lane L46 in flight. Second: `rollback_to` interleave hole in the store
    (fix lane L47 in flight). Also flagged: `chain_work` u64 saturation tie;
    mempool inflation-passes-shadow (one-way law).
43. **strata×beam4pm: fitness-cap + event projection (L31)** — B1
    court-side final marking (closes the 5/6 fitness cap, zero model
    change) + A1 `st:gallEventType` projection — `candidate_committed`
    already admitted in the GALL vocab
    (`beam4pm/lib/beam4pm_gall_ocel.ex:35,52`). B1+A1 recommended,
    ~2 file edits.
44. **erlmcp×ash_a2a (L35)** — completed, 3 candidates ranked. Rank 1:
    conformance-report runner port (pattern Y, effort M; falsifier: a
    MUST violation not FAILing, or a deleted court still PASSing;
    construction lane in flight). Rank 2: shared refusal vocabulary
    crosswalk, ~40 erlmcp codes → ash_a2a classes (effort S-M; unlocks
    C14; pack lane in flight). Rank 3: TaskStore erlmcp adapter
    (effort L; premise correction verified on disk: `erlmcp_priority.erl`
    is in-memory OTP-28 priority aliases, NOT durable — the durable
    candidate is `erlmcp_a2a_task_manager.erl` ETS + a DETS layer).

## X-lane wave 3 + construction receipts — 2026-10-13 (evening)

Construction-lane results from wave 2's in-flight lanes plus three new
X-lane Explore receipts. Same discipline: SHAs exact, falsifiers cited,
KILLED entries stay killed.

45. **ggen-ecosystem×strata (L68)** — rank 1: `ecosystem.lock.toml` maps
    mechanically onto strata-store `ContentStore` (C18: pin →
    `StoredEntry`, ecosystem root → single commitment). Rank 2: crown CAS
    fast-forward as chain entries. CORRECTION to C17's premise:
    anti-windup is already implemented in `github_macro_governor.py`
    (subject-keyed demands + recovery-close verified on disk) — the open
    work is formalization, not invention.
46. **graphlaw×insa (L76)** — rank 1: differential chain court (insa
    3-input step vs graphlaw 99-byte frame fold; falsifier: legal-entry
    head divergence or truncation asymmetry). Rank 2: insa-law N3 pack —
    insa has zero RDF surface today. Rank 3: attest-over-anchors rejected
    as near-zero information gain.
47. **hash-unification KILLED (L41)** — wave 2 entry 39's construction
    lane could not unify: castle BLAKE3-no-frame-term vs graphlaw
    SHA-256-over-RDFC-1.0; 0/3 corpus match. Four layers decomposed
    (algorithm, framing, datatype, bnode labels); divergence pinned as a
    4-court file at graphlaw `tests/castle_hash_unification.rs`
    (commit `0731cbd`).
48. **valve↔affidavit parity IDENTICAL (L70)** — ETF `binary_ext`
    representation stable; 4 receipt hexes byte-equal Elixir/Rust.
49. **TCK re-run (L18)** — 79.0% compatibility unchanged; MUST failures
    87/0 after the pagination fixes (docs commit `2028e771`).
50. **v2-fold KAT MATCH (L66)** — independent in-test BLAKE3 reproduces
    the real ledger receipt chain hash (commit `c2cc4b62b`) — strata is
    now a verified spec substrate for praxis-chain/v2-fold.

## X-lane wave 4 — 2026-10-13 (night)

51. **castle↔beam4pm (L90)** — rank-1 live-feed adapter LANDED (castle
    `beam4pm_feed.rs`, live 201 court); rank-2 fleet-drift Art72 court
    (lane in flight); rank-3 castle vocab module LANDED
    (`BeamPM.CastleOcel`, non-overlap proven — court caught a real
    `receipt_sealed` name collision).
52. **mfact↔castle (L111)** — rank-1 Lean witness → Replayed
    EvidenceInput (axiom-sweep ⊆ standard trio is the load-bearing
    gate; digest = source sha + toolchain); rank-2 `lean-witness/v1`
    chained JSONL via strata-ingest pattern; rank-3 NEGATIVE-EVIDENCE
    GAP: castle has no standing-downgrade channel — defect witness
    (LedgerConservation `duplicate_input_creates_value`) expressible
    only as control inversion.
53. **ash_a2a↔strata (L101)** — R1 valve third crosswalk column (gates
    must generalize 51/18 literals → closure-style; lane in flight);
    R2 owner-scope committed receipts (parity-proven codec; wire rides
    data/detail not the code); R3 fuel-vs-rate-limit needs -32000 law
    reconciliation first.
54. **strata↔knhk (L82)** — rank-1 valve WindowCapacityRefusal LANDED
    (`8f98a4c49`, RDF-only, BLOCKED:merge-open boundary declared);
    rank-2 hot-ops as PN64 7th family (external ABI dep on ~/strata
    `pn64.rs`); rank-3 custody→store capacity semantics (cas excluded
    — analogy not equivalence).
55. **ENGINE HAZARD ESCALATED (L93)** — ggen SPARQL serializer leaks
    unbound OPTIONAL bindings across rows (rdflib-correct, ggen
    materializes); workaround COALESCE genesis sentinel in cas
    `commits.rq`; engine lane in flight.
56. **DEFECT WITNESSED (L72)** — ledger duplicate-input value creation
    proved in Lean (mfact `15fa5e91a7`); fix lane in flight;
    conservation theorem currently needs NoDupIds.

## Integration wave 5 — 2026-10-13 (late night)

57. **insa↔strata-tx (L130)** — polarity vocabulary REJECTED: three
    registers (receipt-typestate vs refusal-valve vs decode-fail-closed)
    share a class name but not semantics — one shared class would be
    laundering. Rank-1 compile-fail courts pattern (insa trybuild with
    exact .stderr pins; strata has zero today — lane in flight);
    rank-2 boundary-replay deepening (verify_from semantics into the
    ledger court).
58. **ledger duplicate-input DEFECT FIXED (1d16f2472)** — debit
    accumulation lands; the Lean counterexample now refuses; 500-tx
    unconditional property; audit corpus entry. mfact witness
    `15fa5e91a7` stands as the discovery receipt (#52/#56 resolved).
59. **owner-scope committed receipts (fb66f364) + standing-receipt
    chain (56e0eb84)** — L33 rank-1 and rank-2 both landed; falsifier
    witnessed live: a valid fresh signature refused by the chain court.
60. **valve crosswalk column (84bcb97f8 + ash_a2a pins 3bc2a5fc)** —
    three-runtime refusal plane mechanically crosswalked
    (erlmcp↔ash_a2a↔strata-valve); closure-style gates with 4 negative
    witnesses (#53 R1 resolved).
61. **fleet harness honesty** — erlmcp full eunit completes (376/237
    honestly reported, L88); cre master merge `9c69220c`; sabotage
    twins now 10/16 packs (5c932f000, coverage holes 10 → 6).

## Integration wave 6 — 2026-10-13 (deep night)

62. **graphlaw refusal-collapse FIXED (6c48b2c2, beam4pm bridge)** —
    ok-flag multi-key envelopes were passed through as success:
    admit_plan and both DeviationAdmission anti-vacuity gates
    admitted malformed input. Typed refusal now propagates across
    the bridge; 14/0.
63. **conservation proof tracks the fix (mfact `aa3d793cf5`)** —
    NoDupIds premise dropped, theorem unconditional; history kept
    honest: the old counterexample theorem renamed with the fix
    citation, plus an admits-and-conserves witness (#56 resolved).
64. **boundary-replay law in ledger verify.py (e1ee25fa2)** —
    mid-root pinned; a tamper below the boundary is caught ONLY by
    the boundary law (non-vacuity witnessed); length-mismatch
    input REFUSED.
65. **sabotage twins 13/16 (e1ee25fa2)** — cas/chain/governance added;
    the chain fold shares the KAT head `05ea1aa0`; 3 remaining
    coverage holes documented with justification (#61 10/16 advanced).
66. **compile-fail courts land (82033542d)** — trybuild with exact
    E-codes: gate state and recompute_root are unconstructible;
    tx-pack honestly UNSUPPORTED (no non-validating path exists to
    force). (#57 rank-1 resolved.)
67. **S3 closed mechanically (32af1f53a)** — signer digest-domain tag
    binds tx payloads; cross-pack ML-DSA court: byte-flip refuses;
    untagged twin caught in both directions.
68. **audit corpus 14 attacks** — includes GgenUnionBindingLeak
    OPEN-UPSTREAM and WasmNonReproducibleBuild OPEN (engine lanes
    in flight; cf. #55).

## Integration wave 7 — 2026-10-14

69. **mempool admission composition law (b3c8360cd)** — NECESSARY
    NOT SUFFICIENT for ledger admission, encoded as RDF with both
    gate citations + Lean provenance; fail-closed gate with
    mutation non-vacuity.
70. **BLAKE3 tx digest (320833d12)** — full multi-chunk port;
    pinned frame KAT `54ee6f3c...` vs b3sum; family determinism
    courts strengthened (20/20, +3 DRIFT_GUARDED).
71. **fleet gates all green (L140)** — 11/11 scope packs ALIVE;
    fresh fingerprint `88b64511...`; standing.md regenerated
    (326 packs); airo canary 326/540 (df8f8cb50).
72. **erlmcp honesty (L88, L121, L131)** — harness triage:
    export fix 206→201; ~250 tests target an API never
    implemented — build-out not repair, classified; 202 .broken
    files untracked (ERR-C); main-tree delta FLAT 256 failures,
    F18 zero regressions.
73. **graphlaw stable toolchain (05cfa6a) + pin re-sweep
    (003f73d)** — gate-engine differential court landed (3/3);
    tx fixture refresh in flight.
74. **Lean witness pipeline E2E (cece0148fd + castle 25ee42e)** —
    5 theorems → lean-witness/v1 JSONL → Replayed EvidenceInput;
    axiom footprints from `#print axioms`, never hardcoded.
75. **beam4pm receipt chain verified (31f75a51)** — 79/79 tips
    exact, 8/8 chains full-verify, 70 gap-incomplete honestly
    classified.

## Integration wave 8 — 2026-10-14

76. **witnessed KATs complete the L27 pattern fleet-wide
    (25307ca8b + 1a7741b2a)** — store content-address root
    (a8378cfa...), consensus u128 work-sum (total
    9223372041149808896), hash BLAKE3 KAT, temprun fuel
    sequence, airo pin in-pack witness (4d50748d7) — every
    major law now has a witness-surface KAT.
77. **constitution 17 constants (1a7741b2a)** — A2aWireLaw
    4 seals; drift negative fires.
78. **BLAKE3 triplication consolidated (8404cdd3d)** —
    hash-pack canonical owner, consumers sha-pinned, shared
    KAT vectors vs b3sum.
79. **lock repairs (8404cdd3d)** — aaif/qri/sa2a stale pins
    after f52ed0e85; sa2a receipt re-cut OWED (user-gated
    pin bump).
80. **audit staleness sweep (8404cdd3d)** — 3 inline copies
    were auditing retired laws — re-captured + meta-court.
81. **insa witness pipeline E2E (insa producer L182 +
    castle family-aware gate L196)** — honest rust-compiled
    marker family admitted as Replayed #rust; refused-witness
    typed path; the gate previously rewarded axiom
    fabrication — fixed.
82. **lean.witness OCEL order law (L188, mfact+beam4pm)** —
    fitness 1.0 under the law, 0.775 :DRIFT on swap;
    order-free baseline admits everything — the law IS the
    discrimination.

## Integration wave 9 — 2026-10-14

83. **ENGINE VERDICT CORRECTED (L114)** — the SPARQL engine never
    leaked: oxigraph per-row solutions proven correct; the leak
    was the generation_rules.rs static-render branch's Tera
    top-level row alias (loop-row fallback silently inherited a
    sibling row's OPTIONAL binding). Fix: cross-row key
    intersection only; heterogeneous rows fail loud FM-GEN-008;
    COALESCE workarounds remain necessary. ggen fix committed
    (coordinator).
84. **three-repo golden lifecycle (L189)** — strata valve
    derivation -> affidavit ChainBuilder<Sha256> -> sealed
    Receipt; mint reproduces 4 pinned hexes; systematic tamper
    REJECT (affidavit eed7c40).
85. **castle insa gate family-aware (L196)** — rust-compiled
    marker admits as Replayed #rust; refused-witness typed path
    (previously would launder a refusal into success evidence);
    the gate previously rewarded axiom fabrication —
    adjudication documented with its residual (producer trust).
86. **lean.witness OCEL order law (L188)** — the law IS the
    discrimination (order-free baseline 1.0; law 0.775 :DRIFT).
87. **AIRo finding (L185)** — airo.ttl was orphaned in its own
    pack (zero in-pack consumers); pin moved in-pack
    (4d50748d7); R2 typed-refusal surface gated on first making
    AIRo non-orphaned; R3 UNSUPPORTED (no rollout-window
    referent).
