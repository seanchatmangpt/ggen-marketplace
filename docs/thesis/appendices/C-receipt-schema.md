# Evidence and receipt schema

## 1. Objective

The marketplace produces evidence through Git identities, CI workflow runs, pack qualification, deterministic catalog/archive comparisons, target compilers, native consumer courts, documentation manufacture, and deployment systems. The next step is to make that evidence **structurally composable**.

This appendix specifies a candidate receipt model. It is deliberately format-neutral: the same logical receipt may be serialized as JSON, RDF, an in-toto/SLSA-compatible attestation, or another signed envelope. The semantic contract matters more than the container.

The schema has five goals:

1. bind evidence to an exact immutable subject;
2. state exactly which boundary executed;
3. preserve dependency and authority lineage;
4. make standing derivable rather than narrated;
5. support Level-5 closure without collapsing seven maturity dimensions or Diátaxis correspondence into one badge.

## 2. Receipt object

Define receipt:

`R = (id, schema, subject, claim, boundary, executor, inputs, authority, outputs, result, time, parents, evidence)`.

### 2.1 `id`

Immutable receipt identifier. Prefer a content-addressed identifier over a database sequence when canonicalization is defined.

### 2.2 `schema`

Receipt schema identifier and version.

Example:

```text
https://ggen.dev/receipt/v1
```

### 2.3 `subject`

The exact thing the receipt is about.

Recommended structure:

```json
{
  "repository": "seanchatmangpt/ggen-marketplace",
  "commit": "<git-commit-sha>",
  "tree": "<git-tree-sha>",
  "path": "packs/example-pack",
  "pack": {
    "name": "example-pack",
    "version": "<semver>",
    "profile": "projection",
    "class": "CapabilityPack"
  },
  "source_digest": {
    "algorithm": "sha256",
    "value": "...",
    "domain": "canonical-marketplace-pack-archive-v1"
  }
}
```

Fields are optional only when genuinely irrelevant to the claim. Omission MUST NOT mean “whatever was current.” Packaging profile and semantic pack class are separate fields.

### 2.4 `claim`

A stable claim type plus parameters.

Examples:

```text
marketplace.config.admitted
pack.source.valid
pack.ggen.manufactures
pack.replay.converges
pack.source.non_mutating
pack.domain.negative_witness.refused
pack.docs.diataxis.structural
pack.docs.correspondence
pack.composition.class_closed
pack.level5.alive
book.mdbook.compiles
pages.deployment.published
```

A human-readable summary MAY accompany the type but MUST NOT replace it.

### 2.5 `boundary`

Describes the executed transition.

```json
{
  "phase": "CONSTRUCT",
  "name": "ggen.sync.run",
  "scope": "root-self-hosting-consumer"
}
```

Recommended phases:

- `OBSERVE`
- `ADMIT`
- `SELECT`
- `CONSTRUCT`
- `VERIFY`
- `DO`
- `REPLAY`
- `DERIVE_STANDING`

A receipt records one primary boundary and references predecessor boundaries rather than pretending a large workflow is one atomic proof.

## 3. Executor and toolchain

The executor object binds the computation that produced the evidence.

```json
{
  "program": "ggen",
  "version": "<admitted-version>",
  "binary_digest": {
    "algorithm": "sha256",
    "value": "..."
  },
  "runner": {
    "provider": "github-actions",
    "image": "ubuntu-24.04",
    "workflow": ".github/workflows/pages.yml",
    "run_id": "<run-id>",
    "job_id": "<job-id>"
  }
}
```

Do not hardcode the repository's current ggen version into a schema example. The receipt binds the version actually admitted/executed for its subject.

The exact fields depend on the claim. A syntax parser receipt does not need a deployment identity; a supply-chain or Level-5 crown may need more complete toolchain/environment identity.

## 4. Inputs

Inputs capture claim-relevant dependencies not already encoded in subject.

```json
{
  "declared": [
    {"kind": "ontology", "path": "docs/book.ttl", "digest": "..."},
    {"kind": "pack", "name": "mdbook-pattern-language-pack", "digest": "..."},
    {"kind": "config", "path": "ggen.toml", "digest": "..."}
  ],
  "environment": {
    "timezone_relevant": false,
    "locale_relevant": false,
    "network_required": false
  }
}
```

An environment claim SHOULD state which attributes are believed irrelevant so that belief can later be challenged by perturbation.

For Level-5 claims, declared inputs SHOULD include identities for domain positive/negative witnesses, documentation semantic/control source, composition dependencies, and authority policy whenever those are required predicates.

## 5. Authority witness

Authority is a first-class receipt dimension.

```json
{
  "principal": "github-actions:pages-workflow",
  "phase": "DO",
  "capabilities": [
    "contents:read",
    "pages:write",
    "id-token:write"
  ],
  "policy": "ggen-marketplace-pages-policy-v1",
  "grant_evidence": "<provider-specific-reference>"
}
```

