# Verification, security, and evaluation

## 1. Verification as an evidence ladder

A deterministic marketplace needs a verification strategy that increases confidence without collapsing distinct claims. The useful pattern is an **evidence ladder**: run the cheapest high-information court first, repair the narrowest failed transition, and expand only after success.

A typical ladder is:

`syntax → repository contract → semantic admission → manufacture → replay → target behavior → integration → actuation`

Each step asks a different question. A later success normally implies that some earlier prerequisites were traversed, but it does not make their evidence interchangeable. Conversely, an early failure should stop expensive downstream work because the subject has not earned admission to the next court.

## 2. Marketplace validation boundary

Repository validation answers questions such as:

- Does every pack directory have a legal identity?
- Does directory name equal `[pack].name`?
- Are required files present?
- Are prohibited path shapes absent?
- Does the marketplace corpus obey the source hierarchy?
- Can derived catalog metadata be produced deterministically?

This boundary is intentionally narrower than pack execution. A green marketplace validator proves the repository contract, not that the ggen runtime accepts every pack and not that every target behavior is correct.

## 3. Real-runtime qualification

The marketplace closes that gap by qualifying packs with the admitted ggen runtime. The core protocol is:

1. establish the pack source fingerprint;
2. build an isolated consumer capsule;
3. materialize required semantic or project dependencies;
4. execute `ggen sync run` under a bounded timeout;
5. snapshot the resulting consumer filesystem;
6. execute the same sync again;
7. snapshot again;
8. refuse nondeterministic replay if snapshots differ;
9. verify the pack source fingerprint did not mutate.

This protocol is stronger than static inspection because it observes the real compiler boundary. It is deliberately weaker than arbitrary runtime testing because qualification does not execute every generated application.

## 4. Isolation properties

Qualification capsules implement several security and epistemic boundaries.

### Filesystem isolation

Each pack receives a temporary consumer root. Generated files can be observed without giving the pack write access to canonical marketplace source.

### State isolation

Ordinary user state is redirected into a qualification-specific home. This reduces accidental dependence on developer-machine configuration.

### Time bounds

Each pass has a strict timeout. A pack that does not converge within the declared court is refused rather than allowed to occupy unbounded CI resources.

### Source immutability check

The pack is fingerprinted before and after qualification. A pack that mutates its own source during generation violates the marketplace contract even if generation otherwise succeeds.

### No arbitrary target execution

The court is filesystem-oriented. This prevents a pack's generated program from inheriting CI execution authority merely because the marketplace wants to prove generation.

These properties turn the qualification harness into a small sandboxed experiment rather than a general-purpose runner.

## 5. Threat model

The relevant threat model includes both malicious and accidental behavior.

### T1 — Path escape

A pack references files outside the admitted pack root using absolute paths, parent traversal, or symlink tricks.

**Control:** normalize and bound paths; refuse escape rather than attempting recovery.

### T2 — Source mutation

Qualification changes pack source and then validates the changed subject while claiming evidence for the original.

**Control:** pre/post source fingerprints and read-only CI expectations.

### T3 — Nondeterministic output

Generation depends on time, unordered iteration, environment, network state, random identifiers, or mutable external content.

**Control:** repeated manufacture plus consequence digest comparison. If environment is intentionally variable, that variability must be incorporated into the admitted subject rather than hidden.

### T4 — Dependency substitution

A consumer resolves a different dependency than the one whose provenance was admitted.

**Control:** explicit paths, release identity, exact commit or artifact digest where consequences depend on dependency bytes.

### T5 — Authority smuggling

A template, hook, or generated program uses marketplace CI credentials to perform unrelated external actions.

**Control:** least-privilege workflow permissions; qualification does not grant `DO` authority to pack code.

### T6 — Evidence substitution

A green run for one commit is presented as evidence for another.

**Control:** exact-head checkout and identity assertion before validation.

### T7 — Vacuous verification

Tests succeed because they do not actually touch the claimed behavior, use hand-transcribed expectations identical to implementation data, or validate only empty output.

