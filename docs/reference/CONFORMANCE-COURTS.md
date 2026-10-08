# Conformance Courts

Index of the four flagship qualification courts backing the
[v26.10.8 release](release-v26.10.8.md) qualification matrix (28/28).

| Court | Test file | Tests | Verifies |
|---|---|---|---|
| AAIF Enterprise | `tests/test_aaif_enterprise_court.py` | 12 | Seven-gate agentic lifecycle: crypto identity, MCP authorization, inference routing, sandbox governance, SHACL, process conformance, anti-vacuity |
| Rust WASI/Wasmex | `tests/test_rust_wasi_wasmex_court.py` | 5 | WASM template/FFI integrity, leak-free linear memory, normative lifecycle conformance, anti-vacuity |
| CDBR Isolation | `tests/test_cdbr_isolation_court.py` | 4 | Container-disk-bound receipts: minting, single-use extraction, tamper/key-substitution refusal |
| PQC Closed-Enum | `tests/test_pqc_closed_enum_court.py` | 7 | LangSec closed-enum DFA, PQC enforcement, fuel-bounded halt, Select/Construct/Do separation |

## How to run

```bash
.venv/bin/pytest tests/test_aaif_enterprise_court.py \
  tests/test_rust_wasi_wasmex_court.py \
  tests/test_cdbr_isolation_court.py \
  tests/test_pqc_closed_enum_court.py -q
```

Current witnessed result (v26.10.8 campaign, re-witnessed for this page):
**28 passed** in 1.67s.

## AAIF Enterprise Court

File: `tests/test_aaif_enterprise_court.py` — 12 tests.

Chicago-style integration court: real rdflib graph parse, real SHACL
(pyshacl), real ECDSA/ES256 + JCS RFC 8785 canonicalization, real IEEE OCEL
v2 event emission with Petri net token-based replay. No mocks, no stubs, no
monkeypatches. Fail-witness anti-vacuity law: every security gate is subjected
to an unlawful mutation and witnessed failing.

Seven-gate architecture (module docstring):

1. Cryptographic Identity & Discovery Gate (JCS canonicalization + JWS tamper refusal)
2. MCP Authorization & Fail-Closed PEP Gate (CEL authorization rule verification)
3. Inference Scheduling & GAIE Routing Gate (InferencePool & EPP reference integrity)
4. Hardened Sandbox Governance Gate (non-root, read-only rootfs, dropped capabilities)
5. Enterprise RDF Topology SHACL Conformance Gate
6. Normative Multi-Object Process Conformance Gate (token-based replay fitness >= 1.0)
7. Process Conformance Anti-Vacuity Gate (illegal state machine bypass fails closed)

Gates/invariants by test ID:

- `test_signed_agent_card_validates_and_refuses_tampering` — signed agent card validates; tampered signature is refused (Gate 1).
- `test_authorized_tool_invocation_succeeds` and `test_unauthorized_tool_invocation_fails_closed` — CEL-backed PEP admits authorized tool calls, fails closed otherwise (Gate 2).
- `test_tier2_manifest_binds_to_inference_pool` and `test_inference_pool_binds_to_epp_service` — InferencePool and EPP reference integrity (Gate 3).
- `test_worker_deployment_enforces_security_context` — non-root, read-only rootfs, dropped capabilities (Gate 4).
- `test_enterprise_deployment_shacl_conformance` — real pyshacl validation of the enterprise topology (Gate 5).
- `test_full_admitted_agent_lifecycle_conformance_passes` — full admitted lifecycle replays with fitness >= 1.0 against the normative FSM (Gate 6).
- `test_illegal_bypass_skipping_policy_fails_conformance`, `test_expired_lease_actuation_tripwire`, `test_unbalanced_token_reservation_tripwire`, `test_unprivileged_uid_drift_tripwire` — anti-vacuity tripwires: policy bypass, expired lease, unbalanced token reservation, UID drift each fail witnessed (Gate 7).

Run: `.venv/bin/pytest tests/test_aaif_enterprise_court.py -q` — 12 passed.

## Rust WASI/Wasmex Court

