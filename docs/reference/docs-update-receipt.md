# Documentation convergence receipt

This receipt binds the Level-5 documentation convergence transition for `ggen-marketplace`.

## Subject

- base: `bcb00c86f5dcd897b84f26cb4c4ac7803bb34c38`
- branch: `agent/docs-level5-convergence`
- scope: marketplace operational/governance documentation, Level-5 maturity/Diátaxis/class-closure documentation, and `pack-maturity-pack` documentation
- generated control surfaces: `docs/SUMMARY.md` and `book.toml` are not edited; they are manufactured from `docs/book.ttl` by the exact-subject Pages rail

## Source hierarchy preserved

`marketplace.toml` remains the source of operational qualification law. Pack RDF/manifests remain semantic/identity authority. `docs/book.ttl` remains the mdBook navigation source. Generated documentation control surfaces remain consequences.

## Changes

The transition:

- defines the 5 × 7 Level-5 maturity contract;
- binds Level 5 to Tutorial + How-to + Reference + Explanation correspondence;
- defines semantic pack classes separately from packaging profiles;
- adds a reversible consolidation/class-closure procedure;
- updates tutorials/how-to/reference/explanation to exact-subject, receipt/replay, and authority-fenced language;
- removes volatile copied runtime/version examples where admitted executable configuration is authoritative;
- connects contributor/security/agent doctrine to the same Level-5 law.

Historical point-in-time and provenance documents remain historical rather than being rewritten as present-tense standing.

## Validation/replay

Canonical commands:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
python3 scripts/marketplace.py validate
python3 scripts/marketplace.py catalog > /tmp/catalog-a.json
python3 scripts/marketplace.py catalog > /tmp/catalog-b.json
cmp /tmp/catalog-a.json /tmp/catalog-b.json
python3 scripts/marketplace.py fingerprint
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

The Pages owning court additionally deletes generated `book.toml`/`docs/SUMMARY.md`, runs exact-subject ggen manufacture, then builds mdBook.

Local materialization is unavailable in the current agent runtime because `github.com` DNS resolution is blocked; GitHub exact-head Actions are therefore the execution fallback. This receipt must not be promoted to ALIVE until those exact-head courts terminate successfully.

## Authority ceiling

Documentation/source only. No live cloud/API/production actuation, release/tag publication, credentials, BRCE widening, or consequential DO authority is introduced.

## Falsifiers

Refuse completion if:

- `docs/book.ttl` cannot manufacture a valid `docs/SUMMARY.md`/`book.toml`;
- any new navigation target is missing;
- repository validation/qualification regresses because of the documentation/source changes;
- reference prose contradicts admitted `marketplace.toml` or pack source;
- generated control surfaces are treated as editable authority;
- Level-5 docs imply domain/runtime/DO evidence that was not executed;
- consolidation language permits authority widening or deletion without equivalence/migration evidence.

## Rollback

Revert this documentation convergence PR as one merge unit. No generated consumer output or external system mutation is owned by this transition.
