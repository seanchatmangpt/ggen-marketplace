# How to consume a pack

Recipe for wiring a pack into a consumer project. For a step-by-step learning walk with a runnable example, see [Tutorial: consume a marketplace pack](../tutorials/consume-a-pack.md).

## Reference the pack

In the consumer's `ggen.toml`, using a local marketplace checkout:

```toml
[packs]
my-pack = { path = "../ggen-marketplace/packs/my-pack" }
```

The consumer also needs `[project]`, `[ontology]`, and an existing `[templates].dir`; see the complete file in [`examples/hello-pack/consumer`](../../examples/hello-pack/consumer/ggen.toml). Add only the consumer facts the pack contract requires, then `ggen sync run`.

## Resolve source identity first

The pack name is not an exact subject. Record the marketplace revision (`git rev-parse HEAD`) and `ggen --version` before execution.

## Fetch without a local checkout

Every admitted published pack has a deterministic archive whose URL and digest are projected by the catalog. Read current values from executable source, never from prose:

```bash
python3 scripts/marketplace.py catalog --scope all
```

`catalog` defaults to `--scope active` (the frozen active set); use `--scope all` for every pack. Verify the archive digest **before** extraction. A published archive proves distribution identity, not consumer behavior.

## Verify

Check behavior with the consumer's native compiler/tests/protocol/simulation, not file existence. Prove replay by running `ggen sync run` again and comparing bytes. When the consumer uses receipts, run `ggen receipt verify`. For Level-5 work compose `pack-maturity-pack` so fixed-point and receipt checks are generated consistently.

## Authority boundary

A consumed pack may manufacture Terraform, GitHub Actions, MCP/API intents, deployment specifications, or other artifacts. Manufacture remains CONSTRUCT unless the consumer has a separately admitted consequential DO path. Never infer execution authority from pack publication, catalog membership, a generated artifact, or a successful marketplace qualification run.

## Standing

State separately: marketplace pack/source standing; ggen manufacture/replay standing; consumer runtime standing; external actuation standing. A green marketplace rail cannot substitute for the consumer boundary, and a green consumer simulation cannot silently become production authority.

## See Also

- [Tutorial: consume a marketplace pack](../tutorials/consume-a-pack.md)
- [Install ggen](install-ggen.md)
- [Level-5 maturity contract](../reference/level5-maturity-contract.md)
