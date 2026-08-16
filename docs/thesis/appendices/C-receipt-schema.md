# Evidence and receipt schema

## 1. Objective

The marketplace already produces evidence through Git commits, CI workflow runs, pack qualification, deterministic catalog/archive comparisons, target compilers, and deployment systems. The next step is to make that evidence **structurally composable**.

This appendix specifies a candidate receipt model. It is deliberately format-neutral: the same logical receipt may be serialized as JSON, RDF, an in-toto/SLSA-compatible attestation, or another signed envelope. The semantic contract matters more than the container.

The schema has four goals:

1. bind evidence to an exact immutable subject;
2. state exactly which boundary executed;
3. preserve dependency/authority lineage;
4. make standing derivable rather than narrated.

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
  "source_digest": {
    "algorithm": "sha256",
    "value": "...",
    "domain": "canonical-marketplace-pack-archive-v1"
  }
}
```

Fields are optional only when genuinely irrelevant to the claim. Omission MUST NOT mean “whatever was current.”

### 2.4 `claim`

A stable claim type plus parameters.

Examples:

```text
marketplace.config.admitted
pack.source.valid
pack.ggen.manufactures
pack.replay.converges
pack.source.non_mutating
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

A receipt can record one primary phase and reference predecessor phases rather than pretending a large workflow is one atomic boundary.

## 3. Executor and toolchain

The executor object binds the computation that produced the evidence.

```json
{
  "program": "ggen",
  "version": "26.8.11",
  "binary_digest": {
    "algorithm": "sha256",
    "value": "..."
  },
  "runner": {
    "provider": "github-actions",
    "image": "ubuntu-24.04",
    "workflow": ".github/workflows/pages.yml",
    "run_id": "31931779811",
    "job_id": "95127613950"
  }
}
```

The exact fields depend on the claim. A syntax parser receipt does not need a deployment identity; a supply-chain crown may.

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

An environment claim SHOULD be explicit about which attributes are believed irrelevant. That belief can then be tested through perturbation.

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

For a construction-only receipt, the useful evidence may be the **absence** of consequential capability:

```json
{
  "phase": "CONSTRUCT",
  "prohibited_capabilities_observed": [
    "pages:write",
    "repository:push"
  ]
}
```

The schema should eventually distinguish declared capability from independently observed capability.

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

A target compiler receipt may instead output a directory/tree digest or provider artifact identifier.

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

The result vocabulary MUST preserve the difference between refusal, failed execution, and non-execution.

## 8. Time and validity

Time fields:

```json
{
  "started_at": "2026-08-16T06:17:40Z",
  "finished_at": "2026-08-16T06:18:10Z",
  "observed_at": "2026-08-16T06:18:11Z",
  "validity": {
    "policy": "until-subject-or-validator-identity-changes"
  }
}
```

A receipt's historical truth does not expire: the execution happened. Its **applicability to a current claim** may expire. The schema should model this without mutating the original receipt.

## 9. Parent receipts

Receipts form a directed acyclic proof graph when each receipt references the evidence required to justify its transition.

Example:

```json
{
  "parents": [
    {"relation": "requires", "receipt": "urn:receipt:config-admitted:..."},
    {"relation": "uses", "receipt": "urn:receipt:ggen-installed:..."},
    {"relation": "same-subject", "receipt": "urn:receipt:exact-head:..."}
  ]
}
```

Parent relation types SHOULD be semantically meaningful rather than one generic edge.

Candidate relations:

- `requires`
- `derived-from`
- `same-subject`
- `replay-of`
- `supersedes`
- `invalidates`
- `authority-derived-from`
- `artifact-derived-from`

PROV-O can represent much of this lineage; local relations should be introduced only where provenance semantics do not express the standing-specific meaning.

## 10. Evidence attachments

Raw evidence can be referenced without embedding megabytes into the receipt.

```json
{
  "evidence": [
    {
      "kind": "workflow-log",
      "uri": "github-actions://run/31931779811/job/95127613950",
      "digest": "..."
    },
    {
      "kind": "artifact",
      "uri": "github-actions://artifact/12345",
      "digest": "..."
    }
  ]
}
```

The receipt SHOULD remain meaningful if the external evidence store later expires. Therefore critical result fields and digests belong in the receipt itself.

## 11. Canonicalization

Content-addressed receipts require deterministic canonical bytes.

JSON object-key order is not semantic by default. RDF has multiple equivalent serializations. Therefore a receipt digest MUST declare the canonicalization domain.

Candidate approaches:

- RFC-defined canonical JSON where suitable;
- canonical CBOR;
- RDF Dataset Canonicalization when standardized/appropriate;
- a marketplace-defined versioned canonical serialization.

The constitution requires algorithm plus domain naming to prevent a digest from appearing stronger than its representation contract.

## 12. RDF representation

A receipt can map naturally to provenance concepts.

Conceptual Turtle:

```turtle
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix ggr: <https://ggen.dev/receipt#> .

<urn:receipt:book-build:35b11cfb> a ggr:Receipt, prov:Entity ;
    ggr:claim ggr:MdBookCompiles ;
    ggr:subjectCommit "35b11cfb..." ;
    ggr:standingCandidate ggr:Alive ;
    prov:wasGeneratedBy <urn:activity:mdbook-build:31931779811> .

<urn:activity:mdbook-build:31931779811> a prov:Activity ;
    prov:used <urn:tree:35b11cfb> ;
    prov:used <urn:artifact:summary> ;
    ggr:executor "mdbook 0.5.3" .
```

