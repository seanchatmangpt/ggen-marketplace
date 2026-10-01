# Tutorial: flag a pack for consolidation and deprecation

A guided walk through recording two lifecycle decisions in a scratch marketplace, and watching the catalog change. Nothing here touches the real `lifecycle.toml`. For the terse recipe see [How to flag a pack's lifecycle](../how-to/flag-a-pack-lifecycle.md).

## 1. Make a scratch copy

```bash
mkdir -p /tmp/flag-tutorial && cd /tmp/flag-tutorial
cp -R "$OLDPWD/scripts" "$OLDPWD/marketplace.toml" "$OLDPWD/docs" .
mkdir packs
for n in old-pack new-pack peer-pack; do
  mkdir packs/$n
  printf '[pack]\nname = "%s"\nversion = "1.0.0"\ndescription = "Pack %s for rust cli"\n' $n $n > packs/$n/pack.toml
  printf '@prefix ex: <http://example.org/> .\n' > packs/$n/ontology.ttl
done
python3 scripts/marketplace.py validate
```

All three packs are `active`. `python3 scripts/marketplace.py lifecycle` prints nothing.

## 2. Flag one supersession and one consolidation lead

```bash
cat > lifecycle.toml <<'EOF'
schema_version = "1.0.0"

[packs.old-pack]
state = "superseded"
successors = ["new-pack"]
reason = "Absorbed by new-pack."

[packs.peer-pack]
intent = "consolidate"
related = ["new-pack"]
reason = "Generates the same target paths as new-pack."
EOF
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py lifecycle
```

You should see two lines: `old-pack superseded - new-pack ...` and `peer-pack active consolidate new-pack ...`.

## 3. Read the catalog projection

```bash
python3 scripts/marketplace.py show old-pack | grep -E '"(status|deprecated)"'
python3 scripts/marketplace.py show peer-pack | grep -A6 '"lifecycle"'
```

`old-pack` is `superseded` and `deprecated`. `peer-pack` stays `active`; its `lifecycle` object carries the `consolidate` intent.

## 3b. Break it on purpose

Change `successors = ["new-pack"]` to `["missing-pack"]` and validate:

```bash
python3 scripts/marketplace.py validate
```

Validation refuses with `REFUSED:LIFECYCLE_SUCCESSOR_UNKNOWN:old-pack:missing-pack`. A flag can never point at a pack that does not exist.

## Where to go next

- [Lifecycle registry reference](../reference/pack-lifecycle-registry.md) for every state, intent, and refusal.
- [How to consolidate a pack family](../how-to/consolidate-a-pack-family.md) for what must be proved before acting on a `consolidate` flag.
