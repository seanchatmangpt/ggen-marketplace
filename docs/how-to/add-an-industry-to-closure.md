# How to add an industry to a closure

Use this procedure to bring a new bounded industry into the industry-closure calculus as a sibling ProfilePack. The profile is data over the kernel vocabulary: it never adds a kernel, never ships building blocks, and never grants authority. Exact contracts are in [Industry closure contract](../reference/industry-closure-contract.md) and [Enterprise operating model contract](../reference/enterprise-operating-model-contract.md); the worked example is `industry-closure-retail-lending-profile-pack`.

Prerequisites: a branch (never write to `main`), and a clean understanding that this procedure produces candidate source for human review, with no consequential action.

## 1. Bound the industry

Write one sentence for the scope and choose a path prefix under `ontologies/public/` that the scope's sources must live inside. The closure individual carries them:

```text
ic:IndustryClosure
  ic:industryScope     "<one bounded scope>"
  ic:baseIri           "<base IRI ending in a slash>"
  ic:boundPathPrefix   "ontologies/public/<family>/"
  ic:hasSnapshot       <epoch-0 snapshot>
  ic:usesSource        <each source, in any admission state>
```

Add the epoch-0 snapshot (`ic:epoch 0`, `ic:snapshotOf` the closure). The closure starts empty, so it records no coverage.

## 2. Admit each public source as a `ic:KnowledgeSource`

A source enters the closure through exactly one of three admissions.

**ADMITTED.** Requires all of: source IRI, version, digest, licence boundary, locator.

1. Vendor the file under `ontologies/public/` inside the closure's path prefix. Do not edit the vendored file.
2. Compute its digest and record it as `sha256:` plus 64 lowercase hex:

   ```bash
   sha256sum ontologies/public/<family>/<file>.rdf
   ```

3. Read the ontology IRI, version IRI and licence statement from the file itself. Do not copy them from documentation, and do not paraphrase the licence into something wider than the file states.
4. Record the licence boundary as the terms under which you vendor and use it. If the licence boundary is unclear, do not admit.
5. Record the locator, repository-relative, starting with `ontologies/public/` and inside the prefix.

**EXCLUDED.** The source was considered and is outside the scope. Record an `ic:exclusionReason`.

**UNKNOWN.** The source is not yet reviewed. Record an `ic:falsifier`: the condition that would prove the current decision wrong and force a review.

Run gate `010_source_admission.rq` under rdflib (see step 7). Its typed refusals tell you which of the above is missing.

## 3. Write requirements

For each atomic need, write an `ic:Requirement`:

- a safe `ic:requirementId` matching `^[A-Za-z0-9._-]+$`, unique;
- a paraphrased `ic:statement` of one need only;
- `ic:inClosure` and an explicit `ic:disposition` of `ic:IN_SCOPE` or `ic:OUT_OF_SCOPE`;
- for `ic:OUT_OF_SCOPE`, an `ic:scopeJustification`; nothing may leave the residual silently;
- for `ic:IN_SCOPE`, an admitted origin: `ic:derivedFrom` an ADMITTED source, or `ic:originAuthority` an `ea:Strategy`;
- `ic:requiresCapability` pointing at a capability individual.

If a requirement needs consequential authority, record `ic:needsDoAuthority true`. That is a need, not a grant: the requirement will classify as the authority deficit with standing `BLOCKED` permanently. Do not try to make it disappear.

Paraphrase only. Do not paste text from a standard or book into a statement.

## 4. Define capabilities

Each capability is an `ea:Capability` individual with an `ic:capabilityKey` (safe key), `ic:groundedIn` an ADMITTED source, and `ic:concept` an IRI of a class that source defines. The class must really exist in the vendored file as an `owl:Class`; the profile court parses the RDF and checks. A capability with no grounding is the ontology deficit and routes upstream to knowledge.

Add no building blocks, solution building blocks, coverages, evidence or receipts. The honest starting residual of a new profile is an architecture deficit for every in-scope requirement, plus the blocked authority row if any.

## 5. Choose the operating-model decision (optional, enterprise-side)

If the closure serves a particular enterprise, supply the strategy-derived side in the consumer's enterprise input, not in the profile:

1. An `ea:Strategy` with `eom:ofEnterprise`.
2. An `eom:OperatingModelDecision` with a safe `eom:decisionKey`, `eom:forStrategy`, one `eom:chosenModel`, the matching `eom:integrationLevel` and `eom:standardizationLevel`, `eom:targetClosure` and an `eom:targetBaseIri` equal to the closure's base IRI, and `dcterms:source`.
3. A foundation with at least one core process, shared data domain and linking automation. Each element has a safe `eom:elementKey` and `eom:supportsCapability` pointing at one of the profile's capabilities. This is how an enterprise's foundation ties to the industry.
4. An engagement model whose three mechanisms join to `ENG-` notations in `togaf-adm-pack`.

