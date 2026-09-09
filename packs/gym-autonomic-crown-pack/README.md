# gym-autonomic-crown-pack

Makes `gym-ecosystem/artifacts/autonomic-crown.json` a **generated** receipt
instead of a hand-reconciled one, without taking any actuation authority.

v26.8.28 · verified against ggen 26.8.28

## Quick reference

| Piece | Path |
| --- | --- |
| Vocabulary (sosa/prov/dcat-grounded) | `ontology.ttl` |
| Read-only git observer | `bin/crown-observe.py` |
| Gate runner (violation-SELECT semantics) | `bin/run-gates.py` |
| One-shot driver | `bin/crown-generate.sh` |
| Receipt template (byte-exact v2 crown) | `templates/autonomic_crown.json.tmpl` |
| Human drift ledger | `templates/crown_drift_ledger.md.tmpl` |
| Gates | `gates/010..040*.rq` |
| Negative fixture | `tests/fixtures/tampered-crown.ttl` |

## Run it

```bash
bash bin/crown-generate.sh /Users/sac/gym-ecosystem /tmp/crown-work
```

Live mode issues 13 real `git ls-remote --symref` calls (~10s) plus one
`git ls-tree` per declared submodule. To reproduce offline from an existing
receipt instead:

```bash
bash bin/crown-generate.sh /Users/sac/gym-ecosystem /tmp/crown-work \
  --from-receipt /Users/sac/gym-ecosystem/artifacts/autonomic-crown.json
```

## Why the template is byte-exact

The real reconciler writes `json.dumps(doc, indent=2, sort_keys=True) + "\n"`.
`templates/autonomic_crown.json.tmpl` reproduces that exact serialization:
alphabetically ordered keys at both levels, two-space indent, edges ordered by
`ORDER BY ?path` (matching the script's `sorted(..., key=path)`), booleans
carried as `"true"`/`"false"` string literals in RDF so they render unquoted
and lowercase, and a single trailing newline. This matters: a receipt that
differs only in whitespace would make every regeneration look like drift.

## What it does not do

No `git checkout`, `commit`, `push`, `submodule update`, or
`ecosystem.lock.toml` write. Authority boundary is `gitlinks+lock-only` and
observation-only; consequential DO stays behind the superproject's
GymAct/BRCE-admitted crown workflow. See `PROVENANCE.md`.

## See also

- `PROVENANCE.md` — term-by-term grounding in the real repo surfaces
- `repo-reconciliation-pack` — the as-found/as-desired delta vocabulary this
  pack's drift states specialize for the submodule-gitlink case
