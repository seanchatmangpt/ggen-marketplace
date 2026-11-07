# FM-PACK-008 re-lock blocked: binary/pin version mismatch

Standing: BLOCKED

## Finding (audit M16, F1)

`strata-ledger-pack` and `qri-consumer-binding-pack` were edited after their lock
entries were minted (FM-PACK-008 drift class). The mechanical remediation is a
re-lock via `ggen sync run`. That re-lock is BLOCKED because the installed ggen
binary does not match the frozen-court pin.

## Observed state (2026-11-07, lane G7)

- Installed binary: `ggen --version` → `ggen 26.11.4` (exit 0)
- Frozen court pin: `marketplace.toml` `[ggen].version = "v26.8.11"`
  (`release_commit = 402cecdff8784767eb9f26e235d87c759610c066`)

26.11.4 ≠ v26.8.11. Re-locking under 26.11.4 would mint lock entries from a
different generator identity than the one the frozen courts qualified — that
contaminates the frozen-court evidence chain (generator-plurality law: the
qualification court is only meaningful against its pinned identity).

## Remediation (operator)

```sh
# 1. Install the pinned binary identity
cargo install --git https://github.com/seanchatmangpt/ggen \
  --rev 402cecdff8784767eb9f26e235d87c759610c066 ggen-cli
#    (or the equivalent pinned checkout: cd <ggen>@402cecdf && cargo install --path crates/ggen-cli)

# 2. Verify the pin match BEFORE re-locking
ggen --version   # must print 26.8.11

# 3. Regenerate both drifted locks per the repo's documented flow
cd /Users/sac/ggen-marketplace
ggen sync run    # exit 0 required

# 4. Verify the diff touches only hash lines in the two lock files
#    ggen.lock and packs/qri-consumer-binding-pack/ggen.lock
```

If step 4 shows any non-hash diff (structure, entries added/removed), stop and
re-audit before landing.
