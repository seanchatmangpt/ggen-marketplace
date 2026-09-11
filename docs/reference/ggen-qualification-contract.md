# Reference: ggen qualification contract

The marketplace has two distinct acceptance layers.

`python3 scripts/marketplace.py validate` establishes structural/catalog admission. `python3 scripts/qualify_packs.py` establishes bounded manufacture/replay qualification through the real ggen runtime.

## Runtime identity

The canonical qualification rail uses the ggen version pinned in `marketplace.toml`'s `[ggen].version` (currently **v26.8.11**), installed by `scripts/install-ggen.sh`. The release archive is selected by OS/architecture and verified against an admitted SHA-256 digest before extraction.

Supported installer targets are Linux x86_64, Linux aarch64, macOS arm64, and macOS x86_64. Unsupported platforms refuse rather than selecting an unverified binary.

## Subject selection

The qualification subject is exactly the list returned by `require_admitted()` from `scripts/marketplace.py`. There is no second pack inventory and no pack-name exception table.

The derived pack profile determines the capsule shape:

- `projection` — create an isolated consumer, reference the marketplace pack through ggen's local `[packs]` contract, add a graph-load probe, and union only pack-owned positive consumer facts/extra ontologies;
- `semantic` — create an isolated **declarative** ggen project, load the pack's native ontology files directly, attach its native SPARQL gates, and manufacture a tiny probe through an explicit generation rule;
- `project` — copy the complete pack byte-for-byte into an isolated project capsule, then overlay only pack-owned `qualification/project/**` positive inputs before running that pack's own `ggen.toml`.

## Pack-owned qualification inputs

A capability that requires consumer facts owns the positive qualification specimen. The generic court does not learn its pack name.

Recognized surfaces are:

- `qualification/consumer.ttl` — one positive RDF consumer fixture;
- `qualification/consumer/*.ttl` — multiple positive RDF fixtures, loaded in lexical order;
- `qualification/project/**` — files overlaid into the temporary copy of a project-profile pack;
- `qualification.toml` — optional consumer contract.

The current `qualification.toml` contract is:

```toml
[consumer]
extra_ontologies = ["bodies.ttl"]
```

Every `extra_ontologies` path must be relative, remain inside its pack, and identify an existing file. Absolute paths, `..` traversal, missing files, malformed TOML, or malformed tables refuse as `REFUSED:QUALIFICATION_CONTRACT_INVALID`.

Qualification fixtures are **synthetic admitted inputs**, not observations that an external event occurred. A fixture can prove that a pack's compiler/gate surface accepts a bounded positive subject; it cannot become an execution receipt, customer consequence, benchmark result, cloud observation, or authority grant.

## Per-pack law

For every admitted pack `p`, qualification requires:

```text
source_digest_before(p)
→ isolated consumer capsule(p)
→ bounded ggen sync run
→ consequence_1
→ bounded ggen sync run
→ consequence_2
→ consequence_1 == consequence_2
→ source_digest_after(p) == source_digest_before(p)
```

Each ggen pass has a hard ceiling of five seconds. The CLI refuses a requested timeout above five seconds. Pack runs are isolated and may execute concurrently; concurrency never relaxes the individual five-second bound.

The runner uses a fresh HOME/XDG state per pack while preserving only the admitted Rust toolchain locations through `RUSTUP_HOME` and `CARGO_HOME` when ggen-owned formatting requires them.

Runtime-only roots excluded from consequence comparison are:

- `.git`
- `.ggen`
- `.ggen-v2`
- `.cache`
- `.qualification-home`
- `target`

Canonical source and all manufactured non-runtime files remain in the snapshot. A second sync that rewrites a source or consequence is therefore visible.

Projection and semantic packs must additionally materialize `qualification/marketplace-probe.txt`. The probe is deliberately trivial; its purpose is to demonstrate that the real ggen runtime loaded the selected graph and completed manufacture, not to promote the graph's claims to external truth.

## Repository-level law

The permanent GitHub qualification rail additionally requires:

1. checkout of `pull_request.head.sha` rather than GitHub's synthetic merge commit;
2. mechanical `git rev-parse HEAD == admitted SHA` assertion;
3. complete structural + Diátaxis validation;
4. two deterministic catalog projections with byte comparison;
5. admitted-corpus fingerprinting;
6. digest-pinned ggen installation;
7. complete all-pack qualification;
8. a clean `git status --porcelain --untracked-files=all` after qualification;
9. absence of the one-shot migration actuator.

The job sets `PYTHONDONTWRITEBYTECODE=1`. This prevents the verifier itself from leaving Python bytecode in the admitted source tree; the source-mutation guard remains strict rather than learning to ignore arbitrary untracked files.

Permanent CI has `contents: read`. Temporary diagnostic or projection-synchronization workflows are not part of the final marketplace architecture and must be removed after their bounded purpose is complete.

## Report

With `--report PATH`, the court emits deterministic-shape JSON using schema:

```text
https://ggen.dev/marketplace/qualification/v1
```

Each pack record binds name, version, profile, status, source digest and, on success, consequence file count plus consequence digest. Failed records carry a typed refusal code and diagnostic detail.

Timing measurements are intentionally absent from the report so scheduler noise does not become marketplace state.

## Refusals

The court fails closed on missing ggen, invalid timeout/worker bounds, ggen version invocation failure, malformed qualification contract, pack timeout, ggen sync failure, missing probe, nondeterministic replay, or canonical-source mutation.

The complete run exits nonzero when **any** admitted pack refuses. There is no partial-success exit that can masquerade as complete marketplace standing.

## Authority boundary

The court exercises ggen's bounded filesystem manufacturer only. It does **not** execute manufactured applications, Terraform, GitHub Actions emitted by packs, MCP calls, cloud APIs, pack-owned arbitrary Python verifier gates, or other external actuators.

Therefore exact-head all-pack qualification may establish deterministic pack load/manufacture/replay standing for the admitted marketplace subject. It cannot establish generated-program runtime correctness, external-system consequence, customer acceptance, benchmark SOTA, cloud authority, physical-world consequence, organizational acceptance, or BRCE DO standing.
