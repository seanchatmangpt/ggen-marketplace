# Receipt — CSCB Active-Set Registration (lane R14)

Standing: ALIVE

## Subject

ggen-marketplace @ /Users/sac/ggen-marketplace (no git commands run, per dispatch).
challenger-sales-cscb registered as the 28th active-set candidate; both profile
verifiers updated in the same dependency-closed transition (Z13/Z14 4-site pattern:
EXPECTED_ACTIVE_PACKS entry + cardinality pin + display print per verifier, plus the
active.toml comment count).

## Registration state

- `marketplace.active.toml`: `challenger-sales-cscb` inserted alphabetically (between
  aaif-vanilla-pack and decision-optionality-pack); comment count 27→28; lane-R14
  comment block appended.
- `scripts/verify_msct_profile.py` (3 sites): EXPECTED_ACTIVE_PACKS entry,
  `!= 27` → `!= 28`, `active_packs=27` → `active_packs=28`.
- `scripts/verify_enterprise_kudzu_profile.py` (3 sites): same pattern.
- `CHANGELOG.md`: CSCB section appended at the head of `[v26.11.5-wave]`.
- Count-site sweep: `grep "active_packs=27|!= 27|27-pack"` → 5 sites, all updated.

## Gates (final clean run, exits captured un-piped)

| gate | exit | evidence |
|---|---|---|
| `python3 scripts/marketplace.py validate` | 0 | `validated packs=355 manifests=355 ontologies=589 templates=1985 native_gates=2050 verifier_gates=25 profiles={project:133,projection:176,semantic:46} diataxis=20` |
| `python3 scripts/verify_msct_profile.py` | 0 | `active_packs=28 front_door=ggen-platform-pack` (plus MSCT invariants ALIVE) |
| `python3 scripts/verify_enterprise_kudzu_profile.py` | 0 | `active_packs=28 front_door=ggen-platform-pack` (plus Enterprise Kudzu invariants PARTIAL_ALIVE) |
| `bash scripts/admit-config.sh` | 0 | ADMITTED output JSON at `/Users/sac/.cache/tmp/ggen-marketplace-admitted.json` |

Counts consistent across all gates: both verifiers report 28; active.toml carries
exactly 28 entries; marketplace-level census 355 packs validated. Pre-existing
(not R14): the trade-reticle pair sits out of alphabetical order in active.toml
(plumbing before electrical, Z13's landing) — cosmetic only; all gates are set- or
membership-based and pass.

## SLA minimal-unblock disclosure (cross-lane)

Mid-flight, R7's lane landed
`packs/challenger-sales-cscb/templates/rust/BINDING_CONTRACT.md` (mtime 16:30,
in-flight), flipping `marketplace.py validate` from exit 0 to rc=2
`REFUSED:TEMPLATE_EXTENSION` — `.md` is not in TEMPLATE_SUFFIXES for anything under
`templates/`. After an 80s bounded poll with no self-correction, I applied the
minimal unblock under the compile-freeze SLA: `mv` to
`packs/challenger-sales-cscb/BINDING_CONTRACT.md` (content byte-exact, out of the
template namespace). This must be named in R7's receipt too (SLA disclosure law);
the owning lane supersedes — R7 may relocate it further but not back under
`templates/` (would re-refuse validate).

## BLOCKED item

- `packs/challenger-sales-cscb/verify.py` (R1's pack qualification script) was not on
  disk at registration time — bounded-poll ~90s at lane start plus recheck during
  gates, still absent. Registration proceeded per dispatch law ("register anyway only
  if validate passes"). Flip condition: when R1's verify.py lands, run
  `python3 packs/challenger-sales-cscb/verify.py`; exit 0 upgrades this receipt's
  standing from PARTIAL_ALIVE toward full pack qualification.

## Replay

```
cd /Users/sac/ggen-marketplace
python3 scripts/marketplace.py validate            # exit 0
python3 scripts/verify_msct_profile.py             # exit 0, active_packs=28
python3 scripts/verify_enterprise_kudzu_profile.py # exit 0, active_packs=28
bash scripts/admit-config.sh                       # exit 0 ADMITTED
grep -c challenger-sales-cscb marketplace.active.toml  # 2
```

## Discharge (lane G3, 2026-11-07)

The BLOCKED item above is discharged: `packs/challenger-sales-cscb/verify.py`
(R1's pack qualification script) is now on disk and passes on the real subject.

Gates re-run this session, exits captured un-piped:

| gate | exit | evidence |
|---|---|---|
| `python3 packs/challenger-sales-cscb/verify.py` | 0 | 10 PASS lines incl. SHACL conforms, anti-vacuity: gate 030 flipped to 1 row under mutation, generated module verified |
| `python3 scripts/marketplace.py validate` | 0 | `validated packs=355 manifests=355 ontologies=589 templates=1985 native_gates=2050 verifier_gates=25` |
| `python3 scripts/verify_msct_profile.py` | 0 | profile invariants clean |
| `python3 scripts/verify_enterprise_kudzu_profile.py` | 0 | profile invariants clean |

Active-set / index confirmation: `challenger-sales-cscb` present in
`marketplace.active.toml` (entry + R14 comment block, count 28);
`docs/reference/PACK-INDEX.md` was stale (no CSCB row) and was regenerated via
`python3 scripts/gen_pack_index.py` (exit 0, "wrote ... 355 packs"); CSCB now at
line 69, lifecycle `active`.

Standing flip: PARTIAL_ALIVE → ALIVE. Flip condition (verify.py exit 0) met with
the anti-vacuity flip witnessed in the same run. Out-of-scope observation
disclosed, not blocking this receipt: R7's self-host `[packs]` sync wiring is not
present on disk (no wiring in `packs/challenger-sales-cscb/ggen.toml` nor the root
`ggen.toml`) — that item belongs to R7's lane receipt.