Pick the model from the axes you can defend; the gates enforce consistency with the axes you state, not that the axes were the right strategic choice. See [the explanation](../explanation/industry-closure-as-architecture-strategy.md).

## 6. Scaffold the sibling ProfilePack

```bash
python3 scripts/new_pack.py industry-closure-<industry>-profile-pack --profile semantic
```

Then:

1. Put the ABox from steps 1 to 4 in `ontology.ttl` (a profile has no templates and no `ggen.toml`, so its derived profile is semantic).
2. Keep `[pack]` to `name`, `version` and `description` only. Read the version from the current release line in the catalog rather than copying one from this page.
3. Replace the scaffold's skeleton gate with a profile gate that checks grounding in your own sources (the retail-lending pack's `010_profile_grounding.rq` is the model), and keep witness stems identical to gate stems. Every `REFUSED:` literal the gate declares needs a failing witness that triggers it.
4. Record the golden starting residual in `qualification/expected-residual.json` from the kernel query, not by hand.
5. Do not add the pack to `marketplace.active.toml`; it appears under `--scope all`.
6. Do not hand-maintain a second catalog. Do not edit the vendored sources. No symlinks below `packs/`.

## 7. Prove it

```bash
python3 scripts/marketplace.py check industry-closure-<industry>-profile-pack --no-qualify
python3 scripts/check_gate_witness_courts.py --packs packs
python3 scripts/check_cross_pack_references.py --mode gate
python3 -m pytest tests/test_industry_closure_profile.py -q
```

Run the kernel gates 010, 020, 030, 060, 070, 080, 090 and 100 over the kernel ontology plus your profile and confirm zero rows, with the recorded residual equal to the computed one. Section 8 wires the profile into a consumer. Without a ggen binary, manufacture and replay are `BLOCKED:ggen_binary_unavailable`; do not claim more. Marketplace CI alone is insufficient evidence for generated behaviour.

## 8. Wire the profile into a consumer

The kernel's `ggen.toml` reads only one input: `ontology/industry-input.ttl`, which ships empty. A profile reaches the kernel by being placed at that path in a consumer; nothing else connects them. The profile's `ontology.ttl` is flat Turtle for exactly this reason.

```bash
scratch=$(mktemp -d)
cp -R packs/industry-closure-pack/. "$scratch"/
cp packs/industry-closure-<industry>-profile-pack/ontology.ttl "$scratch/ontology/industry-input.ttl"
(cd "$scratch" && ggen sync run && ggen sync run)
```

Pass 1 (`enterprise-operating-model-pack`) is optional for a pure profile; when you use it, its generated requirements are appended to the kernel's imports as the kernel's `ggen.toml` comment describes. Then check, in this order:

1. The second run changed nothing: byte-compare every file under `generated/` between the two runs. This is the replay check, and a difference is a refusal, not a warning.
2. `generated/industry-closure/residual-ledger.ttl` has one residual per row of the profile's `qualification/expected-residual.json`, with the same keys and classes.
3. The generated files pass the kernel gates when merged into the consumer's input (gates 060, 070, 080 and 100 over the ledger and the work orders).

`tests/test_industry_closure_profile.py` rehearses the wiring under rdflib: it builds the scratch consumer, reads the kernel's `ggen.toml` source and imports, and runs every rule's query over the result. That rehearsal shows the paths and queries line up. It is not a ggen run. In this repository only the synthetic qualification overlay is consumed by a real ggen, so the golden residual of a real profile is rdflib-only evidence, and manufacture from the real profile is `UNKNOWN` or `BLOCKED:ggen_binary_unavailable` until the commands above are run on the exact subject.

## 9. When an umbrella becomes warranted

Do not create an umbrella pack for a single profile. An umbrella is warranted when at least two profile packs share a common bundle that consumers keep composing together, and then only after the class-closure procedure in [Consolidate a pack family](consolidate-a-pack-family.md) and the classes in [Pack classes](../reference/pack-classes.md). Later industries are always siblings of the same shape, never new kernels, and similar names are not equivalence proof.

## Boundaries

- This procedure proves the bounded qualification boundary of the new profile only.
- A profile carries no ambient DO authority. A requirement that needs it stays blocked.
- Documentation changes for a new profile must update the four quadrants together; do not hand-edit generated navigation. See [Validate locally](validate-locally.md).
