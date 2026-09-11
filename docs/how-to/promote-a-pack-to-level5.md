# How to promote a pack to Level 5

Use this guide when a pack already exists and you want to close its maturity gaps without manufacturing evidence it does not have.

## 1. Resolve the exact subject

Record the repository, base SHA, working branch, pack name/version/profile, and dependency set before changing source. Do not silently move the base during qualification.

Inspect at least:

```text
packs/<name>/pack.toml
packs/<name>/**/*.ttl
templates/
gates/
qualification/
ggen.toml        # when present
README.md         # when present
```

Classify every claim as observed, admitted, executed, changed, verified, inferred, refused, blocked, or unsupported.

## 2. Score the 5 × 7 matrix

Use [the Level-5 maturity contract](../reference/level5-maturity-contract.md). Score the pack independently on:

1. semantic source;
2. admission;
3. manufacture;
4. execution;
5. receipt/replay;
6. authority fence;
7. composition.

Do not average the scores. One missing consequential dimension remains a missing dimension.

## 3. Close semantic authority first

Put domain meaning in canonical RDF or another explicitly admitted semantic source rather than in generated files or duplicated README prose. Reuse public ontologies when they carry the required concept; add pack-specific vocabulary only for the semantic delta.

If a generated artifact disagrees with semantic source, repair the source/query/template/gate path and regenerate. Do not bless the generated drift.

## 4. Add fail-closed admission and negative witnesses

Encode invalid states as deterministic gates, schemas, formal checks, or bounded verifier programs. Add at least one real negative witness for each important refusal family.

A Level-5 negative witness should demonstrate that the intended invalid subject is rejected; it is not enough for the refusal string to exist in source.

## 5. Prove deterministic manufacture

Compose `pack-maturity-pack` where compatible with the consumer. Run the real ggen manufacturing path twice with unchanged admitted inputs and compare the actual consequence bytes.

At minimum:

```bash
ggen sync run
ggen sync run
```

Prefer the generated fixed-point court supplied by `pack-maturity-pack` because it snapshots actual filesystem consequences rather than trusting self-reported write/skip status.

## 6. Exercise the real consumer/runtime boundary

Marketplace qualification proves bounded pack loading/manufacture/replay. It does not automatically prove the generated program, service, workflow, Terraform plan, MCP implementation, or domain behavior.

Run the narrowest repository-native court that reaches the boundary you intend to claim. Examples include a compiled CLI invocation, service integration test, browser test, simulation episode, Terraform plan verifier, or exact protocol exchange.

If the required external authority is unavailable, record `BLOCKED:<typed reason>` or `UNSUPPORTED`; do not replace execution with a mock and promote it to ALIVE.

## 7. Bind receipt and replay

Run the applicable receipt verifier. For ggen consumers using the standard receipt path:

```bash
ggen receipt verify
```

The receipt should bind source identity, admitted inputs, manufacturer/toolchain identity, consequence identity, authority ceiling, execution evidence, and replay relationship.

## 8. Close Diátaxis

A Level-5 pack needs the four quadrants:

- **Tutorial** — executable guided journey;
- **How-to** — operational recipes with authority ceiling/falsifiers/rollback;
- **Reference** — exact semantic/configuration/gate/generated/receipt/dependency contract;
- **Explanation** — rationale, fences, exclusions, falsifiers, extensions.

Use `pack-maturity-pack` to generate the common Level-5 shape. Replace or extend generic sections only with domain facts that are actually admitted. Do not copy generic marketplace doctrine into dozens of pack READMEs when a shared reference is sufficient.

## 9. Close composition and consolidation

Identify whether the pack is a kernel, capability module, profile/world, compatibility pack, evidence pack, or release-control pack. If multiple siblings duplicate the same protocol truth, lifecycle law, maturity law, authority law, or projection grammar, consolidate that truth into a canonical class/kernel and leave only domain/profile deltas in the siblings.

Do not physically merge independent runtimes or domain worlds merely because names are similar. Require an equivalence proof before deleting semantic authority.

See [How to consolidate a pack family](consolidate-a-pack-family.md).

## 10. Run marketplace acceptance

From the marketplace root:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

Then run the pack's domain/consumer court and the generated Level-5 documentation court.

## 11. Publish the receipt, not just the diff

A promotion PR should state:

- exact base/head SHA;
- changed semantic/manufacturing surfaces;
- generated status;
- commands and exits;
- positive and negative witnesses;
- receipt/replay result;
- authority ceiling;
- consolidation/composition impact;
- falsifiers and rollback;
- scoped standing.

`ALIVE` is only appropriate for the exact boundary actually executed. If repository CI is still running, use `PARTIAL_ALIVE / REQUALIFYING`; if a required court cannot run because authority is absent, keep the corresponding boundary `BLOCKED`.
