//! Compile-fail courts for strata-ledger-pack (insa trybuild pattern:
//! exact-error match, "must fail for the RIGHT error").
//!
//! Run via `cargo test --offline` from this directory.

#[test]
fn compile_fail_gate_bypass_is_unconstructible() {
    let t = trybuild::TestCases::new();
    t.compile_fail("tests/compile_fail/gate_state_private_field.rs");
    t.compile_fail("tests/compile_fail/private_root_recompute.rs");
}
