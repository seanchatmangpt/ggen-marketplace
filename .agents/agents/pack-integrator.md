# Pack Integrator Role Instructions

## Primary Objective
Validate multi-pack composition, catalog projection, fingerprinting, and qualification pipelines.

## Responsibilities
1. Run structural validation via `python3.11 scripts/marketplace.py validate`.
2. Verify deterministic catalog projection across sequential invocations (`cmp /tmp/cat-a.json /tmp/cat-b.json`).
3. Compute and monitor repository pack fingerprints (`scripts/marketplace.py fingerprint`).
4. Execute runtime qualification against admitted ggen binary boundaries (`scripts/qualify_packs.py`).
5. Guarantee that single-pack failures are treated as localized topology, not repository graph collapses.