File: `tests/test_rust_wasi_wasmex_court.py` — 5 tests. Qualifies
`packs/rust-wasi-wasmex-pack`.

Real collaborators: real template rendering, real ABI layout assertions, real
packed-u64 FFI contracts (alloc/call/free), real IEEE OCEL v2 process mining.
Petri net token-based replay against `spec/wasm_lifecycle.pnml`. Zero mocks,
zero virtual clocks.

- `test_guest_ffi_exports_alloc_call_free` — guest FFI template exports alloc/dealloc (Gate 1).
- `test_wasmex_host_manifest_declares_linear_memory` — host manifest declares linear memory, allocator, `packed_u64` (Gate 1).
- `test_linear_memory_100_invocations_leak_free` — 100 invocations, leak-free linear memory.
- `test_normative_wasm_lifecycle_conformance` — normative lifecycle replays with fitness >= 1.0.
- `test_unallocated_guest_invocation_fails_conformance` — anti-vacuity: unallocated guest invocation fails conformance.

Run: `.venv/bin/pytest tests/test_rust_wasi_wasmex_court.py -q` — 5 passed.

## CDBR Isolation Court

File: `tests/test_cdbr_isolation_court.py` — 4 tests. Exercises
`ggen_marketplace.cdbr` (`CDBRSealer`, `CDBRExtractor`).

Verifies CDBR-v1 (Container-Disk-Bound Receipt) proof-of-execution isolation:
in-container ephemeral Ed25519 key minting and disk-bound receipt sealing,
single-use capability descriptor emission and air-gapped HTTP extraction, and
anti-vacuity: burn-after-reading refuses replay, in-transit payload tampering
triggers immediate digest/signature failure, unauthorized key substitution
fails cryptographic verification.

- `test_cdbr_in_container_minting_and_extraction_roundtrip` — container-minted receipt round-trips and verifies.
- `test_cdbr_burn_after_reading_tripwire` — replay refused after single use.
- `test_cdbr_tampered_payload_in_transit_fails_verification` — in-transit corruption fails verification.
- `test_cdbr_unauthorized_key_substitution_fails` — unauthorized key substitution fails.

Run: `.venv/bin/pytest tests/test_cdbr_isolation_court.py -q` — 4 passed.

## PQC Closed-Enum Court

File: `tests/test_pqc_closed_enum_court.py` — 7 tests. Exercises
`ggen_marketplace.cdbr.pqc` and `ggen_marketplace.grammar`.

Verifies: closed-enum regular wire language parsing via DFA; anti-vacuity
rejection of free-form strings, SQL injection, and arbitrary prompts at the
lexical boundary; post-quantum algorithm enforcement with classical downgrade
refusal (FIPS 203/204); monotonic Lyapunov fuel depletion guarantees bounded
termination (sub-15 ms execution ceiling); category-theoretic invariant
Select != Construct != Do (unrepresentability of unauthorized actuation).

- `test_closed_enum_lexical_dfa_accepts_valid_sum_types` — canonical closed-enum envelope parses in O(n).
- `test_closed_enum_refuses_arbitrary_strings_tripwire` and `test_closed_enum_refuses_disallowed_keys_tripwire` — free-form strings and disallowed keys refused at the lexical boundary.
- `test_pqc_suite_refuses_classical_crypto_downgrade_tripwire` — classical downgrade refused (FIPS 203/204).
- `test_pqc_fixed_width_buffer_enforcement` — fixed-width buffer enforcement.
- `test_wasm_monotonic_fuel_depletion_guarantees_halt` — monotonic fuel depletion guarantees halt.
- `test_select_construct_do_unrepresentable_actuation` — Select/Construct/Do type-level separation: unauthorized actuation unrepresentable.

Run: `.venv/bin/pytest tests/test_pqc_closed_enum_court.py -q` — 7 passed.

## See Also

- [Release v26.10.8](release-v26.10.8.md)
- [Chicago work-equivalent court](chicago-work-equivalent-court.md)
- [Add or migrate a CI court](../how-to/add-a-ci-court.md)
