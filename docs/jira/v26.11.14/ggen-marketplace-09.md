# ggen-marketplace-09 gate-run court for gcp-marketplace-saas-pack

Standing: UNVERIFIED

## Problem

`/Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/` holds 010/020/030 .rq gates
but, unlike
`/Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.py`, no runner and no court in
`/Users/sac/ggen-marketplace/ci/courts/` or
`/Users/sac/ggen-marketplace/ci/courts.json` executes them. Gates that never run carry no bits.

## Acceptance

`python3 /Users/sac/ggen-marketplace/scripts/check_gate_witness_courts.py` exits 0 and lists the
gcp pack gates as
witnessed; a new `/Users/sac/ggen-marketplace/tests/test_gcp_marketplace_saas_gates.py` passes
under pytest.

## Falsifier

Delete one `FILTER` clause from `gates/020_entitlement_states.rq`; the court must exit 1.

## Owned files

`/Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/run_gates.py`,
`/Users/sac/ggen-marketplace/tests/test_gcp_marketplace_saas_gates.py`,
`/Users/sac/ggen-marketplace/ci/courts.json`

## Depends-on

None.

## Size

M

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/ : 3 files, 90 lines total
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/020_entitlement_states.rq : 30
  lines
- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.py : 41 lines
- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/ : 4 files, 74 lines total
- /Users/sac/ggen-marketplace/ci/courts.json : 783 lines
- /Users/sac/ggen-marketplace/ci/courts/ : 93 files, 2809 lines total
- /Users/sac/ggen-marketplace/scripts/check_gate_witness_courts.py : 138 lines
- /Users/sac/ggen-marketplace/packs/gcp-marketplace-saas-pack/gates/run_gates.py : NEW (0 lines, to
  be created; est. LOC: ~45; basis: typer-azure-pack run_gates.py is 41 lines)
- /Users/sac/ggen-marketplace/tests/test_gcp_marketplace_saas_gates.py : NEW (0 lines, to be
  created; est. LOC: ~60; basis: one pytest per gate plus mutation case)

## Result

Standing: UNVERIFIED (nothing executed; rdflib absent from ambient python3)

Files (/Users/sac/ggen-marketplace): packs/gcp-marketplace-saas-pack/gates/run_gates.py (~60),
tests/test_gcp_marketplace_saas_gates.py (~55), ci/courts.json (+1 entry). Outside owned list but
required by the witness court: packs/gcp-marketplace-saas-pack/gate-court.toml, witnesses/{pass,fail}/*.ttl
(6), ci/courts/gcp-marketplace-saas-gates.sh.

Acceptance: `python3 scripts/check_gate_witness_courts.py` ; `python3
packs/gcp-marketplace-saas-pack/gates/run_gates.py --witnesses` ; pytest
tests/test_gcp_marketplace_saas_gates.py (needs rdflib).

## Repair
Standing: BLOCKED. Audit MEDs: (1) ambient python3 lacks rdflib; run acceptance in an env with it. (2) mutation test covers only the duplicate-stateValue branch; witnesses for missing-stateValue and empty-family FILTERs still to add and validate by execution. (3) files beyond Owned list (gate-court.toml, witnesses/*, ci/courts/*.sh) disclosed in Result; collision unchecked. Rerun the Acceptance commands above.
