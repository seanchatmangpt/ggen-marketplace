# Example: consuming `chicago-tdd-tools-pack`

This is a real, runnable example of attaching `chicago-tdd-tools-pack` to a
consumer project via the documented local-path convention
(`docs/how-to/consume-a-pack.md`):

```toml
[packs]
"chicago-tdd-tools-pack" = { path = "../../../chicago-tdd-tools-pack" }
```

`schema/domain.ttl` declares two real `ctt:CliBoundaryTest` individuals
grounded directly in `chicago_tdd_tools::cli_proof::CliHarness`
(`/Users/sac/chicago-tdd-tools/src/cli_proof/harness.rs`) — the exact
primitive `cli_boundary_runtime.rs.tmpl` wraps as `run_boundary_spec`. This
example targets the toy `receiptctl`-shaped binary this pack's own
`qualification/consumer.ttl` and `ontology.ttl` are already grounded
against, so it is self-consistent with the pack's real individuals, not a
disconnected fixture.

Run it for real:

```bash
cd packs/chicago-tdd-tools-pack/examples/consume-chicago-tdd-tools-pack
ggen sync run
```

This produces `tests/chicago_tdd_tools_boundary.rs`,
`tests/chicago_tdd_tools_boundary_runtime.rs`,
`tests/chicago_tdd_tools_boundary_proof.rs`, and
`docs/chicago_tdd_tools_boundary.md` — the same four artifacts the
qualification fixture produces, generated fresh from this example's own
smaller ontology subset.
