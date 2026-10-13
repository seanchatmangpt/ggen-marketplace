# STRATA-ACTIVATION-DEFERRAL

Wave: v26.10.8 (strata-hardening) · Lane L17 · 2026-10-12

## Decision

The 7 strata packs (cas, pn64, protocol, signer, stratus, temprun, valve) are **NOT**
activated into `marketplace.active.toml` this wave. They land hardened on disk;
activation is deferred pending ALIVE qualification.

## Rationale (court-verified 2026-10-12/13)

Activation is a curated 3-file edit, not a per-pack flag:

1. `marketplace.active.toml` — `[active].packs` list (13 entries, version/standing header).
2. `scripts/verify_msct_profile.py:10` — `EXPECTED_ACTIVE_PACKS`.
3. `scripts/verify_enterprise_kudzu_profile.py:12` — `EXPECTED_ACTIVE_PACKS`.

Both verify scripts enforce an exact-set invariant (`active_packs=13`); adding a pack
without updating both pins in lockstep fails the profile checks.

The active set is deliberately rare (13 of ~315 catalog packs). The 2026-10-04 wave
precedent (`marketplace.active.toml` legacy header comment) holds healthy, manifest-complete
packs out as "UNKNOWN, not ALIVE" until a real-ggen qualification falsifier
(`python3 scripts/marketplace.py check <pack>`) flips them. Strata hardening lands
in-wave, but ALIVE-qualification of the whole active profile is the evidentiary
precondition for touching the exact-set files.

Monetization is orthogonal: `scripts/marketplace.py` loads `monetization.toml`
independently of the active set — activation is not a monetization event.

## Future activation checklist (post-ALIVE, one atomic commit)

1. Per pack: `python3 scripts/marketplace.py check <pack>` → ALIVE (all 7 strata packs).
2. Edit the 3 files in lockstep: `[active].packs` + both `EXPECTED_ACTIVE_PACKS` sets.
3. `python3 scripts/marketplace.py catalog --scope active` shows the new set.
4. Rerun both verify scripts (invariant becomes `active_packs=<new N>`).
5. Receipt citing per-pack ALIVE evidence.

## Non-goals (this wave)

- No `marketplace.active.toml` edits.
- No pin changes in either verify script.
- No `monetization.toml` edits.
