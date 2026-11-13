# L19 notes: ea.graph.json (G2) and relock (G3)

## G2: ea.graph.json from the pack

- `templates/L19_ea_graph.json.tmpl` emits `ea.graph.json` (schema `ggen.ea.graph.v1`).
- Default (`aap:eaDeclare` absent or `"false"`): the same minimal-valid shape `ggen init` writes
  (`crates/ggen-cli/src/cmds/init.rs:239`, documented there as passing FM-LAW-015 without
  `--skip-ea-admission`): strategy + six empty arrays. Strategy id is `strategy:<appName>`.
- `aap:eaDeclare "true"`: one capability, ABB and contract per `aap:Agent`
  (`cap:/abb:/contract:<agentName>`, authority ceiling CONSTRUCT, `max_artifacts` 8).
- Never emitted: `candidate_sbbs`, `qualifications`, `packs`. Their `sha256:` digests
  (`ggen-abb-sbb` `sha256_hex(canonical_json_bytes(..))`, lib.rs:433-450, `contract_digest`
  lib.rs:629) are computed by Rust over canonical JSON; Turtle cannot supply them, so emitting
  placeholders would be a fabricated identity. Consequence: the graph is admissible for the
  gate (FM-LAW-015) but offers nothing to `ggen ea admit --sbb ...`.
- Gates `L19_010..030` refuse unsafe names (ids are interpolated unescaped), a non-boolean
  `eaDeclare`, and `eaDeclare "true"` with no agent.

UNVERIFIED until run: whether FM-LAW-015 accepts an ABB/contract set with zero candidate SBBs
(structure matches `fixtures/ea-graph.json` minus SBB/qualification rows). If it refuses,
leave `eaDeclare` unset (the default path is the `ggen init` graph byte-for-structure).

Verify (coordinator): in a fresh dir with `ggen.toml` + app.ttl, `ggen sync run` (no
`--skip-ea-admission`) exits 0; then with `fixtures/L19-ea.ttl` appended to app.ttl.

## G3: relock behavior

- `ggen.lock` records `[packs.<name>] content_hash = "blake3:..."` over sorted
  `(relative path, bytes)` of EVERY file under the pack root (`ggen-engine/src/pack.rs`
  `content_hash`). Any pack edit (including this lane's files) changes it and `ggen sync run`
  refuses until the lock is replaced; the workaround is `rm ggen.lock`.
- Closing it in ggen proper needs a `--relock` flag on `ggen sync run` (CLI change, outside
  this lane). Closing it on the igniter side is done:
  `mix ggen_igniter.pack_sync --relock` rewrites `ggen_igniter.pack.lock`
  (`GgenIgniter.PackLock`, sha256 over the same file set minus `.git/_build/.DS_Store`), and
  `--lock PATH` refuses on mismatch. The two lock formats are independent; `--relock` never
  touches `ggen.lock`.
