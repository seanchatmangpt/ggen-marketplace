# Tutorial: build your first ggen pack

You will create a minimal pack, validate its marketplace shape, and use ggen to manufacture one file from RDF.

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

## 2. Validate marketplace structure

```bash
python3 scripts/marketplace.py validate
```

Fix any `REFUSED:*` result before continuing.

## 3. Wire a consumer

In a separate ggen consumer project:

```toml
[packs]
hello-pack = { path = "../ggen-marketplace/packs/hello-pack" }
```

Run:

```bash
ggen sync run
cat output/greeting.txt
```

The output should be `Hello from ggen.` because that literal is admitted in RDF.

## 4. Prove replay

Run `ggen sync run` again. The second run should not create a semantic change. You have now exercised the core pack loop: admitted fact → template projection → deterministic consumer artifact.

Next: [Publish a pack](../how-to/publish-a-pack.md).