For a construction-only receipt, useful evidence may be the absence/prohibition of consequential capability:

```json
{
  "phase": "CONSTRUCT",
  "prohibited_capabilities_observed": [
    "pages:write",
    "repository:push"
  ]
}
```

The schema should distinguish declared capability, observed capability, and admitted authority. A generated artifact or signed receipt is not itself a capability grant.

## 6. Outputs

Outputs bind material consequences.

```json
[
  {
    "path": "book.toml",
    "media_type": "application/toml",
    "digest": {
      "algorithm": "sha256",
      "value": "...",
      "domain": "file-bytes"
    }
  },
  {
    "path": "docs/SUMMARY.md",
    "media_type": "text/markdown",
    "digest": {
      "algorithm": "sha256",
      "value": "...",
      "domain": "file-bytes"
    }
  }
]
```

A target-compiler receipt may instead output a directory/tree digest or provider artifact identifier. A Level-5 documentation receipt may bind generated Tutorial/How-to/Reference/Explanation paths and their source-control identity without treating those Markdown files as new semantic authority.

## 7. Result

Result is typed.

```json
{
  "status": "SUCCESS",
  "standing_candidate": "ALIVE",
  "exit_code": 0
}
```

Failure examples:

```json
{
  "status": "REFUSED",
  "code": "REFUSED:EXACT_HEAD_MISMATCH",
  "detail": "actual=<sha1> expected=<sha2>"
}
```

```json
{
  "status": "FAILURE",
  "code": "BUILD_BROKEN:FM-CONFIG-101",
  "detail": "consumer config ambiguous between schemas"
}
```

```json
{
  "status": "BLOCKED",
  "code": "BLOCKED:TOOLCHAIN_UNAVAILABLE"
}
```

The result vocabulary MUST preserve refusal, failed execution, unsupported capability, and non-execution as different states. A `standing_candidate` remains candidate until predecessor/evidence closure is checked.

## 8. Time and validity

Time fields:

```json
{
  "started_at": "<rfc3339>",
  "finished_at": "<rfc3339>",
  "observed_at": "<rfc3339>",
  "validity": {
    "policy": "until-claim-relevant-identity-changes"
  }
}
```

A receipt's historical truth does not expire: the execution happened. Its applicability to a current claim may expire when subject, validator, toolchain, configuration, dependency, environment, authority policy, documentation contract, or validity epoch changes.

## 9. Parent receipts

Receipts form a directed acyclic proof graph when each receipt references evidence required to justify its transition.

```json
{
  "parents": [
    {"relation": "requires", "receipt": "urn:receipt:config-admitted:..."},
    {"relation": "uses", "receipt": "urn:receipt:ggen-installed:..."},
    {"relation": "same-subject", "receipt": "urn:receipt:exact-head:..."}
  ]
}
```

Candidate relation types:

- `requires`
- `derived-from`
- `same-subject`
- `replay-of`
- `supersedes`
- `invalidates`
- `authority-derived-from`
- `artifact-derived-from`
- `corresponds-to`
- `migrates-consumer-of`
- `composes-with`

PROV-O can represent much generic lineage; local relations should exist only where standing/composition semantics require more precision.

## 10. Evidence attachments

Raw evidence can be referenced without embedding megabytes into the receipt.

```json
{
  "evidence": [
    {
      "kind": "workflow-log",
      "uri": "github-actions://run/<run>/job/<job>",
      "digest": "..."
    },
    {
      "kind": "artifact",
      "uri": "github-actions://artifact/<artifact-id>",
      "digest": "..."
    }
  ]
}
```

The receipt SHOULD remain meaningful if an external evidence store later expires. Critical identities, results, refusal codes, authority ceiling, and artifact digests therefore belong in the receipt itself.

## 11. Canonicalization

Content-addressed receipts require deterministic canonical bytes.

JSON object-key order is not semantic by default. RDF has multiple equivalent serializations. Therefore a receipt digest MUST declare the canonicalization domain.

Candidate approaches include canonical JSON, canonical CBOR, RDF Dataset Canonicalization when appropriate, or a versioned marketplace-defined canonical serialization.

Algorithm plus canonicalization domain must be named; a bare digest string is insufficient.

## 12. RDF representation

A receipt maps naturally to provenance concepts.

Conceptual Turtle:

```turtle
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ggr: <https://ggen.dev/receipt#> .

<urn:receipt:book-build:subject> a ggr:Receipt, prov:Entity ;
    ggr:claim ggr:MdBookCompiles ;
    ggr:subjectCommit "<exact-commit>" ;
    ggr:standingCandidate ggr:Alive ;
    prov:wasGeneratedBy <urn:activity:mdbook-build:run> .

<urn:activity:mdbook-build:run> a prov:Activity ;
    prov:used <urn:tree:subject> ;
    prov:used <urn:artifact:summary> ;
    ggr:executor "mdbook <pinned-version>" .
```

