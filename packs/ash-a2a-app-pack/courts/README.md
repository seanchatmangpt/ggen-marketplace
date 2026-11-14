# ash-a2a-app-pack courts

Shim courts for the pack's Elixir-producing templates (lane L32). Authored, not run.

Standing: UNVERIFIED

## Invocation

```bash
cd /Users/sac/ggen-marketplace/packs/ash-a2a-app-pack
bash courts/shim_court.sh                          # every template whose to: ends .ex/.exs
bash courts/shim_court.sh agent_test.exs.tmpl      # one template
GGEN_BIN=/path/to/ggen SHIM_KEEP=1 bash courts/shim_court.sh L20_resource_court.exs.tmpl
```

Exit 0 = all PASS, 1 = any FAIL, 3 = nothing ran (all SKIP). Requires `ggen`, `mix`, and network
for `mix deps.get` (once per run).

## Protocol

1. Self-check: corrupt a restore of a real template copy; sha256 must detect it.
2. Pack and `examples/helpdesk` are copied to a temp dir; the real pack is never edited.
3. Per template: BASELINE sha256, BEFORE (`ggen sync run --skip-ea-admission` then `mix test`
   green in a fresh fixture), SHIM (`raise "SHIM-COURT"` inserted after the frontmatter), AFTER
   (sync again; `mix test` must be red and the marker must be in generated output), RESTORE
   (sha256 byte-exact).
4. A template the fixture never materializes is a loud `[SKIP]`; a court that cannot flip is
   `[FAIL:AFTER]`. Final check: real pack `templates/` tree hash unchanged.

## See Also

Protocol source: smalt `scripts/shim_court/lib.sh`.
