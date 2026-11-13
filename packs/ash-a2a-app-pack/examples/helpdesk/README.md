# helpdesk example

Standing: UNVERIFIED

Minimal consumer of `ash-a2a-app-pack`: one domain, Ticket and Note resources, two
a2a skills and one `AshA2A.Agent`.

## Run

```sh
cd examples/helpdesk
rm -f ggen.lock
ggen sync run --skip-ea-admission
mix deps.get && mix compile
mix test
```

`ggen.toml` points at the pack by absolute path and `ontology/app.ttl` sets
`aap:ashA2aDep` to a local `path:` dep; replace it with a hex requirement outside
this machine.

## What is exercised

| Term family | Status in this example |
|---|---|
| Legacy core (Project, Domain, Resource, Attribute, Action, Skill, Agent) | Live: wired by shared templates |
| L01 `EnumType` / `EnumValue` | Emitted as a standalone enum module, unreferenced |
| L02 `Relationship` (has_many / belongs_to with inverses) | Emitted as fragment, not yet wired |
| L05 `Identity` / `Validation` | Emitted as fragment, not yet wired |

The shared `resource.ex.tmpl` has no `fragments:` option, so L02 and L05 take effect
on `Helpdesk.Desk.Ticket` only after that wiring lands. Gates (`010`, `020`, `030`,
L01, L02, L05) are intended to pass for this ontology; no run has confirmed it.

## Expected output

`mix.exs`, `config/config.exs`, `lib/helpdesk/{desk,ticket,note,desk_agent}.ex`,
`ticket_l02.ex`, `ticket_l05.ex`, `note_l02.ex`, `ticket_status.ex` and
`test/desk_agent_test.exs`, which asserts the agent card lists `list_tickets` and
`open_ticket`.