The final ontology should reuse PROV-O for generic lineage and define only terms required for boundary, standing, refusal, exact-subject, authority, maturity, and composition semantics.

## 13. Compatibility with in-toto/SLSA

The receipt model overlaps strongly with supply-chain attestations.

| Marketplace receipt | SLSA/in-toto concept |
|---|---|
| subject/output digest | statement subject/product |
| executor | builder/functionary |
| declared inputs | resolved dependencies/materials |
| boundary | build type / supply-chain step |
| parameters | external parameters |
| workflow run | run details |
| authority witness | signer/functionary + policy context |
| parent receipts | attestation/material graph |

The marketplace should prefer adapters over incompatible reinvention. What may remain local is the standing calculus, phase/refusal vocabulary, pack-composition semantics, and Level-5 evidence closure.

## 14. Standing derivation

A claim definition declares required predicates.

Example:

```json
{
  "claim": "book.publication.alive",
  "requires": [
    "subject.exact",
    "marketplace.config.admitted",
    "book.ggen.manufactured",
    "book.mdbook.compiled",
    "book.pages.deployed"
  ]
}
```

Conceptual derivation:

```text
function standing(claim, receipts, now):
    required = requirements(claim)
    matched = []

    for predicate in required:
        candidates = receipts proving predicate
        candidates = filter_exact_or_equivalent_subject(candidates, claim.subject)
        candidates = filter_valid_policy_epoch(candidates, now)

        if candidates is empty:
            if evidence_of_execution_failure(predicate): return BUILD_BROKEN
            if evidence_of_external_block(predicate): return BLOCKED
            if capability_is_unsupported(predicate): return UNSUPPORTED
            return PARTIAL_ALIVE if matched else UNKNOWN

        matched.append(select_admissible_receipt(candidates))

    if predecessor_closure_complete(matched): return ALIVE
    return PARTIAL_ALIVE
```

Conflicting receipts, revocation, policy epochs, and equivalence proofs remain mechanization obligations.

## 15. Level-5 evidence closure

For a bounded pack subject `P@S`, define Level-5 claim requirements:

```json
{
  "claim": "pack.level5.alive",
  "requires": [
    "subject.exact",
    "pack.semantic.authority",
    "pack.admission.positive",
    "pack.admission.negative_witnesses",
    "pack.manufacture.fixed_point",
    "pack.consumer.runtime.executed",
    "pack.receipt.valid",
    "pack.replay.valid",
    "pack.authority.fenced",
    "pack.composition.class_closed",
    "pack.docs.tutorial.corresponds",
    "pack.docs.howto.corresponds",
    "pack.docs.reference.corresponds",
    "pack.docs.explanation.corresponds"
  ]
}
```

This list is claim-relative. A documentation-only kernel may never claim an external deployment predicate. A world/simulation pack may have a different execution boundary from an infrastructure profile. The requirement set must describe the actual Level-5 claim, not a universal checklist detached from the subject.

### 15.1 Maturity vector receipt

A promotion receipt MAY summarize the evidence vector:

```json
{
  "maturity": {
    "semantic_source": "L5",
    "admission": "L5",
    "manufacture": "L5",
    "execution": "L4",
    "receipt_replay": "L5",
    "authority_fence": "L5",
    "composition": "L4"
  },
  "diataxis": {
    "tutorial": "ALIVE",
    "how_to": "ALIVE",
    "reference": "ALIVE",
    "explanation": "ALIVE"
  },
  "standing_candidate": "PARTIAL_ALIVE"
}
```

The vector is **derived metadata** over underlying receipts. It MUST NOT replace the evidence DAG, and coordinates MUST NOT be averaged into a global score.

### 15.2 Diátaxis correspondence receipts

A documentation receipt should distinguish:

- structural quadrant existence;
- source/reference correspondence;
- documented-command execution;
- generated-surface correspondence;
- refusal/falsifier correspondence;
- authority-boundary correspondence;
- replay/receipt correspondence.

`L5-DOC-*` structural success is therefore one predecessor of Level-5 documentation standing, not the whole crown.

### 15.3 Class-closure receipts

A class-closure receipt SHOULD bind:

- candidate family inventory;
- before/after `Class(P)` assignments;
- semantic facts canonicalized vs preserved;
- target ownership before/after;
- admission/refusal correspondence;
- consumer migration/supersession relations;
- toolchain/runtime compatibility;
- authority ceilings before/after;
- unresolved non-equivalences;
- rollback.

Deletion/supersession receipts require stronger evidence than an analysis finding such as `DUPLICATE_SEMANTIC_AUTHORITY`.

