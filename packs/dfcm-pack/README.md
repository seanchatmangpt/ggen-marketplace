# DfCM Pack

`dfcm-pack` is the executable source model for **Design for Combinatorial Maximalism** and the deployment calculus for the full Chatman ecosystem. It preserves the lawful option graph until admission makes an irreversible choice defensible; it is not an imperative "install everything" script.

## Governing sequence

`Preserve → Fence/Chesterton → Calculus → Exclusions → Falsifier → Extension → Operationalization`

The operational calculus is `parse → route → admit/refuse → diagnose/repair → construct → actuate → receipt → replay/hook → standing`. `SELECT`, `CONSTRUCT`, and `DO` are distinct. `DO` has one authority route: BRCE. Hooks manufacture intents and never actuate.

## Standing law

- `UNKNOWN` is not admitted.
- `UNSUPPORTED` is not `REFUSED`.
- `ALIVE` requires observed execution against the exact admitted subject plus a receipt.
- One failed edge changes topology; it does not invalidate the remaining lawful option graph.
- Generated artifacts begin at `UNKNOWN`; generation cannot self-promote them to runtime standing.
- Receipts bind source, base, authority, artifact, consequence, toolchain, environment, predecessor, replay identity, and standing; the generated runtime requires BLAKE3 for digest manufacture.

## Full Chatman deployment profile

The ontology carries `FullChatmanEcosystem` across deterministic manufacture, formal admission, process/workflow, gym/actuation, deterministic MCP, release, and publication surfaces. Existing release engineering remains fenced: `chatman-ecosystem-release-pack` publishes admitted consequences; it is not the deployment actuator.

## Manufactured consumer surface

`ggen sync` manufactures fourteen coordinated projections from the same graph:

1. `DFCM_DEPLOYMENT.md` — human-readable deployment blueprint.
2. `DEPLOYMENT.toml` — machine deployment/proof contract.
3. `O.star.toml` — raw observation/admission carrier starting at `UNKNOWN`.
4. `OPTION_GRAPH.json` — reversible dependency topology.
5. `SELECT_LEDGER.json` — irreversible-selection fence and invariants.
6. `BRCE_POLICY.json` — exclusive `DO` authority route.
7. `RECEIPT_CONTRACT.json` — receipt-DAG morphism contract.
8. `REPLAY.md` — deterministic replay law.
9. `deployment-state.json` — initial bounded state.
10. `STANDING.json` — falsifier-bound standing declaration.
11. `runtime.py` — SELECT/CONSTRUCT/admit/BRCE/receipt/replay runtime with actuator injection only at BRCE.
12. `verify.py` — non-actuating state verifier with typed refusals.
13. `formal/DfcmAdmission.lean` — formal admission laws for authority and ALIVE standing.
14. `formal/MFACT.json` — `ggen renders; Lean admits; mfact certifies` certification manifest.

Marketplace qualification can establish deterministic graph load/manufacture/replay standing for these projections. It does **not** itself execute generated deployment programs or external actuators, so generated-runtime and external `DO` standing remain separate proofs.
