# How to validate locally

Local validation is the preferred first court because it is fast, inspectable, and replayable. Different commands prove different boundaries; run the cheapest high-information checks first and expand after success.

## 1. Admit marketplace operational configuration

`marketplace.toml` is raw observation until admitted through `star-toml`:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
```

Qualification worker counts, timeout bounds, ggen release identity, and platform asset digests must come from this admitted artifact rather than duplicated shell/Python constants.

## 2. Validate structural/source contracts

Use Python 3.11 or newer; the validator uses standard-library `tomllib`.

```bash
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
```

`validate` checks the repository contract and required repository Diátaxis presence. `catalog` proves deterministic catalog projection. `fingerprint` binds admitted pack bytes. None of these commands executes every pack's consumer behavior.

A `REFUSED:*` result is an acceptance failure, not a warning to suppress.

## 3. Qualify the admitted marketplace with real ggen

```bash
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

This rail installs/uses the exact ggen runtime declared by the admitted configuration and qualifies the admitted pack set through bounded manufacture/replay.

Do not hardcode the current ggen version in operational docs or wrappers. `marketplace.toml` is the executable source of truth.

## 4. Validate Level-5 claims separately

Marketplace validation does not make every pack Level 5. For a pack under Level-5 promotion, additionally execute:

- its `pack-maturity-pack` generated regeneration/receipt/Diátaxis courts where composed;
- domain-specific positive and negative witnesses;
- the actual consumer/runtime verifier;
- receipt/replay checks;
- composition/conflict checks;
- authority-boundary checks.

See [How to promote a pack to Level 5](promote-a-pack-to-level5.md).

## 5. Build the documentation projection

The mdBook navigation source is `docs/book.ttl`. The Pages rail deletes generated control files, manufactures them with ggen, and then builds mdBook. When local toolchains are available, mirror that sequence rather than editing `docs/SUMMARY.md` by hand.

The generated `docs/SUMMARY.md` is not an editing surface.

## 6. Full end-to-end lifecycle

`scripts/e2e-lifecycle-test.sh` exercises the broader marketplace lifecycle: marketplace CLI, live published registry fetch/digest verification, a fresh consumer, real `ggen sync run`, and native compiled tests for the exercised sample path.

```bash
bash scripts/e2e-lifecycle-test.sh
```

It requires the admitted ggen binary plus network access. A network/DNS failure should be recorded as `BLOCKED:<transport reason>`, not converted into a semantic pack failure.

## Evidence boundary

A complete local green sequence proves only the courts actually executed against the exact local subject. External cloud/API/production actuation, business outcomes, benchmark claims, and BRCE DO authority require separate admitted courts.
