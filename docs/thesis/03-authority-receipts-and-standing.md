# Authority, receipts, and standing

## 1. Why authority is a separate axis

Deterministic manufacture does not imply safe execution. A compiler can deterministically emit a destructive program. A workflow can reproducibly deploy to the wrong environment. A signed artifact can faithfully preserve an unauthorized decision. For this reason, ggen Marketplace treats **semantic correctness, determinism, and authority as orthogonal dimensions**.

The system's governing intuition is simple:

> Construction may be broad; actuation must be narrow, explicit, and receipted.

This chapter formalizes that boundary and explains how repository standing is manufactured from evidence rather than inferred from intention.

## 2. BRCE: bounded receipted actuation

Let `I` be an intent manufactured by a planner, template, hook, or other construction process. Let `K` represent the authority context: permissions, policy, subject identity, target identity, and any required admission witnesses.

An actuation boundary may be modeled as a partial function:

`β : (I, K) ⇀ (D, R)`

where `D` is the consequential effect and `R` is a receipt.

The key invariant is:

`D ⇒ R`

Every successful consequential effect must yield a receipt sufficient to bind the effect to the exact admitted intent and authority context. This is the **Bounded Receipted Chatman Equation (BRCE)** in operational form: zero unreceipted actuation.

BRCE is deliberately narrower than “log everything.” Logs are observations. A receipt is an evidence object with identity, authority, consequence, and replay semantics.

## 3. No ambient authority

The following objects have no ambient execution authority merely by existing:

- raw user input;
- ontology facts;
- SPARQL query output;
- model or planner output;
- generated source code;
- a workflow definition;
- a hook;
- a proof artifact;
- a semantic derivation;
- a file named `receipt`.

Each may contribute to an authorized intent. None may silently become `DO`.

This prevents a common agentic failure mode in which the boundary between “the system proposed a change” and “the system executed the change” disappears inside one orchestration loop.

## 4. Hooks manufacture intents

A hook is often introduced as a convenient execution mechanism: “when X happens, run Y.” In an authority-preserving architecture, the hook should instead manufacture an intent:

`hook(event) → I`

The intent is then admitted at the BRCE boundary. This adds one explicit step but yields three advantages.

First, hook behavior becomes inspectable as data. Second, authorization policy can evolve independently from trigger logic. Third, replay can distinguish “the hook fired” from “the action was authorized and executed.”

This is particularly important for generated systems. A generated hook should never inherit the authority of the generator merely because both reside in the same repository.

## 5. Receipt semantics

A useful receipt binds six dimensions.

### 5.1 Subject identity

The receipt identifies exactly what was acted upon: repository and commit, pack fingerprint, deployment artifact digest, ontology digest, or another stable identity.

### 5.2 Authority identity

The receipt states why the action was permitted: workflow permissions, user authorization, admitted configuration witness, policy decision, or capability token.

### 5.3 Transformation identity

The receipt identifies the transformation or command that crossed the boundary. A successful exit code without command identity is weak evidence because it cannot be meaningfully replayed.

### 5.4 Consequence identity

The receipt records what changed: new branch SHA, publication artifact, external resource identifier, deployment revision, or immutable digest.

### 5.5 Verification identity

The receipt records which validator established the claimed postcondition. Creation and verification are distinct activities.

### 5.6 Replay context

The receipt records enough environment/toolchain information to reconstruct the check later, or explicitly states which dimensions remain unbound.

These dimensions can be represented as PROV-O entities/activities and cryptographic digests, but the exact serialization is secondary to the binding semantics.

## 6. Cryptographic identity

Cryptographic hashes are useful because they make byte identity compact and replayable. They do not, by themselves, establish truth or authority.

If `h = H(A)`, then `h` can bind future observations to the exact bytes of `A` under the collision-resistance assumptions of `H`. It cannot prove that `A` was correct, authorized, or safe.

A cryptographic receipt therefore composes at least two relations:

`subject --digest--> h`

`authority --permits--> action(subject)`

Confusing these produces a dangerous category error: provenance integrity becomes authorization.

The repository's use of exact Git commit SHAs follows the same logic. A SHA identifies the subject of a run. It does not make the run successful.

## 7. Exact-head law

For GitHub publication and CI, the most important receipt primitive is the exact commit under test.

Suppose PR head is `h`. A CI workflow establishes evidence for `h` only if the checked-out subject is also `h` or a documented merge subject whose relationship to `h` is part of the claim.

A robust workflow therefore performs:

1. resolve expected subject SHA;
2. checkout that exact SHA;
3. compute actual `git rev-parse HEAD`;
4. refuse if expected and actual differ;
5. run validators only after identity is established.

This ordering matters. A green validator on the wrong commit is not weak evidence; it is evidence for a different subject.

## 8. Evidence dimensions

Repository work frequently produces several kinds of evidence at once. They should be tracked independently.