## 16. Receipt equivalence

Incremental qualification depends on deciding when an old receipt may prove a new claim.

Define claim-relative equivalence:

`R1 ≡_C R2`

when every field relevant to claim `C` is equivalent under its declared relation.

Examples:

- two runner IDs may be equivalent for an R3 replay class but not for exact execution provenance;
- a documentation-only change may be irrelevant to pack manufacture only if dependency closure proves no semantic/template/gate/config dependency on that file;
- a toolchain patch may be equivalent only if policy explicitly admits it;
- a profile refactor may preserve semantic authority but invalidate composition/consumer receipts.

Equivalence MUST be a proof object or admitted policy rule, not intuition used to avoid requalification.

## 17. Invalidation

Each receipt references identity nodes. When an identity changes, compute the receipt dependency closure:

```text
changed = {identity nodes whose values differ}
invalid = reachable_receipts(changed, proof_dependency_edges)
required = invalid ∩ receipts_needed_for_requested_claims
```

This yields minimum safe revalidation only when the dependency graph is complete. If dependency completeness is uncertain, expand conservatively.

Level-5 changes commonly invalidate multiple dimensions: moving semantic authority into a kernel may preserve generated bytes but invalidate composition, provenance, documentation/reference, and consumer migration receipts.

## 18. Receipt DAG invariants

A valid receipt graph SHOULD satisfy:

1. every crown-bearing receipt has an exact subject identity;
2. every artifact digest names algorithm and domain;
3. every `DO` receipt has authority evidence;
4. every replay receipt references the original/shared exact subject identity;
5. predecessor derivation edges are acyclic;
6. invalidation/revocation does not rewrite historical receipts;
7. contradictory receipts remain visible and trigger conflict resolution;
8. standing is computed from a policy version whose identity is recorded;
9. no receipt proves a broader boundary than its executed phase;
10. no missing edge is silently treated as proof;
11. a Level-5 summary vector is derivable from underlying dimension receipts;
12. Diátaxis structural receipts do not substitute for domain execution receipts;
13. class-closure receipts preserve unresolved non-equivalence rather than deleting it;
14. consolidation cannot widen authority without a new authority receipt.

## 19. Example: mdBook self-hosting chain

A high-fidelity receipt chain for the book contains separate receipts for:

1. exact subject checked out;
2. marketplace configuration admitted;
3. admitted ggen runtime installed;
4. root consumer manufactured `book.toml` and `docs/SUMMARY.md` from `docs/book.ttl`;
5. generated controls replayed/checked for determinism;
6. mdBook compiler installed at its pinned workflow identity;
7. `mdbook build` accepted the exact generated controls;
8. Pages artifact uploaded on an authorized publication event;
9. Pages deployment returned a public deployment identity.

A pull-request execution may lawfully supply steps 1–7 while skipping 8–9 because deployment authority is not granted to that event. The receipt DAG preserves that distinction without turning a green build into a deployment claim.

## 20. Release capsule

A release capsule can be defined as:

`Capsule = (source manifest, toolchain manifest, receipts, artifacts, reproduction instructions)`.

Minimum candidate contents:

- repository commit/tree;
- marketplace admitted-config receipt;
- corpus fingerprint;
- pack archive digests;
- exact manufacturer/toolchain identity;
- qualification receipt DAG;
- generated catalog/archive artifacts;
- target-compiler receipts for self-hosting infrastructure;
- Level-5 maturity/Diátaxis/class-closure receipts for any L5 claims;
- explicit missing evidence tiers;
- reproduction commands;
- expected digests.

The capsule SHOULD be independently downloadable/verifiable without trusting a mutable branch.

## 21. Security considerations

Receipt systems create new attack surfaces:

- forged success receipts;
- replaying a valid receipt for a different subject;
- omitting failed receipts;
- compromised signer/builder;
- digest ambiguity through unspecified canonicalization;
- truncated predecessor edges;
- policy downgrade;
- stale receipt reuse;
- confused-deputy authority claims;
- misleading Level-5 vector summaries that hide a missing coordinate;
- false class-closure receipts that erase incompatible consumers;
- log retention shorter than audit requirements.

Signing helps authenticity but does not prove semantic completeness. A perfectly signed false or incomplete receipt remains false or incomplete.

## 22. Research target

The receipt system is mature when an independent verifier can ask:

> “Why is this exact artifact or pack family allowed to have this exact standing?”

and obtain a closed machine-readable proof graph whose leaves are immutable source/policy/toolchain/authority identities and whose internal nodes are observed execution, replay, correspondence, and migration receipts.

At that point, CI ceases to be a collection of ephemeral green checks and becomes a **content-addressed evidence fabric** for semantic software manufacture and Level-5 class closure.
