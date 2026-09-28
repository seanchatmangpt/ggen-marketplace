# Provenance — semantic-life-loop-pack

## Fence

This pack exists only because the existing reusable packs stop at adjacent
boundaries:

- `lifegym-world-pack` owns life-world semantics and explicitly delegates
  consequential authority to GymAct.
- `biblegym-pack` already exposes
  `urn:biblegym:capability:devotion_prompt_packet` as a READ capability.
- `process-intelligence-pack` owns observed process/conformance/drift facts.
- `ocel-feedback-pack` already demonstrates the observed-evidence -> semantic
  gate feedback pattern.
- `semantic-jira-pack` in ggen_igniter owns WorkOrder admission.

The missing edge was a deterministic, authority-free representation from a
life + formation observation into the bounded delta contract consumed by
Semantic Jira. This pack supplies only that edge.

## Public vocabulary reuse

- PROV-O: episode activity, derived candidate entities, source usage.
- SOSA: observations.
- DCTERMS: stable identifiers and subjects.

The `sll:` residue is limited to the bridge concepts not supplied by those
vocabularies: Episode membership, delta class, work kind, and the source
digest.

## Authority

The template hard-codes the consequence boundary:

`CONSTRUCT_ONLY / CANDIDATE / do_authority=false / NOT_EXECUTED`.

Those values are consequences of this pack's law, not caller-supplied knobs.
The generated JSON is powerless input to a later Semantic Jira admission
court. It cannot dispatch, actuate, promote standing, merge, publish, or
deploy.
