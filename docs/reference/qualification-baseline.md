# Qualification baseline

`qualification/baseline.json` records the per-pack outcome of a real
`scripts/qualify_packs.py` run, and `scripts/warn_ratchet.py` refuses any
change that makes the corpus worse. It is a ratchet: WARN may only fall.

## Contents

- [Baseline format](#baseline-format)
- [Commands](#commands)
- [Ratchet rules](#ratchet-rules)
- [Qualifying a subset](#qualifying-a-subset)

## Baseline format

```json
{
  "counts": {"ALIVE": 377, "REFUSED": 0, "SKIPPED": 5, "WARN": 12},
  "ggen_version": "ggen 26.9.28",
  "packs": {"some-pack": {"status": "WARN", "warn_reason": "missing path dependency: ..."}},
  "schema": "https://ggen.dev/marketplace/qualification-baseline/v1"
}
```

The file is deterministic: sorted keys, no timestamps. `warn_reason` appears
only for WARN packs and comes from the generated-build failure recorded by
`qualify_packs.py`.

## Commands

```bash
python3 scripts/qualify_packs.py --ggen "$(which ggen)" --workers 6 --report /tmp/qual.json
python3 scripts/warn_ratchet.py check /tmp/qual.json      # exit 2 on regression
python3 scripts/warn_ratchet.py baseline /tmp/qual.json   # re-record after improvements
```

## Ratchet rules

`check` prints `REFUSED:WARN_RATCHET` and exits 2 when:

- a pack moved ALIVE to WARN, REFUSED or SKIPPED, or WARN to REFUSED or SKIPPED;
- a pack absent from the baseline is not ALIVE;
- the WARN count rose, when the report covers every baselined pack.

Improvements pass, and `check` prints that the baseline should be re-recorded.
By default `check` requires a non-empty report covering every baselined pack; a
partial report is refused. For a `--pack` subset run, pass `--subset`: absent
packs and the WARN-count rule are then skipped. Empty, non-object, or malformed
reports are refused as `REFUSED:WARN_RATCHET:report_invalid` (exit 2).

## Qualifying a subset

`qualify_packs.py --pack NAME` (repeatable) qualifies only the named packs and
composes with `--shard-index/--shard-count`. An unknown name is refused with
`REFUSED:GGEN_PACK_UNKNOWN`.

## See Also

- [Pack contract](pack-contract.md)
- [Publish a pack](../how-to/publish-a-pack.md)
