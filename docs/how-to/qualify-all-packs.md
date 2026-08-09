# How to qualify every pack with ggen

Use this when you need behavioral marketplace evidence beyond manifest/layout admission.

## Run the bounded court

Install the exact admitted ggen runtime and execute the complete corpus:

```bash
export GGEN_BIN="$(scripts/install-ggen.sh)"
python3 scripts/qualify_packs.py --report /tmp/ggen-marketplace-qualification.json
python3 -m json.tool /tmp/ggen-marketplace-qualification.json >/dev/null
```

The installer downloads ggen v26.8.8 for the current supported platform and refuses if the release-asset SHA-256 differs from the pinned digest.

`qualify_packs.py` discovers the complete admitted pack set from the same local marketplace calculus used by `marketplace.py`. It does not accept a hand-maintained pack list.

For projection and semantic packs, the court creates a throwaway consumer that imports exactly one marketplace pack and adds a tiny probe template. The probe forces ggen to load the combined RDF graph even when a semantic pack intentionally has no templates.

For project-profile packs, the court copies the complete pack into a throwaway project capsule and runs that pack's own `ggen.toml` without modifying marketplace source.

Every pack must:

1. complete `ggen sync run` within five seconds;
2. complete a second sync within five seconds;
3. produce an identical non-runtime file snapshot on the second pass;
4. leave the marketplace pack source byte-identical;
5. for projection/semantic profiles, materialize the qualification probe.

The court runs packs concurrently, but each pack receives its own HOME/cache/config/data directories and its own filesystem capsule.

## Interpret refusals

A failure is typed. Examples include:

- `REFUSED:GGEN_PACK_TIMEOUT` — the bounded manufacturer exceeded the admitted per-pass ceiling;
- `REFUSED:GGEN_PACK_SYNC_FAILED` — the real ggen runtime rejected or failed to manufacture the pack;
- `REFUSED:GGEN_PACK_PROBE_MISSING` — ggen did not produce the graph-load witness for a projection/semantic pack;
- `REFUSED:GGEN_PACK_NONDETERMINISTIC_REPLAY` — pass two changed the manufactured filesystem consequence;
- `REFUSED:GGEN_PACK_SOURCE_MUTATED` — qualification altered canonical marketplace source.

Do not suppress a refusal to make CI green. Repair the pack's admitted source or, when the refusal exposes a real unsupported packaging shape, change the marketplace contract explicitly and re-qualify the complete corpus.

## Evidence boundary

This court proves bounded **ggen load/manufacture/replay behavior** for every admitted pack at one exact repository head. It does not execute manufactured programs, Terraform, GitHub Actions, MCP calls, cloud operations, or pack-owned Python verifier gates, and it does not establish consumer-specific business behavior or BRCE DO authority.
