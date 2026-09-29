# Tutorial: build your first ggen pack

You will create a minimal ontology-backed pack, admit it through the marketplace checks, manufacture one file with a real `ggen`, prove a fixed point, and identify what evidence is still missing before any Level-5 claim.

Every step below is executed for real by `python3 scripts/run_quickstart.py` (tested by `tests/test_quickstart.py`); the files shown are byte-identical to [`examples/hello-pack`](../../examples/hello-pack/README.md).

## 0. Install ggen

You need a `ggen` binary on `PATH`. The marketplace pins one release in `marketplace.toml` (`[ggen]`); install it with the digest-checked installer, see [Install ggen](../how-to/install-ggen.md):

```bash
export PATH="$(dirname "$(bash scripts/install-ggen.sh)"):$PATH"
ggen --version
```

## 1. Create the pack

```text
packs/hello-pack/
├── pack.toml
├── ontology.ttl
└── templates/
    └── greeting.txt.tmpl
```

`pack.toml` (the `[pack]` table admits only `name`, `version`, `description`, `deprecated`, `superseded_by`):

<!-- file: pack.toml -->
```toml
[pack]
name = "hello-pack"
version = "0.1.0"
description = "Says hello from an admitted RDF fact."
```

`ontology.ttl`:

<!-- file: ontology.ttl -->
```turtle
@prefix hp: <http://example.org/hello-pack#> .
hp:Greeting a hp:GreetingClass ; hp:text "Hello from ggen." .
```

`templates/greeting.txt.tmpl`:

<!-- file: templates/greeting.txt.tmpl -->
```text
---
to: "output/greeting.txt"
sparql:
  row: |
    PREFIX hp: <http://example.org/hello-pack#>
    SELECT ?text WHERE { hp:Greeting hp:text ?text . }
---
{{ row[0].text }}
```

The literal lives in RDF; the template is only a projection rule. The directory name must equal `[pack].name`.

## 2. Validate marketplace structure

From the marketplace root:

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py check hello-pack
```

`validate` inspects every pack under `packs/`. `check hello-pack` additionally parses the pack's Turtle and qualifies it against the real `ggen` on `PATH` (add `--no-qualify` to skip that step).

Do not rely on `catalog` or `archive` to see your new pack yet: they default to `--scope active`, the frozen set listed in `marketplace.active.toml`, which does not contain a brand-new pack. Use `python3 scripts/marketplace.py catalog --scope all` to project the whole corpus.

Fix any `REFUSED:*` result before continuing. This proves repository/pack admission only; it has not executed your consumer yet.

## 3. Wire a consumer

A consumer is a separate ggen project. `examples/hello-pack/consumer/` is a complete one. Its `ggen.toml`:

<!-- file: consumer/ggen.toml -->
```toml
[project]
name = "hello-consumer"

[ontology]
source = "ontology.ttl"

[packs]
hello-pack = { path = "../pack" }

[templates]
dir = "templates"
```

`[templates].dir` must exist (the example keeps an empty `templates/` via `.gitkeep`); ggen refuses with `FM-CONFIG-004` otherwise. Adjust `path` to point at your pack (for the marketplace checkout: `../ggen-marketplace/packs/hello-pack`). The consumer's own `ontology.ttl`:

<!-- file: consumer/ontology.ttl -->
```turtle
@prefix ex: <http://example.org/consumer#> .
ex:Consumer ex:name "hello-consumer" .
```

Run from the consumer directory:

```bash
ggen sync run
cat output/greeting.txt
```

The output is `Hello from ggen.` because that value is selected from the admitted RDF graph.

## 4. Verify the consequence

Use a consumer-native assertion rather than visual inspection when possible. For this trivial tutorial, an exact comparison is enough:

```bash
test "$(cat output/greeting.txt)" = "Hello from ggen."
```

For a real pack this boundary should be the native compiler, service test, browser test, protocol court, simulation, or other verifier that actually establishes the claimed behavior.

## 5. Prove replay/fixed point

Run manufacture again without changing semantic inputs:

```bash
cp output/greeting.txt /tmp/greeting.first
ggen sync run
cmp output/greeting.txt /tmp/greeting.first
```

The second manufacture must not change the output bytes for the fixed-point claim you intend to make. For real consumers, compose `pack-maturity-pack` and run its generated regeneration court so actual filesystem bytes are compared across repeated manufacture.

## 6. Run the whole tutorial mechanically

```bash
python3 scripts/run_quickstart.py
python3 -m pytest tests/test_quickstart.py -q
```

The script copies the example into a scratch directory, admits the pack in a scratch marketplace root, runs real `ggen sync run` twice, and exits nonzero on any failure.

## 7. Understand the maturity boundary

This minimal pack has now demonstrated a small slice:

```text
RDF source → marketplace admission → ggen manufacture → bounded verification → replay
```

It has **not** automatically demonstrated complete domain admission, negative witnesses, generated receipt validity, an external runtime boundary, authority fencing for consequential DO, class-closed composition, or Level-5 Diátaxis.

Use [the Level-5 maturity contract](../reference/level5-maturity-contract.md) instead of turning one green path into a global maturity claim.

## 8. Continue lawfully

Next steps:

- [Consume a marketplace pack](consume-a-pack.md)
- [Install ggen](../how-to/install-ggen.md)
- [Publish a pack](../how-to/publish-a-pack.md)
- [Take a pack through a Level-5 promotion slice](level5-promotion.md)
