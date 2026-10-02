# SYNTHESIZED RENDER FIXTURES — NOT A RENDER

These four JSON files (`machine`, `verification`, `executive`, `replay`) are L3's
hand-synthesized contract fixtures shaped to RESOLUTIONS R2 (machine/verification/replay
headers + bodies) and R3 (executive schema). They were NOT produced by a `ggen sync run`
of this pack. The `xRenderProvenance` key on each file records that; courts ignore
unknown keys, and no court treats these files as render evidence.

- `canonical/` — the fixture set the JSON courts admit (all standing UNKNOWN per R8).
- `replay/` — byte-copy of `canonical/` used by the determinism court as the second render.

When L2's real rendered outputs land under the pack `generated/` directory, replace
`canonical/` with copies of them (they then stop being synthesized) and re-run:

    python3 packs/chicago-xaas-surface-pack/test/run_courts.py json
