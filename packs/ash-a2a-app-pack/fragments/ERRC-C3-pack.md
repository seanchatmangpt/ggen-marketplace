# ERRC C3: consumer surface

Standing: UNVERIFIED

## Files

- `pack.toml` rewritten (v0.2.0): 20-lane description, expanded `provides`,
  `consumer_contract.runtime` for all optional deps, `peer_context`.
- `README.md` new: quickstart, vocabulary map, gates catalog, limitations.
- `examples/helpdesk/{ggen.toml,ontology/app.ttl,README.md}` new.

## Decisions

- `requires = []`: no template consumes another pack's output, so no URN was invented.
- Example resource bodies rely only on legacy edges; L01/L02/L05 facts are included
  because their templates and gates exist, but their fragments are not wired into
  `resource.ex.tmpl` (coordinator seam).
- Note create action accepts only `body`: accepting `ticket_id` would break compile
  while the L02 fragment is unwired.

## Open for coordinator

- Wire `fragments:` in `resource.ex.tmpl` so L02/L05 activate in the example.
- Run the example (`ggen sync run`, `mix compile`, `mix test`); nothing was executed.
- Confirm `ggen sync` loads `ontology.d/*.ttl` automatically from a pack.
