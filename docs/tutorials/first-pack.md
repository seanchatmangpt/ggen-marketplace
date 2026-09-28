# Tutorial: build your first ggen pack

You will create a minimal ontology-backed pack, validate its marketplace shape, manufacture one file with ggen, prove a fixed point, and identify what evidence is still missing before any Level-5 claim.

## 1. Create the pack

```text
packs/hello-pack/
├── pack.toml
├── ontology.ttl
└── templates/
    └── greeting.txt.tmpl
```

`pack.toml`:

```toml
[pack]
name = "hello-pack"
version = "0.1.0"
description = "Says hello from an admitted RDF fact."
```

`ontology.ttl`:

```turtle
@prefix hp: <http://example.org/hello-pack#> .
hp:Greeting a hp:GreetingClass ; hp:text "Hello from ggen." .
```

`templates/greeting.txt.tmpl`:

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

The literal lives in RDF; the template is only a projection rule.

## 2. Validate marketplace structure

From the marketplace root:

```bash
python3 scripts/marketplace.py validate
```

Fix any `REFUSED:*` result before continuing. This proves repository/pack admission only; it has not executed your consumer yet.

## 3. Wire a consumer

In a disposable ggen consumer project:

```toml
[packs]
hello-pack = { path = "../ggen-marketplace/packs/hello-pack" }
```

Run:

```bash
ggen sync run
cat output/greeting.txt
```

The output should be `Hello from ggen.` because that value is selected from the admitted RDF graph.

## 4. Verify the consequence

Use a consumer-native assertion rather than visual inspection when possible. For this trivial tutorial, an exact comparison is enough:

```bash
test "$(cat output/greeting.txt)" = "Hello from ggen."
```

For a real pack this boundary should be the native compiler, service test, browser test, protocol court, simulation, or other verifier that actually establishes the claimed behavior.

## 5. Prove replay/fixed point

Run manufacture again without changing semantic inputs:

```bash
ggen sync run
```

The second manufacture must not create a semantic or byte-level consequence change for the fixed-point claim you intend to make. For real consumers, compose `pack-maturity-pack` and run its generated regeneration court so actual filesystem bytes are compared across repeated manufacture.

## 6. Understand the maturity boundary

This minimal pack has now demonstrated a small slice:

```text
RDF source → marketplace admission → ggen manufacture → bounded verification → replay
```

It has **not** automatically demonstrated complete domain admission, negative witnesses, generated receipt validity, an external runtime boundary, authority fencing for consequential DO, class-closed composition, or Level-5 Diátaxis.

Use [the Level-5 maturity contract](../reference/level5-maturity-contract.md) instead of turning one green path into a global maturity claim.

## 7. Continue lawfully

Next steps:

- [Consume a marketplace pack](consume-a-pack.md)
- [Publish a pack](../how-to/publish-a-pack.md)
- [Take a pack through a Level-5 promotion slice](level5-promotion.md)
