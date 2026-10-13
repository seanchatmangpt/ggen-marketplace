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
44. **erlmcp×ash_a2a (L35)** — re-running; in-flight, no receipt yet.
