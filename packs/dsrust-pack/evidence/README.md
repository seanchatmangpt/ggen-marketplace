# Real verification evidence, dsrust-pack v0.1.0

Real, live end-to-end test (this repo does not commit the throwaway consumer
project itself, only this record): a consumer `ggen.toml` referenced this
pack via local `path`, with a real `ontology.ttl` supplying one `Signature`
(`ProposeDisposition`, 4 inputs, 2 outputs -- `proposed_disposition`
constrained to 5 `dsrust:LiteralOption`s: `ARCHIVED`(0)/`REFUSED`(1)/
`REPLACED`(2)/`SUBSUMED`(3)/`PRESERVED`(4)) and one `Module` (`kind
"Predict"`) with a real `groq-lm` `LMConfig`.

- `ggen sync run` against that consumer: real success, gate passed, wrote
  `src/dsrust_program.rs`.
- `cargo check` of a real standalone crate wrapping the generated file
  against real `dsrust = "0.1.0-alpha.2"`: **`Finished `dev` profile
  [unoptimized + debuginfo] target(s)` -- zero errors.**
- The generated instructions text correctly ordered the 5 literal options
  by `optionIndex` (`ARCHIVED, REFUSED, REPLACED, SUBSUMED, PRESERVED`),
  confirming the `fieldConstraints` query's pre-sorted-subquery fix.
- Applied the identical generated pattern (`Signature::from_str` +
  `with_instructions` + `Predict::from_signature`, replacing the earlier
  unconstrained `predict!` macro call) to this pack's real first consumer,
  `ggen-legacy/tools/dsrust-disposition-proposer`. Real `cargo build`:
  clean. Two real, live Groq API calls (model
  `llama-3.3-70b-versatile` via Groq's OpenAI-compatible endpoint) each
  returned exactly one of the 5 constrained values -- confirming the fix
  works against a real model, not just a template-rendering test.
