# How to qualify every pack with ggen

Use this when you need behavioral marketplace evidence beyond manifest/layout admission.

## Admit configuration first

`marketplace.toml` is the source of truth for qualification worker/timeout law and the pinned ggen release identity. Admit it before execution:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
```

Do not copy a ggen version, release commit, timeout, worker count, platform archive name, or asset digest into this document or another wrapper. Those values are intentionally centralized in admitted configuration so documentation cannot silently drift behind executable law.

## Run the bounded court

```bash
export GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json
export GGEN_BIN="$(scripts/install-ggen.sh /tmp/ggen-marketplace-admitted.json)"
python3 scripts/qualify_packs.py --report /tmp/ggen-marketplace-qualification.json
python3 -m json.tool /tmp/ggen-marketplace-qualification.json >/dev/null
```

Or run the repository wrapper:

```bash
GGEN_MARKETPLACE_ADMITTED_CONFIG=/tmp/ggen-marketplace-admitted.json \
  bash scripts/qualify-marketplace.sh \
  /tmp/ggen-marketplace-admitted.json \
  /tmp/ggen-marketplace-qualification.json
```

The installer selects the admitted platform asset and refuses when release identity or the downloaded digest does not match admitted configuration.

`qualify_packs.py` discovers the complete admitted pack set from the same marketplace calculus used by `marketplace.py`. It does not accept a hand-maintained pack list or pack-name exemptions.

## Understand the three capsule shapes

For a **projection** pack, the court creates a throwaway consumer, references exactly that marketplace pack through ggen's local pack contract, adds pack-owned positive consumer RDF/extra ontologies, and adds a tiny graph-load probe.

For a **semantic** pack, the court creates a throwaway declarative ggen project, loads the pack's native ontology files directly, attaches native SPARQL gates, and manufactures the probe with an explicit generation rule. Semantic packs are not misrepresented as template packs merely to satisfy the court.

For a **project** pack, the court copies the complete pack into a throwaway project capsule, overlays source-owned `qualification/project/**` inputs, and runs that pack's own `ggen.toml` without modifying canonical marketplace source.

When a pack needs a positive subject, keep it with the pack:

```text
qualification/consumer.ttl
qualification/consumer/*.ttl
qualification/project/**
qualification.toml
```

Use `qualification.toml` only when the real consumer contract needs additional pack-local RDF authority. Do not add pack-name branches to the generic court just to make one capability pass.

Fixtures are **synthetic admitted inputs**, not observations that an external event occurred. They can prove bounded compiler/gate behavior for the fixture; they cannot become customer evidence, cloud observation, benchmark result, or authority grant.

## Acceptance law

For every admitted pack `p`, qualification establishes the configured bounded form of:

```text
source_digest_before(p)
→ isolated capsule(p)
→ ggen sync run
→ consequence_1
→ ggen sync run
→ consequence_2
→ consequence_1 == consequence_2
→ source_digest_after(p) == source_digest_before(p)
```

Projection/semantic profiles must materialize the marketplace probe. Runtime-only ggen/cache/toolchain state is excluded from consequence comparison; canonical pack source and manufactured non-runtime output remain observable.

The exact numeric timeout/concurrency values are read from admitted `marketplace.toml`, not this guide.

## Interpret refusals

Representative refusal families include:

- `REFUSED:GGEN_PACK_TIMEOUT` — bounded manufacture exceeded admitted timeout law;
- `REFUSED:GGEN_PACK_SYNC_FAILED` — the real ggen runtime rejected or failed to manufacture the pack;
- `REFUSED:GGEN_PACK_PROBE_MISSING` — the graph-load witness was not manufactured for a profile that requires it;
- `REFUSED:GGEN_PACK_NONDETERMINISTIC_REPLAY` — the second pass changed the manufactured consequence;
- `REFUSED:GGEN_PACK_SOURCE_MUTATED` — qualification altered canonical marketplace source;
- `REFUSED:QUALIFICATION_CONTRACT_INVALID` — pack-owned qualification input is malformed, unsafe, or references missing data.

Do not suppress a refusal to make CI green. Repair the owning semantic/manufacturing boundary, or classify a genuinely unsupported boundary explicitly.

## Verify the repository stayed clean

Permanent CI runs with read-only source authority and finishes with a strict source-mutation check. Qualification tooling must prevent temporary residue instead of teaching the guard to ignore arbitrary files.

## Relationship to Level 5

All-pack qualification closes an important **manufacture/replay** boundary for the exact marketplace head. It does not by itself make every pack Level 5.

A Level-5 pack additionally requires domain-specific closure for semantic authority, complete admission/negative witnesses, the claimed real consumer/runtime boundary, receipt/replay semantics, authority fencing, composition/class closure, and all four Diátaxis quadrants.

See [Level-5 maturity contract](../reference/level5-maturity-contract.md) and [How to promote a pack to Level 5](promote-a-pack-to-level5.md).

## Evidence boundary

This court exercises ggen's bounded filesystem manufacturer. It does not execute manufactured applications, Terraform, emitted GitHub Actions, MCP calls, cloud operations, arbitrary external actuators, or every pack-owned domain verifier.

Therefore exact-head all-pack qualification may establish deterministic load/manufacture/replay standing for the admitted marketplace subject. It cannot establish generated-program runtime correctness, external-system consequence, customer acceptance, benchmark SOTA, cloud authority, physical-world consequence, organizational acceptance, or BRCE DO standing.
