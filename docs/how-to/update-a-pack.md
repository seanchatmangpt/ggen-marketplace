# How to update a pack

## 1. Resolve the exact existing contract

Read the pack's current manifest, RDF, templates/project rules, gates, qualification fixtures, README/docs, dependencies, and known consumer/compatibility surfaces. Record the exact base SHA before editing.

Classify the requested change as one or more of:

- semantic authority;
- admission/refusal;
- projection/manufacture;
- consumer/runtime contract;
- receipt/replay;
- authority boundary;
- composition/compatibility;
- metadata/documentation only.

## 2. Change source, not consequences

Make the smallest coherent source change. If a generated consumer artifact is wrong, repair RDF/query/template/gate/project source and regenerate; do not patch the output in place.

Bump `[pack].version` when the published behavior or contract changes.

## 3. Preserve documentation correspondence

Any semantic or behavioral change must update the relevant Diátaxis surface:

- tutorial path when the learning journey changes;
- how-to when the operator procedure/authority ceiling changes;
- reference when exact commands/schema/gates/generated surfaces change;
- explanation when the architecture, fence, exclusion, or extension law changes.

For Level-5 packs, a semantic change that leaves those surfaces contradictory is a maturity regression even if the code still compiles.

## 4. Re-evaluate class/duplication

Check whether the change introduces semantic truth already owned by a kernel/capability sibling. Prefer importing/composing the canonical class over creating a second authority.

If the pack is compatibility-only, new features should normally land in its named successor rather than extending the legacy surface.

## 5. Validate and qualify

Run marketplace structural admission and deterministic catalog projection. For behavioral changes, run the real ggen manufacturer against representative consumer RDF, prove replay/fixed point, then run the consumer's native verifier and relevant negative witnesses.

When receipts are part of the contract, verify them again.

## 6. Re-score maturity

Use [the Level-5 maturity contract](../reference/level5-maturity-contract.md). A change may improve one dimension while regressing another. Do not average away a lost authority fence, negative witness, composition contract, or runtime court.

## 7. Publish exact-subject evidence

Use a purpose branch and PR. Record exact base/head, commands/exits, generated status, positive/negative witnesses, receipts/replay, authority ceiling, Diátaxis correspondence, compatibility/consolidation impact, falsifiers, rollback, and scoped standing.

Historical ALIVE evidence does not automatically transfer to a changed subject.
