# Governed Runtime Adapter Pack

Reusable GGen semantic law extracted from Project #2 fanout across PM4Py, Ex4pm, AshR2RML, POWL, MFW, mfact, and Weaver.

The pack models the boundary between a generated/governed consumer and an execution substrate. It deliberately does **not** implement process-intelligence algorithms. `wasm4pm/wasm4pm-compat` remains the exclusive PI algorithm owner; consumers bind to it through adapter/runtime identity.

## Generalized invariants

- exact subject + Project #2 + canonical OCEL lineage
- stable adapter/runtime identity and version/digest binding
- explicit execution mode; replay-only and SELECT/CONSTRUCT modes cannot acquire fresh DO
- consequential DO requires an authority policy, host-capability identity, and bounded resources
- input/output schema and content digests cross the adapter boundary
- receipts bind exact subject, adapter version, runtime digest, input/output digests, version, nonce, signature policy, provenance, and standing
- replay binds the original invocation and exact receipt rather than merely repeating a command
- WASM adapters additionally bind module digest, export/entrypoint, ABI, fuel, and memory limits
- external-process adapters bind executable and registry identity
- certified standing binds a certification digest
- PI ownership is fenced to `wasm4pm/wasm4pm-compat`

Consumers may map repository-specific vocabulary (Ash actions, Reactor steps, Python bridges, CLI routes, external registries, WASM modules) onto this framework-neutral contract.