- **observed** — the subject or metadata was read.
- **admitted** — the subject passed the named admission court.
- **executed** — the claimed command or behavior actually ran.
- **changed** — a persistent or consequential mutation occurred.
- **verified** — a validator observed the required postcondition.
- **inferred** — a conclusion was derived without direct execution.
- **refused** — a named court rejected the subject.
- **blocked** — execution could not proceed because of a prerequisite outside the subject.
- **unsupported** — the requested boundary is outside the available system contract.

This decomposition prevents “green check” from becoming a universal proof token.

## 9. Standing vocabulary

Standing compresses an evidence set into an operational status without erasing the underlying receipts.

### `UNKNOWN`

No sufficient evidence exists for the claimed boundary. `UNKNOWN` is not admitted uncertainty; it is absence of a qualifying observation.

### `PARTIAL_ALIVE`

Some required boundaries executed successfully, but the full claim remains unproven. A pack whose marketplace qualification passes while its publication workflow fails is `PARTIAL_ALIVE` for the combined “qualified and published” claim.

### `ALIVE`

The exact admitted subject executed successfully across the full claimed boundary and produced the required verification evidence.

### `BLOCKED`

The subject could not reach the required execution boundary because of an external prerequisite, such as unavailable credentials, missing network, unsupported runner environment, or inaccessible dependency.

### `BUILD_BROKEN`

Execution reached the relevant boundary and failed due to the subject or its declared build/manufacturing contract.

### `UNSUPPORTED`

The requested behavior is outside the available capability set. This is not equivalent to refusal: the system may have no applicable implementation at all.

### `REFUSED:<type>`

A policy or admission court intentionally rejected the subject. Typed refusal preserves cause and helps identify the lawful repair path.

## 10. Standing is scoped

A subject may have different standing at different boundaries.

For example:

| Boundary | Possible evidence | Standing |
|---|---|---|
| RDF parse | parser exit 0 | ALIVE for syntax |
| marketplace validation | validator exit 0 | ALIVE for repo contract |
| ggen qualification | two convergent syncs | ALIVE for manufacture |
| target tests | target test suite | ALIVE for tested runtime behavior |
| Pages build | mdBook compile | ALIVE for static site build |
| Pages deploy | deployment receipt | ALIVE for publication |

It is therefore imprecise to say “the pack is ALIVE” without naming the boundary when the context is ambiguous. The stronger the claim, the broader the required evidence closure.

## 11. Refusal versus failure

A mature system distinguishes **refusal** from **failure**.

Failure means the system attempted the operation and could not satisfy its postcondition. Refusal means the system determined that attempting the operation would violate its contract.

Examples:

- malformed Turtle → refusal at parse/admission;
- path escaping the pack root → `REFUSED:QUALIFICATION_CONTRACT_INVALID`;
- exact-head mismatch → `REFUSED:EXACT_HEAD_MISMATCH`;
- ggen exits non-zero on a valid admitted pack → build/manufacturing failure;
- deployment credentials absent → blocked, unless policy explicitly requires refusal.

Typed distinctions improve automated repair because each state implies a different next transition.

## 12. Replay and temporal standing

Standing decays when its bound identities cease to match the current subject.

Suppose a pack at SHA `h1` has a successful qualification receipt. A new commit `h2` changes the ontology. The `h1` receipt remains historically valid but cannot crown `h2`. The new subject returns to `UNKNOWN` or another pre-execution state for the affected boundary until revalidated.

This gives standing a temporal character:

`standing(subject, validator, toolchain, time)`

A reusable validation receipt is sound only when subject, validator, configuration, and relevant environment identities match. Reuse without identity equivalence is memoization across the wrong function arguments.

## 13. Standing DAG

For a complex release, evidence forms a DAG rather than a single line.

A simplified release DAG may include:

`source SHA`

→ `marketplace admission`

→ `pack qualification shards`

→ `aggregate qualification receipt`

→ `book manufacture`

→ `mdBook compile`

→ `Pages artifact`

→ `Pages deployment`

Each node has its own evidence. The release standing is the closure of the required nodes, not the color of any one workflow badge.

This structure enables targeted repair. If book manufacture fails after marketplace qualification succeeds, there is no reason to invalidate the already-observed qualification edge. The failed transition is localized.

## 14. Governance consequence

Authority separation changes organizational design. Humans or policies need not manually perform every action, but every action must still be attributable to an admitted authority relation. Automation can therefore increase while accountability becomes more precise.

This avoids a false dichotomy between “human in the loop” and “uncontrolled autonomy.” The meaningful question is not whether a human clicked the final button. It is whether the system can prove who or what had authority, what exact subject was acted on, which policy admitted the action, what consequence occurred, and how the claim can be replayed.

## 15. Falsifiers

The authority/standing model is falsified or materially weakened if:

- a generated artifact can mutate an external system without a distinct authorization edge;
- a receipt lacks exact subject identity but is used to crown current standing;
- a historical receipt is reused after source/validator/toolchain identity changes without proving equivalence;
- refusal, build failure, and environmental blockage are collapsed into one status;
- a successful workflow definition is treated as equivalent to a successful workflow run;
- the repository cannot reconstruct which validator established a release claim.

The next chapter turns these principles into an executable verification and security methodology.