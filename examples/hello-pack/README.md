# hello-pack example

A minimal, real pack plus the consumer project that manufactures a file from it.

```text
examples/hello-pack/
├── pack/        the pack: pack.toml, ontology.ttl, templates/greeting.txt.tmpl
└── consumer/    a ggen project: ggen.toml references ../pack by path
```

Run it:

```bash
cd examples/hello-pack/consumer
ggen sync run
cat output/greeting.txt        # Hello from ggen.
```

This directory is not under `packs/`, so it is not part of the marketplace corpus. The full
walkthrough is [Tutorial: build your first ggen pack](../../docs/tutorials/first-pack.md); the whole
flow is executed by `python3 scripts/run_quickstart.py`.

## See Also

- [First-pack tutorial](../../docs/tutorials/first-pack.md)
- [Install ggen](../../docs/how-to/install-ggen.md)
