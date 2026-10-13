//! Compile-fail court harness for strata-ledger-pack.
//!
//! The pack's generated `ledger_state.rs`, compiled unmodified via #[path]
//! (mirrors strata-signer-pack/courts).

#[path = "../../generated/ledger_state.rs"]
pub mod ledger_state;
