# ggen-marketplace-11 non-vacuity court for typer-azure-pack gates

Standing: UNVERIFIED

## Problem

`/Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.py` runs
  /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/010_required_options.rq and
/Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/020_typer_module.rq against
  `/Users/sac/ggen-marketplace/packs/typer-azure-pack/generated/`, but no mutation proves a bad
  generated module is
refused. Receipt standing for the pack is unwitnessed.

## Acceptance

`bash /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.sh` exits 0 on the
  committed
`/Users/sac/ggen-marketplace/packs/typer-azure-pack/generated/`,
and exits nonzero on a temp copy with a required option removed (court script asserts both).

## Falsifier

The mutated copy passes both gates.

## Owned files

`/Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.py`,
`/Users/sac/ggen-marketplace/tests/test_typer_azure_gate_nonvacuity.py`

## Depends-on

None.

## Size

S

## References (path : LOC)

- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.py : 41 lines
- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.sh : 8 lines
- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/010_required_options.rq : 16 lines
- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/020_typer_module.rq : 9 lines
- /Users/sac/ggen-marketplace/packs/typer-azure-pack/generated/ : 0 files, 0 lines (empty or absent)
- /Users/sac/ggen-marketplace/tests/test_typer_azure_gate_nonvacuity.py : NEW (0 lines, to be
  created; est. LOC: 45, basis: 3 tests x ~15 lines w/ temp-copy mutation)

## Result

Standing: UNVERIFIED (nothing executed; hook forbids tests)

- /Users/sac/ggen-marketplace/packs/typer-azure-pack/gates/run_gates.py (+2 LOC: optional argv[1] ontology override)
- /Users/sac/ggen-marketplace/tests/test_typer_azure_gate_nonvacuity.py (new, ~44 LOC, 3 tests)
- Note: gates query ontology.ttl (generated/ is empty); run_gates.sh needs `ggen gate` and is not owned, so the court drives run_gates.py. The apiVersion mutation regex is unobserved and may need adjusting.
- Acceptance: run the new test file with python3 -m pytest from /Users/sac/ggen-marketplace.
