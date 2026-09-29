# How to scaffold a pack

`scripts/new_pack.py` creates a pack that passes `marketplace.py check` on first run.

## 1. Scaffold

```bash
python3 scripts/new_pack.py my-new-pack --profile semantic|projection|project [--dir packs]
```

Names are kebab-case (`[a-z][a-z0-9-]*`). An existing directory or an invalid name is refused
with a typed `REFUSED:` line and a non-zero exit; nothing is written.

## 2. What you get

Every profile receives `pack.toml` (only `name`, `version`, `description`), a parseable
`ontology.ttl`, one gate `gates/010_subject_identity.rq`, matching `witnesses/pass` and
`witnesses/fail` cases, a `gate-court.toml` (`case_key = "exact-stem"`), and a `README.md`.

- `semantic`: the common files only.
- `projection`: adds `templates/subject-count.txt.tmpl`.
- `project`: adds `ggen.toml`, `queries/10-subjects.rq` and `templates/subjects.txt.tera`.

Sources live in `scaffolds/pack-skeleton/`; edit them to change what every new pack starts with.

## 3. Prove it

```bash
python3 scripts/marketplace.py check my-new-pack
python3 scripts/check_gate_witness_courts.py
```

`check` runs validation, the Turtle syntax check and real ggen qualification (two-pass replay).

## 4. Replace the placeholders

Rewrite the description, ontology, gate and witnesses for the real domain claim before publishing;
see [How to publish a pack](publish-a-pack.md).

## See Also

- [How to publish a pack](publish-a-pack.md)
- [Pack contract](../reference/pack-contract.md)
