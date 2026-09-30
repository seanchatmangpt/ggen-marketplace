# How to flag a pack's lifecycle

Use this to record that a pack should be consolidated, upgraded, replaced, or deprecated, or that a suspected overlap was checked and ruled out. The contract is in [the lifecycle registry reference](../reference/pack-lifecycle-registry.md).

## 1. Choose the smallest truthful flag

| You know | Flag |
|---|---|
| a lead, unverified | `intent = "review"` |
| verified duplicate truth with named peers | `intent = "consolidate"`, `related = [...]` |
| verified non-equivalence with a named peer | `intent = "keep-separate"`, `related = [...]` |
| needs in-place work | `intent = "upgrade"` |
| a named successor exists or is planned | `intent = "replace"`, `successors = [...]` |
| a named successor fully covers it and consumers are being moved | `state = "deprecated"` |
| consumers migrated; kept only for path-pinned resolution | `state = "superseded"` |

Prefer the weakest row that matches what you actually verified. Do not set `state` beyond `active` without an exactly-named live successor.

## 2. Add the entry

Edit `lifecycle.toml` (keep entries sorted by pack name):

```toml
[packs.noun-verb-cli-pack]
state = "superseded"
successors = ["ex-noun-verb-cli-pack"]
reason = "Renamed; 4-file subset of the successor with only the nvc: namespace IRI changed."
since = "v26.9.29"
evidence = ["packs/ex-noun-verb-cli-pack/README.md"]
```

`reason` is mandatory and should say what you checked, not what you suspect. Point `evidence` at repo files that support it.

## 3. Validate

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py lifecycle --state superseded
python3 -m pytest tests/test_lifecycle_registry.py -q
```

Validation refuses dangling names, missing successors, successors that are themselves superseded or retired, and missing evidence paths.

## 4. Act on the flag separately

The flag records a decision; it does not perform it. To physically consolidate, follow [How to consolidate a pack family](consolidate-a-pack-family.md) and publish its receipt. To retire discovery, check the consumer inventory first. Keep the flag change and the consolidation change in separate commits so either can be rolled back.

## 5. Clear a flag when its cause is gone

Delete the entry when an upgrade lands or a review concludes. If the review concluded the packs are not equivalent, replace it with `intent = "keep-separate"` so the pair is not re-flagged.

## Changing a pack's version

Flags do not alter pack bytes, so they do not require a pack version bump. The work the flag points at (the upgrade, the consolidation) does.
