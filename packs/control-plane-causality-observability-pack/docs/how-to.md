# How to qualify a new control-plane observation

Update only admitted evidence, never generated projections or live control state.

- Add or replace fixture entities with exact request, workflow, receipt, and memory identities.
- Preserve `prov:used` for request → workflow and `prov:wasGeneratedBy` for receipt → workflow.
- Mark currentness explicitly. Stale observations remain useful falsifier evidence but must not be promoted to current truth.
- Mark `cpc:independentEvidenceRoot` only when the evidence root is genuinely independent; shared workflow infrastructure is not independence by itself.
- Keep `cpc:actuationPerformed false` for this pack. Any consequential DO belongs behind BRCE and a separate receipt boundary.
- Add a new court only for a distinct semantic question. Do not duplicate an existing predicate merely to increase court count.
- Run the executable verifier and repository marketplace validation before publication.

A failed court should be repaired at the narrowest failed transition and retained as a regression asset when generalizable.
