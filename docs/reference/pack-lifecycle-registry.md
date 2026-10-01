# Reference: pack lifecycle registry

`lifecycle.toml` at the repository root is the canonical source for per-pack lifecycle **state** and planned **intent**. The catalog derives `status`, `deprecated`, `successors`, and `lifecycle` from it; nothing else is hand-maintained.

It lives outside `pack.toml` because the real ggen loader deserializes `[pack]` with deny-unknown-fields, so extra lifecycle keys are refused at pack-load time (see the comment in `packs/clap-noun-verb-pack/pack.toml`). A missing `lifecycle.toml` is an empty registry, not an error.

For the procedure see [How to flag a pack's lifecycle](../how-to/flag-a-pack-lifecycle.md); for rationale see [Pack lifecycle](../explanation/pack-lifecycle.md).

## File shape

```toml
schema_version = "1.0.0"

[packs.<pack-name>]
state      = "deprecated"            # optional, default "active"
intent     = "replace"               # optional
successors = ["<pack-name>", ...]    # optional list
related    = ["<pack-name>", ...]    # optional list
reason     = "one or two sentences"  # required on every entry
since      = "v26.9.29"              # optional marketplace version tag
evidence   = ["docs/....md"]         # optional repo-relative paths that must exist
```

Each `[packs.<name>]` key must be an existing directory under `packs/`. TOML itself rejects a duplicate key.

## Two independent axes

**`state`** is what the pack is now. It changes how consumers should treat it.

| state | meaning | `successors` |
|---|---|---|
| `active` | normal; the default | not required |
| `deprecated` | still resolvable; discouraged; new work should not start on it | recommended |
| `superseded` | a named successor fully covers it; kept for path-pinned consumers | required |
| `retired` | removed from normal discovery; bytes kept on disk | required |

**`intent`** is a review flag: what we plan. It is advisory and never changes `ggen sync run` output, archive bytes, digests, or fingerprints.

| intent | meaning | requires |
|---|---|---|
| `consolidate` | duplicate truth with the `related` peers; follow [the consolidation procedure](../how-to/consolidate-a-pack-family.md) | `related` |
| `keep-separate` | compared with `related` peers and proved non-equivalent; recorded so the pair is not re-flagged | `related`, state `active` |
| `replace` | a successor is planned or exists | `successors` |
| `upgrade` | needs in-place work (drifted pin, failing baseline, reuse smell); no successor implied | `reason` |
| `review` | a lead that has not been verified; do not act on it | `reason` |

`state` and `intent` combine freely except where stated. `state = "active"` with no `intent` carries no information and is refused.

## Refusals

`python3 scripts/marketplace.py validate` refuses, with `REFUSED:<CODE>:<detail>`:

| code | condition |
|---|---|
| `LIFECYCLE_TOML_INVALID` | file is not valid TOML |
| `LIFECYCLE_SCHEMA_VERSION` | `schema_version` is not `1.0.0` |
| `LIFECYCLE_PACKS_TYPE`, `LIFECYCLE_ENTRY_TYPE` | `packs` or an entry is not a table |
| `LIFECYCLE_PACK_UNKNOWN` | entry names a pack that does not exist |
| `LIFECYCLE_KEY_UNKNOWN` | entry has a key outside the table above |
| `LIFECYCLE_STATE_UNKNOWN`, `LIFECYCLE_INTENT_UNKNOWN` | value outside the vocabularies above |
| `LIFECYCLE_ENTRY_EMPTY` | `active` with no `intent` |
| `LIFECYCLE_REASON_MISSING` | no non-blank `reason` |
| `LIFECYCLE_SINCE_FORMAT` | `since` is not `vMAJOR.MINOR.PATCH` |
| `LIFECYCLE_SUCCESSOR_REQUIRED` | `superseded`/`retired` without `successors` |
| `LIFECYCLE_SUCCESSORS_REQUIRED` | `intent = "replace"` without `successors` |
| `LIFECYCLE_RELATED_REQUIRED` | `consolidate`/`keep-separate` without `related` |
| `LIFECYCLE_SUCCESSOR_SELF`, `LIFECYCLE_RELATED_SELF` | a pack names itself |
| `LIFECYCLE_SUCCESSOR_UNKNOWN`, `LIFECYCLE_RELATED_UNKNOWN` | names a pack that does not exist |
| `LIFECYCLE_SUCCESSOR_NOT_LIVE` | a successor is itself `superseded` or `retired`; point at the live successor |
| `LIFECYCLE_SUCCESSORS_TYPE`, `LIFECYCLE_RELATED_TYPE`, `LIFECYCLE_EVIDENCE_TYPE` and `_DUPLICATE` | list is not a list of non-blank unique strings |
| `LIFECYCLE_EVIDENCE_MISSING` | an `evidence` path does not exist under the repository |
| `LIFECYCLE_KEEP_SEPARATE_STATE` | `keep-separate` on a non-`active` pack |
| `LIFECYCLE_MANIFEST_CONFLICT` | `pack.toml` carries legacy `deprecated`/`superseded_by` while the registry says `active` |

## Catalog projection

For a pack with a registry entry, `status` is the `state`, `deprecated` is `state != "active"`, and `successors` is the entry's list. Packs with no entry fall back to the legacy `pack.toml` `deprecated`/`superseded_by` keys, so existing manifests keep working; when both exist the registry wins and a contradiction is refused.

Every catalog record also carries `lifecycle`: `null` when there is no entry, otherwise `{evidence, intent, reason, related, since}`.

```bash
python3 scripts/marketplace.py lifecycle                        # every pack with lifecycle information
python3 scripts/marketplace.py lifecycle --state superseded
python3 scripts/marketplace.py lifecycle --intent consolidate
python3 scripts/marketplace.py show <pack>                      # full record including `lifecycle`
```

`lifecycle` prints `name status intent links reason`, where `links` is the successors, or the `related` peers when there are none.

## What the registry does not do

- It does not delete, move, or rewrite packs, and it does not merge them.
- A flag is a claim with a `reason`, not evidence of equivalence. `consolidate` and `replace` are lawful to act on only after the [consolidation procedure](../how-to/consolidate-a-pack-family.md) has produced its receipt.
- `superseded`/`retired` do not prove that consumers have migrated; that evidence is separate.
- Class assignment stays in `PACK_CLASSES` ([pack classes](pack-classes.md)); it is an orthogonal axis.

## See Also

- [Catalog command](catalog-command.md)
- [Pack contract](pack-contract.md)
- [Pack classes](pack-classes.md)
