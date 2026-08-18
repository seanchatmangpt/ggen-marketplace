# How to qualify every pack with ggen

Use this when you need behavioral marketplace evidence beyond manifest/layout admission.

## Run the bounded court

Install the exact admitted ggen runtime and execute the complete corpus:

```bash
export GGEN_BIN="$(scripts/install-ggen.sh)"
python3 scripts/qualify_packs.py --report /tmp/ggen-marketplace-qualification.json
python3 -m json.tool /tmp/ggen-marketplace-qualification.json >/dev/null
```

The installer downloads the ggen version pinned in `marketplace.toml`'s `[ggen].version` (currently v26.8.11) for the current supported platform and refuses if the release-asset SHA-256 differs from the pinned digest.

`qualify_packs.py` discovers the complete admitted pack set from the same local marketplace calculus used by `marketplace.py`. It does not accept a hand-maintained pack list or pack-name exemptions.

## Understand the three capsule shapes

For a **projection** pack, the court creates a throwaway consumer, references exactly that marketplace pack through ggen's local pack contract, adds any pack-owned positive consumer RDF/extra ontologies, and adds a tiny graph-load probe.

For a **semantic** pack, the court creates a throwaway declarative ggen project, loads the pack's native ontology files directly, attaches its native SPARQL gates, and manufactures the probe with an explicit generation rule. Semantic packs are not misrepresented as template packs merely to satisfy the court.

For a **project** pack, the court copies the complete pack into a throwaway project capsule, overlays any source-owned `qualification/project/**` inputs, and runs that pack's own `ggen.toml` without modifying marketplace source.

When a pack needs a positive subject, keep that subject with the pack:

```text
qualification/consumer.ttl
qualification/consumer/*.ttl
qualification/project/**
qualification.toml
```

Use `qualification.toml` only when the real consumer contract needs additional pack-local RDF authority:

```toml
[consumer]
extra_ontologies = ["bodies.ttl"]
```

Do not add pack names or special cases to `qualify_packs.py` just to make a capability pass.

## Acceptance law

Every pack must:

1. complete `ggen sync run` within five seconds;
2. complete a second sync within five seconds;
3. produce an identical non-runtime file snapshot on the second pass;
4. leave the marketplace pack source byte-identical;
5. for projection/semantic profiles, materialize `qualification/marketplace-probe.txt`.

The court runs packs concurrently, but each pack receives its own HOME/XDG state and filesystem capsule. Runtime-only ggen/cache/toolchain state is excluded from consequence comparison; canonical pack source and manufactured non-runtime output remain observable.

## Interpret refusals

A failure is typed. Examples include:

- `REFUSED:GGEN_PACK_TIMEOUT` — the bounded manufacturer exceeded the admitted per-pass ceiling;
- `REFUSED:GGEN_PACK_SYNC_FAILED` — the real ggen runtime rejected or failed to manufacture the pack;
- `REFUSED:GGEN_PACK_PROBE_MISSING` — ggen did not produce the graph-load witness for a projection/semantic pack;
- `REFUSED:GGEN_PACK_NONDETERMINISTIC_REPLAY` — pass two changed the manufactured filesystem consequence;
- `REFUSED:GGEN_PACK_SOURCE_MUTATED` — qualification altered canonical marketplace source;
- `REFUSED:QUALIFICATION_CONTRACT_INVALID` — a pack-owned qualification contract is malformed, unsafe, or references missing data.

Do not suppress a refusal to make CI green. Repair the pack's admitted source or source-owned qualification contract and re-run the complete corpus.

## Verify the repository stayed clean

Permanent CI runs with `PYTHONDONTWRITEBYTECODE=1` and finishes with:

```bash
git status --porcelain --untracked-files=all
```

Any residue refuses the exact-head qualification. The guard is intentionally strict; qualification tooling must prevent its own temporary files rather than teaching the guard to ignore arbitrary source-tree changes.

## Evidence boundary

This court proves bounded **ggen load/manufacture/replay behavior** for every admitted pack at one exact repository head. It does not execute manufactured programs, Terraform, emitted GitHub Actions, MCP calls, cloud operations, or arbitrary pack-owned Python verifier gates, and it does not establish consumer-specific business behavior, external consequence, or BRCE DO authority.
