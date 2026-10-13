//! Gate-bypass law, mechanically enforced: the ledger's gate state (applied
//! digests, per-account nonces, balances, OCEL log) is PRIVATE, so the only
//! route to state mutation is `apply_transition` — every refusal valve runs.
//! Reaching past the valves via direct field access must NOT compile.

use strata_ledger_courts_compile::ledger_state::LedgerState;

fn main() {
    let mut st = LedgerState::new();
    // Replay-valve bypass: plant a digest in the `seen` set directly.
    st.seen.insert([7u8; 32]);
    // Double-spend-valve bypass: overwrite the per-account nonce directly.
    st.nonces.insert([1u8; 32], 999);
    // Balance forgery: write a balance without passing the conservation gate.
    st.accounts.insert([2u8; 32], u128::MAX);
    // OCEL log forgery: append an event without an applied transition.
    let _ = &st.events;
}
