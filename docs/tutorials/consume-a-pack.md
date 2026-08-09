# Tutorial: consume a marketplace pack

This tutorial uses a local marketplace checkout so every input is inspectable.

1. Clone or place `ggen-marketplace` beside a ggen consumer project.
2. Pick a pack and read its `pack.toml`, `ontology.ttl`, templates, gates, and README before execution.
3. Add a path dependency in the consumer `ggen.toml`:

```toml
[packs]
ggen-combinatorial-maximalism-pack = { path = "../ggen-marketplace/packs/ggen-combinatorial-maximalism-pack" }
```

4. Add the consumer RDF required by that pack.
5. Run `ggen sync run`.
6. Inspect the manufactured files and run the consumer's repository-native tests.
7. Run `ggen sync run` again and verify the projection is stable.

The marketplace tells you which pack source you selected; the ggen runtime and consumer boundary establish what that pack actually manufactures in your environment.
