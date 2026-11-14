# L26 multi-domain agent notes

- ash_a2a has no `domains` option: `AshA2A.Agent` pops one `:resource_or_domain`
  (`/Users/sac/ash_a2a/lib/ash_a2a/agent.ex:110`, stored at `:137`). Multiple agents are
  co-served via `AshA2A.Protocol.AgentSupervisor` (`protocol/agent_supervisor.ex:12`).
- Modeled as `aap:FederatedAgent` (`aap:servesDomain` 1..n, `aap:memberAgent`,
  `aap:exposesSkill`); emitted as a facade with `domains/0` and `agents/0`.
- Gates: `L26_010` (zero domains), `L26_020` (skill outside served domains).
- Legacy `aap:forDomain` on `aap:Agent` is unchanged.
