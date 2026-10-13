//! The state-root commit step (`recompute_root`) is private: a receipt chain
//! can only be advanced through `apply_transition`, so prev_root/next_root
//! chaining cannot be forged out-of-band. Direct invocation must NOT compile.

use strata_ledger_courts_compile::ledger_state::LedgerState;

fn main() {
    let mut st = LedgerState::new();
    st.recompute_root();
}
