# Reference: ggen qualification contract

The marketplace has two distinct acceptance layers.

`python3 scripts/marketplace.py validate` establishes structural/catalog admission. `python3 scripts/qualify_packs.py` establishes bounded runtime qualification through the real ggen manufacturer.

## Runtime identity

The canonical qualification rail uses **ggen v26.8.8** installed by `scripts/install-ggen.sh`. The release archive is selected by OS/architecture and verified against an admitted SHA-256 digest before extraction.

Supported installer targets are Linux x86_64, Linux aarch64, macOS arm64, and macOS x86_64. Unsupported platforms refuse rather than selecting an unverified binary.

## Subject selection

The qualification subject is exactly the list returned by `require_admitted()` from `scripts/marketplace.py`. There is no second pack inventory.

Derived pack profiles determine the capsule shape:

- `projection` — isolated consumer with the pack path plus a graph-load probe;
- `semantic` — the same isolated consumer/probe, proving RDF can be loaded even without pack templates;
- `project` — byte-for-byte temporary copy of the pack executed through its own `ggen.toml`.

## Per-pack law

For each admitted pack `p`, qualification requires:

```text
source_digest_before(p)
→ ggen sync run
→ consequence_1
→ ggen sync run
→ consequence_2
→ consequence_1 == consequence_2
→ source_digest_after(p) == source_digest_before(p)
```

Each ggen pass has a hard ceiling of five seconds. The CLI refuses a requested timeout above five seconds. Pack runs are isolated and may execute concurrently; concurrency does not relax any individual bound.

Runtime metadata roots `.git`, `.ggen`, `.cache`, and `target` are excluded from consequence comparison. Canonical input and manufactured non-runtime files remain in the snapshot, so a second sync that rewrites a source or consequence is visible.

Projection and semantic packs must additionally produce `qualification/marketplace-probe.txt`. The probe contains only a SPARQL graph-count projection; it exists to demonstrate that ggen loaded an RDF graph containing the selected pack.

## Report

With `--report PATH`, the court emits deterministic-shape JSON using schema:

```text
https://ggen.dev/marketplace/qualification/v1
```

Each pack record binds name, version, profile, status, source digest, and, on success, consequence file count plus consequence digest. Failed records carry a typed refusal code and diagnostic detail.

Timing measurements are intentionally absent from the report so scheduler noise does not become marketplace state.

## Refusals

The court fails closed on missing ggen, invalid timeout/worker bounds, ggen version invocation failure, pack timeout, ggen sync failure, missing probe, nondeterministic replay, or canonical-source mutation.

The complete run exits nonzero when any admitted pack refuses.

## Authority boundary

The court exercises ggen's filesystem manufacturer only. It does **not** execute manufactured artifacts or external actuators. Pack-owned Python verifier gates are source admitted by the marketplace but are not automatically executed by this generic court because arbitrary verifier execution is a different authority/sandbox boundary.

Therefore all-pack ggen qualification can establish pack manufacture/replay standing at an exact head, but cannot establish external-system consequence, customer acceptance, benchmark SOTA, cloud authority, or BRCE DO standing.
