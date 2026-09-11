# Deterministic Dynamic UI pack

This pack is the reusable ggen manufacture surface for Deterministic Dynamic UI (DDUI).

## Constitution

`UI_t = P(G_t, alpha, kappa, rho, Gamma)`

- `G_t`: admitted process/repository world state.
- `alpha`: avatar.
- `kappa`: context.
- `rho`: admitted authority.
- `Gamma`: bounded DDUI grammar.
- `P`: deterministic projection.

DfCM preserves the reversible presentation frontier before a deterministic presentation is chosen. Presentation choice is not business selection: `irreversibleUiSelections = 0`.

Runtime AI has no render authority. Rendering has no actuation authority. UI controls manufacture unselected intents only. `DO` remains behind BRCE.

## Ownership boundary

- **wasm4pm** owns process reduction, DDUI projection, receipts, intent receipts, and replay. The current DDUI v2 contract used by ecosystem integration is exact head `8d48e784a4215857c8428c09bb09a91c05a8be97` from draft PR #606; its dedicated DDUI verifier completed successfully before this pack was proposed.
- **ggen** owns deterministic manufacture from admitted RDF + query + template.
- **this pack** owns the reusable DDUI grammar ontology and manufactured grammar/topology projections.
- **consumer repositories** own their local world/profile observations. They do not fork the runtime projection law.

## Generated consequences

Running the pack manufactures:

- `dd-ui/grammar.json` — a deterministic inventory of admitted avatars, contexts, domains, components, and consequence classes.
- `dd-ui/uiux.mmd` — the Mermaid-first lawful UI topology.

These are generated projections and are not editing surfaces.

## DfCM falsifiers

The contract is false if identical admitted inputs can produce different projection identity, if a presentation choice acquires business authority, if rendering can DO, if runtime AI can introduce an unadmitted component, if an unknown avatar/context silently succeeds, or if replay cannot reconstruct the bound screen identity.

## Consumer pattern

Each ecosystem repository contributes a bounded `dd-ui/world.json` observation fixture. Its dedicated profile verifier checks that fixture against one exact wasm4pm DDUI engine SHA and replays every required avatar/context projection. This makes the ecosystem federated: local truth remains local, while projection law remains singular.
