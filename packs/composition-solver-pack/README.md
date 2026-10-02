# composition-solver-pack

Class: KernelPack. Profile: project. Authority: SELECT/CONSTRUCT only, no DO.

## Identity

- Semantic source: `ontology.ttl` plus `ontology/basis.ttl` (seed atoms) and `ontology/requirements.ttl` (empty consumer input contract).
- Manufacture: `ggen.toml` runs five unrolled `[[inference.rules]]` stages (0 = givens, 1..4 = compose), then writes `generated/composition-solver/coverage.json` and `selected-atoms.json`.
- Gates (`gates/`, witnesses share the exact stem): atom identity, stage-bound convergence, given admission, DO fence.

## Evidence boundary

Marketplace admission and ggen qualification of this bounded boundary only. A covered requirement is a candidate plan at one exact subject, standing UNKNOWN. It is not a manufactured, qualified or executed capability. See `docs/reference/composition-solver-contract.md` for the contract and the known limits (L1-L5) that are tracked as sJira tickets.
