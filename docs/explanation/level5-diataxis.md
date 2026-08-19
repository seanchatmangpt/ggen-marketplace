# Explanation: why Level 5 requires Diátaxis

Level 5 documentation is not a larger README. It is a correspondence system between admitted semantic source, manufacture, verification, authority, receipts, and the four different kinds of information a user needs.

The governing idea is:

```text
O* → { Tutorial, How-to, Reference, Explanation } → executable/inspectable evidence
```

The four outputs are intentionally different projections of the same admitted system. Combining them into one undifferentiated page loses useful constraints: tutorials become reference dumps, reference acquires narrative claims, operational instructions hide authority boundaries, and architecture explanations drift away from what is executable.

## Preserve

The marketplace preserves Diátaxis because learning, task completion, exact lookup, and architectural understanding are different user problems. Level 5 does not erase those distinctions in the name of consistency; it establishes correspondence between them.

It also preserves a stronger distinction: **documentation standing and runtime standing are separate**. A perfect reference does not prove a generated application runs. A successful tutorial does not prove all inputs are admitted. An explanation does not grant DO authority.

## Fence

The Level-5 fence is:

```text
Tutorial ≠ How-to ≠ Reference ≠ Explanation
Documentation ≠ execution
Generation ≠ actuation
Receipt ≠ correctness
Historical evidence ≠ exact-head evidence
```

Each quadrant has a bounded job and a bounded falsifier.

## Calculus

### Tutorial

A tutorial teaches by taking a learner through a real path. At Level 5, that path should terminate in observable verification rather than a screenshot or prose assertion.

A generic path is:

```text
observe → admit → compose → manufacture → verify → receipt → replay
```

The tutorial may stop before external DO. If it does, it must say so.

### How-to

A how-to begins from a concrete goal. It should name prerequisites, admitted inputs, the procedure, expected consequence, verification, authority ceiling, falsifiers, and rollback. The reader should not have to infer whether a command only constructs an intent or actually actuates a system.

### Reference

Reference is the closest documentation projection to canonical source. Facts that can be derived from ontology, manifests, admitted configuration, gates, or generated schemas should not be re-authored by hand in a second competing registry.

Reference answers: what exists, what it means, what command accepts it, what refusal rejects it, what output is manufactured, what identity is bound, and which compatibility surface is supported.

### Explanation

Explanation preserves why the architecture looks the way it does. Level-5 explanations should follow the repository's constitutional order:

```text
Preserve
→ Fence / Chesterton
→ Calculus
→ Exclusions
→ Falsifiers
→ Extensions
→ Operationalization
```

That order prevents a future maintainer from deleting a constraint merely because its original reason is no longer obvious.

## Exclusions

Level-5 Diátaxis deliberately does not require every pack to duplicate generic marketplace doctrine. Repeated generic material should be inherited from common documentation kernels or linked reference. Pack-specific docs should supply the semantic delta: the domain concepts, generated surfaces, gates, positive/negative witnesses, execution boundary, authority ceiling, and composition law unique to that pack.

Nor does generic documentation infrastructure manufacture facts it does not possess. `pack-maturity-pack` can provide the shape and mechanical checks for Diátaxis, regeneration, and receipts. It cannot truthfully invent a domain invariant, a negative witness, an external API result, or a customer's acceptance criterion.

## Falsifiers

The Level-5 documentation claim is falsified when any of the following is observed:

- one quadrant is missing or empty;
- the reference contradicts canonical RDF/manifest/configuration;
- a tutorial command is not the path actually used to verify the subject;
- a how-to crosses an authority boundary without naming it;
- generated surfaces or typed refusals are undocumented;
- replay/receipt claims have no executable or machine-readable witness;
- the explanation hides an exclusion or treats an unsupported boundary as admitted;
- composition semantics are replaced by copy/paste duplication;
- a generated documentation projection is hand-maintained as source authority.

## Extensions

A new Diátaxis requirement is lawful when it is attached to a named capability or pack class, has a typed falsifier, and does not manufacture domain semantics from absence. Families may add domain-specific tutorial/reference obligations while retaining the universal four-quadrant contract.

The same rule applies to automation: generators may project reference and skeletons from semantic source, but the system must refuse when required domain facts are missing instead of filling them with plausible prose.

## Operationalization

For marketplace packs, Level-5 Diátaxis is operationalized by:

1. the semantic facts and templates in `pack-maturity-pack`;
2. the generated four-quadrant documentation surface;
3. typed `L5-DOC-*` structural refusals;
4. consumer/domain courts that prove the documented execution paths;
5. repository Pages generation from `docs/book.ttl`, so mdBook navigation is itself a projection rather than a second hand-maintained control plane.

This produces the intended closure:

```text
semantic change
  → code/manufacture change if required
  → verifier/refusal change if required
  → reference/tutorial/how-to/explanation change
  → receipt/replay requalification
  → standing update
```

If those surfaces do not converge, Level 5 should refuse promotion rather than normalize the drift.