The final ontology should reuse PROV-O for generic lineage and define only the terms required for boundary, standing, refusal, exact-subject, and authority semantics.

## 13. Compatibility with in-toto/SLSA

The receipt model overlaps strongly with supply-chain attestations.

Potential mapping:

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

The marketplace should prefer adapters over incompatible reinvention. What may remain local is the **standing calculus** and phase/refusal vocabulary.

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
            if evidence_of_execution_failure(predicate):
                return BUILD_BROKEN
            if evidence_of_external_block(predicate):
                return BLOCKED
            if capability_is_unsupported(predicate):
                return UNSUPPORTED
            return PARTIAL_ALIVE if matched else UNKNOWN

        matched.append(select_admissible_receipt(candidates))

    if predecessor_closure_complete(matched):
        return ALIVE

    return PARTIAL_ALIVE
```

This pseudocode is intentionally incomplete around conflicting receipts, revocation, and temporal policies. Those are mechanization obligations, not reasons to keep standing manual forever.

## 15. Receipt equivalence

Incremental qualification depends on deciding when an old receipt may prove a new claim.

Define claim-relative equivalence:

`R1 ≡_C R2`

when every field relevant to claim `C` is equivalent under its declared relation.

Examples:

- two runner IDs may be equivalent for an R3 replay class but not for exact execution provenance;
- a documentation-only file change may be irrelevant to pack manufacture only if the pack's dependency closure proves no semantic/template/gate dependency on that file;
- a toolchain patch version may be equivalent only if policy explicitly admits it.

Equivalence MUST be a proof object or policy rule, not an intuition used to avoid CI.

## 16. Invalidation

Each receipt references identity nodes. When an identity changes, compute the receipt dependency closure.

Conceptual algorithm:

```text
changed = {identity nodes whose values differ}
invalid = reachable_receipts(changed, proof_dependency_edges)
required = invalid ∩ receipts_needed_for_requested_claims
```

This yields minimum safe revalidation when the dependency graph is complete.

If dependency completeness is uncertain, the system MUST expand conservatively.

## 17. Receipt DAG invariants

A valid receipt graph SHOULD satisfy:

1. every crown-bearing receipt has an exact subject identity;
2. every artifact digest names algorithm and domain;
3. every `DO` receipt has authority evidence;
4. every replay receipt references the original or shared subject identity;
5. predecessor edges are acyclic for derivation history;
6. invalidation/revocation does not rewrite historical receipts;
7. contradictory receipts remain visible and trigger conflict resolution;
8. standing is computed from a policy version whose identity is recorded;
9. no receipt proves a broader boundary than its executed phase;
10. no missing edge is silently treated as proof.

## 18. Example: mdBook self-hosting chain

A high-fidelity receipt chain for the current book would contain separate receipts for:

1. exact PR head checked out;
2. marketplace configuration admitted;
3. admitted ggen runtime installed;
4. root consumer manufactured `book.toml` and `SUMMARY.md`;
5. generated controls replayed or otherwise checked for determinism;
6. mdBook compiler installed at the pinned version;
7. `mdbook build` accepted the exact generated controls;
8. Pages artifact uploaded on main;
9. Pages deployment returned a public deployment identity.

The first PR execution supplied steps 1–7 but intentionally skipped 8–9 because deployment authority is not granted for pull-request events.

That history is a good example of why a receipt DAG is more accurate than a single workflow badge.

## 19. Release capsule

A release capsule can be defined as:

`Capsule = (source manifest, toolchain manifest, receipts, artifacts, reproduction instructions)`.

Minimum candidate contents:

- repository commit/tree;
- marketplace admitted-config receipt;
- corpus fingerprint;
- pack archive digests;
- ggen exact version/commit/binary digest where available;
- qualification receipt DAG;
- generated catalog/archive artifacts;
- target compiler receipts for self-hosting infrastructure;
- explicit missing evidence tiers;
- reproduction commands;
- expected digests.

The capsule SHOULD be independently downloadable and verifiable without trusting a mutable branch.

## 20. Security considerations

Receipt systems create new attack surfaces.

Threats include:

- forged success receipts;
- replaying a valid receipt for a different subject;
- omitting failed receipts;
- compromising the signer/builder;
- digest ambiguity through unspecified canonicalization;
- truncating predecessor edges;
- policy downgrade;
- stale receipt reuse;
- confused-deputy authority claims;
- log retention shorter than audit requirements.

Signing helps authenticity but does not prove semantic completeness. A perfectly signed false or incomplete receipt remains false or incomplete.

## 21. Research target

The receipt system is mature when an independent verifier can ask:

> “Why is this exact artifact allowed to have this exact standing?”

and obtain a closed machine-readable proof graph whose leaves are immutable source/policy/toolchain identities and whose internal nodes are observed execution receipts.

At that point, CI ceases to be a collection of ephemeral green checks and becomes a **content-addressed evidence fabric** for semantic software manufacture.
