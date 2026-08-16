# Formal calculus of admitted manufacture

## 1. Motivation

A deterministic generator is easy to describe informally and surprisingly easy to overclaim formally. The phrase “input goes in and files come out” suppresses the distinctions that matter most in a governed software system: whether the input was observed or admitted, whether the transform was selected or authorized, whether materialization changed external state, whether a validator actually executed, and whether the resulting evidence binds to the exact subject later discussed.

This chapter introduces a compact calculus for those distinctions. It is intentionally operational rather than foundational mathematics: the notation exists to make invalid architectural moves visible.

## 2. The core equation

Let `O` denote an observation available to the system. Observation alone grants no standing.

Let `α` be an admission relation. When admission succeeds:

`α(O, Γ) = O*`

where `Γ` is the bounded context required to judge the subject and `O*` is the admitted observation.

Let `μ` be a manufacturing transformation. The basic manufacturing equation is:

`A = μ(O*)`

This equation is deliberately partial. `μ` need not be defined for every possible observation. A system that fails closed may return a typed refusal instead of an artifact.

A richer form makes context explicit:

`μ : Γ ⇀ (A, Rμ)`

where `⇀` denotes a partial function and `Rμ` is a manufacturing receipt. The context may contain policy, ontology, templates, dependency identities, toolchain identity, and configuration. The exact factorization is an implementation choice; what matters is that context is not ambient and that the admitted subject is not silently replaced.

## 3. Objects

The calculus distinguishes the following object classes.

### 3.1 Observation `O`

Raw or discovered information. Examples include a TOML file read from the repository, an RDF graph supplied by a consumer, a Git commit SHA obtained from GitHub, or a release manifest fetched from a registry.

An observation is not automatically true, current, authorized, or safe.

### 3.2 Admitted observation `O*`

An observation that has passed the applicable admission relation. Admission may prove only structural properties. For example, valid Turtle syntax does not prove semantic consistency, and a valid pack manifest does not prove that ggen can manufacture the pack.

The star therefore means **admitted for a named purpose**, not universally certified.

### 3.3 Artifact `A`

A materialized consequence of manufacture: source code, configuration, Markdown, an archive, a catalog, a deployment description, or another bounded file-system object.

Artifacts can themselves become observations for later stages. If a generated file is re-ingested, it enters the next stage as `O`, not as permanently privileged truth.

### 3.4 Intent `I`

A description of a possible consequential action. Intents are data. They carry no ambient actuation authority.

### 3.5 Action `D`

A consequential effect produced by an authorized `DO` transition: publishing a Git ref, deploying a Pages artifact, sending a request to an external system, or mutating a persistent resource.

### 3.6 Receipt `R`

A record that binds a transition to enough identity and evidence to support later replay or standing. A receipt may contain subject digest, exact commit, toolchain version, validator identity, command, exit code, consequence digest, timestamps, and typed failure information.

A file named `receipt.json` is not automatically a receipt in this sense. The semantics come from the binding properties, not the filename.

## 4. Morphisms

The principal morphisms are:

`parse : Bytes ⇀ Syntax`

`route : Syntax ⇀ Domain`

`admit : (Domain, Policy) ⇀ O*`

`select : O* ⇀ Candidate`

`construct : Candidate ⇀ A`

`authorize : (A or I, Authority) ⇀ AuthorizedIntent`

`do : AuthorizedIntent ⇀ (D, Rdo)`

`verify : (Subject, Validator) ⇀ Evidence`

`replay : Receipt ⇀ Evidence'`

`stand : EvidenceSet ⇀ Standing`

The arrows are partial because refusal is a first-class result. Each morphism has a local contract and can fail independently.

## 5. SELECT, CONSTRUCT, and DO

The most important decomposition is:

`SELECT → CONSTRUCT → DO`

### SELECT

Selection narrows the possibility graph. SPARQL is often a selection mechanism: from an admitted graph, a query chooses the rows relevant to a template. Selection should be reversible insofar as it only identifies candidates.

### CONSTRUCT

Construction materializes consequences without granting external authority. ggen templates are construction mechanisms. Their natural court is the filesystem: did the admitted data produce the expected bounded files?

### DO

`DO` crosses a consequential boundary. A Pages deployment, release publication, cloud change, issue mutation, or branch update belongs here.

The architectural rule is **zero unreceipted actuation**. Formally:

For every successful consequential transition `do(x) = (D, Rdo)`, a receipt `Rdo` must exist and must bind the action to the exact authorized subject.

This does not imply that every file write is a global actuation event. The boundary is scoped. A temporary qualification capsule may allow bounded filesystem construction while refusing network or repository mutation.

## 6. Admission invariants

A valid admission system should preserve at least four invariants.

### I1 — Non-escalation

`O` cannot be used where `O*` is required without passing through `admit`.

If a raw configuration file is supposed to be admitted through a validator, downstream installation logic cannot lawfully read the raw file directly as executable policy.

### I2 — Subject identity preservation

If `O*` was admitted for subject identity `s`, subsequent evidence must either refer to `s` or explicitly perform a new admission for a changed subject `s'`.

This is the Exact-Subject Law. A CI run against commit `h1` cannot establish standing for commit `h2` merely because the diff is believed to be small.

### I3 — Bounded context

Admission must name the relevant policy/toolchain context. If changing the validator, dependency set, or policy could change the result, those identities belong in the evidence boundary.

### I4 — Typed refusal