**Control:** positive qualification fixtures, non-empty probes, adversarial falsifiers, behaviorally distinct verifiers, and review of proof independence.

## 6. Vacuity and proof independence

Generated proof can be misleading when proof and implementation are projections of exactly the same mistaken relation. If both code and test expectations are rendered from an identical query, a missing domain case can disappear from both sides and the test remains green.

This does not make generated tests useless. It means proof strength depends on **independence of the witness**.

Useful sources of independent evidence include:

- a second query with a different structural path;
- source-audited counts or type contracts;
- a real target runtime;
- adversarial fixtures that should be refused;
- compilation failure when a required generated symbol is absent;
- external standards or schema validators;
- exact consequence comparison against a separately manufactured oracle.

The design goal is not complete independence—often impossible—but enough diversity that one ontology omission is unlikely to erase both implementation and falsifier.

## 7. Determinism tests

Determinism can fail at several layers.

### Query nondeterminism

SPARQL result ordering is not guaranteed unless ordered. If row order affects output, `ORDER BY` is part of the semantic contract.

### Template nondeterminism

Templates may iterate over maps whose ordering is undefined by the template engine or data model.

### Environment nondeterminism

Generated content may include current time, absolute paths, hostnames, tool versions, or locale-dependent formatting.

### Dependency nondeterminism

Unpinned dependencies can change generated output without source changes.

### Write-policy nondeterminism

A generator may merge with existing files differently depending on prior local state.

A replay court should therefore compare the observable consequence, not merely exit codes. The marketplace's filesystem snapshot digest is a practical approximation of referential transparency at the consumer boundary.

## 8. Security of the publication path

The mdBook workflow adds a second execution plane after pack qualification. Its security properties should be analyzed separately.

### Build identity

The workflow checks out the exact PR or main subject and asserts the resulting Git SHA before manufacture.

### ggen provenance

The ggen binary is installed from admitted marketplace configuration, and release identity/digest checks bind the executable to the configured release.

### Manufacture before compile

`book.toml` and `SUMMARY.md` are regenerated from the mdBook pack before `mdbook build`. The static-site compiler therefore consumes the semantic projection rather than an independently hand-edited navigation file.

### Compile before deploy

GitHub Pages receives only the built static artifact. Deployment does not bypass the mdBook compiler.

### Permission separation

The build job can operate with read-oriented repository permissions. The Pages deployment job needs deployment-specific authority. Keeping these as distinct jobs aligns workflow permissions with SELECT/CONSTRUCT/DO separation.

## 9. Failure localization: the self-hosting example

The first Pages execution against the mdBook feature branch provides a useful empirical example.

Marketplace CI and the vacuity audit succeeded, establishing that the pack itself satisfied repository admission and real-runtime qualification. The Pages workflow then failed at `ggen sync run` while manufacturing the self-hosted book. The admitted ggen runtime reported that the root `ggen.toml` was ambiguous between declarative and frontmatter schemas because the consumer combined a project-version marker with a packs table shaped for frontmatter projection.

This failure is valuable because it distinguishes two claims:

- **pack qualification claim:** the generic mdBook pack is manufacturable — supported;
- **self-hosting consumer claim:** the repository's root consumer contract is manufacturable — broken at that exact head.

The correct repair is therefore local: make the root consumer unambiguously one schema. Rewriting the pack or weakening marketplace qualification would repair the wrong transition.

This is evidence-driven debugging in the architecture's own terms: preserve successful edges, locate the failed morphism, repair the narrowest cause, encode a permanent guard if appropriate, and rerun the boundary.

## 10. Evaluation dimensions

A marketplace pack can be evaluated on at least eight dimensions.

### E1 — Semantic coverage

How much of the target domain is represented as inspectable facts rather than template literals or handwritten generated output?

### E2 — Projection fidelity

Do generated consequences preserve the semantics of the selected graph relation?

### E3 — Determinism

Does replay over equivalent admitted subjects converge?

### E4 — Composability

Can the pack be combined with other packs without hidden global state or path escape?

### E5 — Provenance

Can outputs be traced to pack source, ontology, templates, toolchain, and consumer facts?

