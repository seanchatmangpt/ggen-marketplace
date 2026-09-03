# How to publish a pack

## 1. Establish identity and semantic authority

Create `packs/<name>/pack.toml` with matching name, SemVer version, and a non-empty description. Add admitted RDF source at the pack root or under `ontology/`.

Do not put canonical domain facts only in templates, generated output, or README prose.

## 2. Add manufacture and admission surfaces

If the pack projects files, add `.tmpl` or `.tera` templates under `templates/`. A semantic-only pack may omit templates. A self-contained project pack may use `ggen.toml` and its own rules/queries.

Add `gates/*.rq` for native SPARQL refusals or bounded `gates/*.py` verifier programs only when the pack contract needs them. Encode meaningful invalid states with typed, deterministic refusals and pack-owned negative witnesses where possible.

## 3. Classify the pack

Packaging profile and semantic class are different:

- profile: `projection`, `semantic`, or `project`;
- class: kernel, capability, profile/world, compatibility, evidence, release-control, or umbrella.

See [Pack classes](../reference/pack-classes.md). If the new pack duplicates a sibling's semantic authority, factor the shared class/kernel before adding another copy.

## 4. Close documentation at the claimed maturity

At minimum, document identity, semantic source, generated surfaces, gates/refusals, dependencies, and the evidence boundary.

For Level-5 promotion, provide all four Diátaxis quadrants and their proof obligations. Prefer composing `pack-maturity-pack` for reusable mechanical scaffolding rather than duplicating generic maturity prose across packs.

## 5. Run marketplace admission

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
```

Do not hand-edit a marketplace catalog; it is a deterministic projection of admitted manifests.

## 6. Exercise real manufacture and replay

For generation behavior, run the matching ggen runtime against a representative admitted consumer subject. Run manufacture twice and verify the actual consequence is stable.

Run the consumer's native verifier for the behavior you intend to claim. Marketplace qualification does not automatically prove the generated application/service/workflow/domain consequence.

## 7. Verify receipts and authority boundaries

When the consumer uses ggen receipts, run:

```bash
ggen receipt verify
```

State whether the pack only SELECTs/CONSTRUCTs or whether a separate consumer runtime can reach DO. Generated Terraform, workflow, MCP, API, or deployment artifacts do not receive execution authority from publication.

## 8. Publish through an exact-subject PR

Use a purpose branch. The PR receipt should include:

- exact base/head SHA;
- pack/version/profile/class;
- semantic and generated surfaces changed;
- commands and exit codes;
- positive/negative witnesses;
- replay/receipt results;
- Diátaxis/maturity status;
- authority ceiling;
- consolidation/compatibility impact;
- falsifiers and rollback;
- scoped standing.

A queued workflow or authored test does not justify `ALIVE`. Wait for exact-subject execution before promoting standing.

See [How to promote a pack to Level 5](promote-a-pack-to-level5.md).