A failed admission should preserve the reason when feasible. `REFUSED:INVALID_SCHEMA` and `REFUSED:UNAUTHORIZED_ACTUATION` carry different operational information and lead to different repair paths.

## 7. Deterministic manufacture

For an admitted subject `x`, deterministic manufacture requires more than “the command exited zero once.” A useful local property is:

`μ(x) = A1`

`μ(x) = A2`

`digest(A1) = digest(A2)`

under an equivalent toolchain and bounded environment.

This is replay convergence. It is stronger than a single successful build and weaker than universal reproducibility across arbitrary environments. The latter requires the environment itself to be part of the admitted subject.

The marketplace qualification court operationalizes this by running the ggen boundary twice in an isolated consumer and comparing the resulting filesystem snapshot. A difference is not waved away as “generated noise”; it is evidence that the claimed deterministic boundary is false for that subject.

## 8. Closure and composition

Packs compose. Let `P = {p1, p2, …, pn}` be a set of packs and `E` the explicit dependency relation among them. The composition graph is `G = (P, E)`.

A pack is **dependency-closed for a consumer boundary** when every dependency required by its selected manufacturing path is present, admitted, and resolvable inside the bounded capsule.

Closure is path-sensitive. If a pack contains optional capabilities that the selected consumer does not invoke, those capabilities need not become actuation requirements merely because they exist in the repository.

This matters for combinatorial systems. One failed edge `e ∈ E` proves that the associated path is unavailable or invalid; it does not prove `G` has no lawful paths. A qualification system should therefore preserve as much topology as practical instead of collapsing all partial failure into one undifferentiated state.

## 9. Combinatorial maximalism

Software manufacturing often faces an avoidable contradiction: exploration benefits from many possibilities, while actuation must remain conservative. The calculus resolves the contradiction by maximizing reversible construction and minimizing irreversible selection.

Let `C(O*)` be the set of lawfully constructible candidates from an admitted subject. Let `D ⊆ C(O*)` be the subset authorized for actuation.

The design objective is not to minimize `|C|`. It is to preserve a large lawful candidate set while keeping the authority relation over `D` explicit and bounded.

This yields the principle:

> Preserve maximal reversible lawful possibilities before irreversible selection.

The constraint set includes ontology, capability, authority, cost, evidence, and declared policy. Combinatorial maximalism is therefore not “try everything.” It is “do not destroy lawful option value earlier than necessary.”

## 10. Standing as a derived judgment

Standing is not a property declared by the subject. It is a judgment derived from evidence.

Let `E_s` be the evidence set for subject `s`. Then:

`stand(E_s) = σ`

where `σ` belongs to a standing vocabulary such as `UNKNOWN`, `PARTIAL_ALIVE`, `ALIVE`, `BLOCKED`, `BUILD_BROKEN`, or `UNSUPPORTED`, plus typed refusals.

A useful ordering is not purely linear. For example, `BLOCKED` and `BUILD_BROKEN` communicate different states rather than different confidence levels. Nevertheless, `ALIVE` has a strict condition:

> `ALIVE` requires observed execution against the exact admitted subject across the exact claimed boundary.

This forbids several common substitutions:

- source inspection for execution;
- a workflow file for a successful workflow run;
- a connector object for a mounted local checkout;
- a unit test for an explicitly requested end-to-end behavior;
- successful generation for successful deployment;
- successful deployment for semantic correctness beyond the deployment boundary.

## 11. Receipts and replay

A receipt should be sufficient to answer four questions.

### Identity

What exact subject was acted on? Examples: repository, ref, SHA, pack fingerprint, ontology digest.

### Authority

Why was the action permitted? Examples: admitted config, explicit workflow permission, user-authorized publication target.

### Consequence

What changed or was produced? Examples: output digest, branch head, artifact identifier, deployment URL.

### Replay

What must be reconstructed to check the claim again? Examples: toolchain, command, validator, environment identity, source capsule.

A minimal receipt schema can therefore be modeled as:

`R = (subject, authority, transform, consequence, verifier, replay_context)`

The exact serialization may vary. The invariant is semantic: a receipt must bind these dimensions strongly enough to prevent a different subject from inheriting standing accidentally.

## 12. Falsifiers

The calculus is useful only if it identifies observations that would disprove it.

### F1 — Ambient execution

If a model, template, hook, or query can perform consequential external execution without crossing an explicit authority boundary, the SELECT/CONSTRUCT/DO separation is false.

### F2 — Unbound evidence

If a successful validator report cannot be tied to the exact source subject, the standing derived from that report is inadmissible.

### F3 — Non-convergent replay

If repeated manufacture over equivalent admitted input produces materially different consequences, determinism is false for that boundary.

### F4 — Duplicate canonical metadata

If two independently edited catalogs must be kept synchronized, the claimed source hierarchy is false or incomplete.

### F5 — Authority through naming

If calling a file, object, or event a “receipt” grants it standing without proving the required identity/authority/consequence/replay bindings, the receipt model has collapsed into nomenclature.

## 13. From calculus to repository architecture

The calculus maps directly onto marketplace structure:

- `marketplace.toml` is observed configuration until admitted.
- `pack.toml` declares pack identity.
- `ontology.ttl` carries semantic source facts.
- SPARQL queries perform bounded selection.
- templates perform construction.
- qualification capsules execute the manufacturing boundary.
- workflow exact-head assertions bind evidence to commit identity.
- Pages deployment crosses a separate publication boundary.

The next chapter develops this mapping as an ontology/compiler architecture and explains why the graph is the appropriate canonical intermediate representation.