### E6 — Falsifiability

Does the pack have fixtures or validators capable of failing when its central claim is false?

### E7 — Authority discipline

Can generation remain useful without granting unnecessary actuation rights?

### E8 — Operational cost

How much wall-clock time, network access, toolchain installation, and CI capacity are required to establish standing?

These dimensions are deliberately plural. A pack may have excellent semantic coverage and poor runtime economics, or excellent determinism and weak behavioral verification.

## 11. Performance and Little's Law

Marketplace evolution is also a flow problem. Let:

- `L` = average work in process;
- `λ` = average completed pack changes per unit time;
- `W` = average lead time from admitted task to verified consequence.

Little's Law gives:

`L = λW`

For a large corpus, serial qualification increases `W` and therefore raises WIP at a fixed arrival rate. The marketplace's sharded qualification strategy reduces critical-path time by paying fixed admission cost once and distributing independent pack qualifications across workers.

The important optimization target is not raw commit count or test count. It is **evidence throughput**: how quickly an admitted change can obtain the receipts required for standing without weakening the courts.

Parallelism is lawful when shards are independent and the aggregate court proves complete, non-overlapping coverage. Otherwise parallelism can improve wall-clock time while silently dropping evidence.

## 12. Cost of false positives and false negatives

Verification design balances two errors.

### False positive

The court assigns standing to a subject whose claimed behavior is false. This is especially dangerous at authority boundaries because downstream automation may act on the result.

### False negative

The court refuses or fails a subject that is actually lawful. This reduces throughput and can encourage engineers to bypass the court.

Fail-closed systems intentionally bias toward avoiding false positives at consequential boundaries, but excessive friction can undermine adoption. The architectural solution is not to weaken the final court; it is to move cheap, precise diagnostics earlier and preserve typed failure reasons so repair is fast.

## 13. Experimental protocol for a pack

A rigorous pack evaluation should record:

1. **Subject identity** — repository, pack name, exact source SHA/fingerprint.
2. **Claim** — the specific manufacturing or behavioral boundary under test.
3. **Admission** — syntax/schema/policy checks applied before execution.
4. **Toolchain** — exact ggen and validator identities.
5. **Consumer** — fixture graph and project overlay.
6. **Execution** — command, timeout, environment bounds.
7. **Consequence** — generated file inventory and digest.
8. **Replay** — second-run digest and drift result.
9. **Negative controls** — mutations expected to trigger refusal or test failure.
10. **Standing** — scoped judgment derived from the above.

This protocol makes a pack evaluation closer to an experiment than to a screenshot of a green CI badge.

## 14. Research validity threats

The marketplace's own evidence has limitations.

### Construct validity

Filesystem convergence is an operational proxy for deterministic generation, not proof of semantic correctness.

### External validity

A pack qualified in the marketplace capsule may encounter different target environments or toolchains in downstream repositories.

### Internal validity

A qualification harness defect could produce systematic false confidence across many packs. The harness itself therefore needs adversarial tests and independent review.

### Temporal validity

Receipts are bound to exact source/toolchain identities. Updating ggen, Python, action versions, or marketplace policy can invalidate reuse assumptions.

### Selection bias

Packs that are easy to model declaratively may be overrepresented among successful examples. Runtime-heavy or environment-dependent domains require additional courts.

Explicitly naming these threats prevents local success from becoming an unbounded general claim.

## 15. Security theorem, stated modestly

The architecture supports the following bounded proposition:

> If pack source is admitted under bounded path and schema rules, qualification executes only the declared ggen manufacturing boundary in an isolated capsule, source identity is unchanged, repeated manufacture converges, workflow execution is bound to the exact commit, and consequential deployment requires separate permissions, then the marketplace substantially reduces the classes of accidental source mutation, evidence substitution, hidden dependency drift, and ambient actuation available through the qualification path.

This is not a proof that generated software is secure. It is a security property of the **manufacturing and evidence plane**.

The next chapter studies the marketplace as a socio-technical distribution system: composition, governance, versioning, economics, and release standing.