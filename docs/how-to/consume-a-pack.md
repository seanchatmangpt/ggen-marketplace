# How to consume a pack

Reference the selected pack from the consumer project's `ggen.toml` using a local path or another transport supported by the admitted ggen version. For a local checkout:

```toml
[packs]
my-pack = { path = "../ggen-marketplace/packs/my-pack" }
```

## Resolve source identity first

Before execution, record the marketplace revision and inspect the pack's manifest, RDF source, gates, templates/project rules, qualification fixtures, documentation, and dependencies. The pack name is not enough to identify an exact subject.

## Fetching without a local checkout

Every admitted published pack may be represented by a deterministic archive with URL/digest information projected by the marketplace catalog. Obtain the current values from:

```bash
python3 scripts/marketplace.py catalog
```

Verify the archive digest **before** extraction. Do not copy a digest/version from prose when executable catalog/configuration source is available.

A published archive proves distribution identity; it does not prove consumer behavior.

## Manufacture

Add only the consumer facts/inputs required by the pack contract, then run:

```bash
ggen sync run
```

Generated files are consequences. Inspect them, but verify the behavior with the consumer's native compiler/tests/protocol/simulation court rather than treating existence as correctness.

## Replay and receipts

Run manufacture again without changing admitted inputs and prove the consequence converges. When the consumer uses ggen receipts:

```bash
ggen receipt verify
```

For Level-5 work, prefer composing `pack-maturity-pack` so fixed-point and receipt checks are generated consistently.

## Authority boundary

A consumed pack may manufacture Terraform, GitHub Actions, MCP/API intents, deployment specifications, or other artifacts. Manufacture remains CONSTRUCT unless the consumer has a separately admitted consequential DO path.

Never infer execution authority from pack publication, catalog membership, a generated artifact, or a successful marketplace qualification run.

## Standing

State separately:

- marketplace pack/source standing;
- ggen manufacture/replay standing;
- consumer runtime standing;
- external actuation standing.

A green marketplace rail cannot substitute for the consumer boundary, and a green consumer simulation cannot silently become production authority.

See [Tutorial: consume a pack](../tutorials/consume-a-pack.md) and [Level-5 maturity contract](../reference/level5-maturity-contract.md).
