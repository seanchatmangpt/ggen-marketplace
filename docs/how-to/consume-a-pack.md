# How to consume a pack

Reference the selected pack from the consumer project's `ggen.toml` using a local path or another transport supported by the ggen version you have admitted. For a local checkout:

```toml
[packs]
my-pack = { path = "../ggen-marketplace/packs/my-pack" }
```

Before running ggen, inspect the pack source and any gates. After `ggen sync run`, validate the generated artifacts with the consumer's native compiler/tests and rerun sync to check stability. Do not treat marketplace CI as proof of the consumer consequence.
