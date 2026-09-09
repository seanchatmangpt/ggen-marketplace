# ggen Marketplace Agent Operating Contract

This repository is the canonical, reviewable corpus of reusable ggen pack source. Scope is repository-wide unless a deeper `AGENTS.md` narrows a subtree. Live tree evidence outranks stale prose; deterministic manufacture and fail-closed admission outrank duplicated metadata or generated-output ownership.

## Preserve → Fence → Calculus
Resolve repo/ref/base to an exact commit. Read applicable doctrine, `marketplace.toml`, pack manifests/ontologies/templates/gates, scripts, CI, docs, and release policy before editing. Preserve pack identity, provenance, source/generated ownership, path safety, admission, deterministic catalog/fingerprint behavior, and maximal reversible lawful alternatives. Apply Chesterton's fence before removing a rule. One failed pack/qualification edge is topology, not graph failure.

## Source hierarchy
1. `marketplace.toml` declares marketplace operational law and is raw observation until admitted through the repository's current formal configuration boundary.
2. `packs/<name>/pack.toml` declares pack identity; directory and declared identity must agree.
3. `packs/<name>/ontology.ttl` carries admitted RDF facts.
4. `templates/` projects facts.
5. `gates/` may refuse invalid facts before generation.
6. Pack/project `ggen.toml` files remain generation contracts, not a second marketplace control plane.
7. Consumer outputs are generated consequences and do not belong here unless explicitly admitted source fixtures.

Do not hand-maintain a duplicate catalog, create a generated metadata namespace as source, use symlinks under packs, or duplicate release/platform/digest/qualification control values outside their authoritative configuration. CI is read-only evidence: it must not rewrite or push corrections. Preserve exact provenance when moving pack source. Keep Diátaxis categories semantically distinct.

## Evidence / authority
Use `UNKNOWN | PARTIAL_ALIVE | ALIVE | BLOCKED | BUILD_BROKEN | UNSUPPORTED` plus typed `REFUSED_*`. `ALIVE` requires exact admitted execution. Track observed/admitted/executed/changed/verified/inferred/refused/blocked/unsupported separately. A green repository validator proves only the contract it executed; consequential pack behavior requires the matching ggen runtime and real consumer boundary when that claim changes.

`A = μ(O*)`; `R = receipt(A)`. Separate `SELECT`, `CONSTRUCT`, `DO`. Raw config, model/planner output, templates, generated source, and hooks have no ambient execution authority. Configuration becomes executable only after the current formal admission boundary returns its required witness. Consequential qualification/consumer execution must be receipted.

## Work / verification
Follow `parse → orient → resolve → materialize → read doctrine → inspect → admit/refuse → diagnose/repair → construct → actuate → receipt → replay → standing`. Prefer the existing lawful path and smallest coherent diff. Edit ontology/config/template/gate sources rather than emitted catalogs/consumer outputs.

Acceptance precedence: exact user behavior/command → live documented repository command → narrowest equivalent. Discover the current admission, validation, deterministic-catalog, fingerprint, and qualification commands from `scripts/`, configuration, CI, and docs at the admitted SHA. Run catalog generation twice and compare when determinism is in scope. On failure preserve command/exit/diagnostic, form a new hypothesis, repair narrowly, and rerun the failed boundary. CI supplements local proof; it is not truth.

## GitHub / receipt
Never silently move the admitted base. Unless explicitly instructed otherwise: purpose branch, intentional commit, non-force push, draft PR, no merge. Final receipt states repo/base/tree, O/O*, config admission witness, source/generated changes, transports/failures, commands/exits, qualification/replay, branch/SHA/PR, scoped standing, and falsifiers.