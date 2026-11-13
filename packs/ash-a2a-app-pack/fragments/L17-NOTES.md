# L17 notes: complete AshA2A DSL

Standing: UNVERIFIED

## Coordinator seams (exact lines)

Resource (`templates/resource.ex.tmpl`, `use Ash.Resource` for every resource that has L17 facts):

    fragments: [{{ module_name }}.A2aL17]

Domain (`templates/domain.ex.tmpl`, only domains with `aap:a2aConfigured "true"`):

    use Ash.Domain, extensions: [AshA2A, AshA2A.Domain], fragments: [{{ module_name }}.A2aL17]

The fragments declare `extensions:` themselves (Spark fragment.ex:14 accepts `extensions:`), so the
base templates only need the `fragments:` option plus `AshA2A.Domain` in the domain extension list.

Config (`config/config.exs`, one line, after `import Config`):

    import_config "a2a_l17.exs"

Application supervision tree (one child per `aap:Endpoint`, e.g. in `application.ex`):

    children = [Demo.Edge]   # starts AshA2A.Protocol.AgentSupervisor + Bandit; rest_for_one

mix.exs deps needed by the endpoint template: `{:bandit, "~> 1.5"}`, `{:plug, "~> 1.16"}`.

## Files emitted (one output per template)

| template | output | module |
|---|---|---|
| L17_resource_a2a_fragment.ex.tmpl | lib/<app>/<resource_file>_a2a_l17.ex | `<Resource>.A2aL17` |
| L17_domain_a2a_fragment.ex.tmpl | lib/<app>/<domain_file>_a2a_l17.ex | `<Domain>.A2aL17` |
| L17_agent_configured.ex.tmpl | lib/<app>/<agent_file>_configured_l17.ex | `<Agent>.Configured` |
| L17_endpoint.ex.tmpl | lib/<app>/<endpoint_file>.ex | `<Endpoint>` (Supervisor) + `<Endpoint>.Router` |
| L17_dispatch_hooks_config.exs.tmpl | config/a2a_l17.exs | `config :ash_a2a, :dispatch_hooks` |

Mounts and the endpoint supervise `<Agent>.Configured` when `aap:agentConfigured "true"`, else the plain
agent. The shared `agent.ex.tmpl` cannot carry execution/dispatch options; the coordinator may instead fold
the `.Configured` option set into it and drop the suffix logic.

## DSL options covered (source file:line)

Skill entity, `skill :name, [resource,] :action` (dsl.ex:188-197): name :20, action :30, description :35,
tags :40, expose? :45, consequence :50, on_cancel :61, argument_mapping :73, get? :82, lease_required? :90,
examples :99, input_modes :104, output_modes :112, security_requirements :119, streaming? :128.
Nested `hddl_operator` (dsl.ex:178; parameters :157, preconditions :161, add_effects :166, delete_effects :171).
Section `a2a`: semantic_requests (dsl.ex:205). Section `authority`: gate :232, lease_duration_ms :242.
Section `hooks`: pre_dispatch :257, post_dispatch :265, ids resolved from `config :ash_a2a, :dispatch_hooks`.
Domain `agent` (domain.ex:79-143): name, description, version, url, provider, documentation_url, icon_url,
default_input_modes, default_output_modes, sign_card. `security` (domain.ex:153-241): security_scheme with
kind/location/param_name/http_scheme/bearer_format/oauth_flows/scopes/openid_url; requirements;
requirement_scopes. `transport` (domain.ex:243-380): mount (agent/path/binding/tenant/protocol_version),
extension (uri/description/required/params), extended_agent_card, user_artifacts, push_allowed_hosts,
push_retry, base_url, default_mount, streaming, push_notifications.
`use AshA2A.Agent` (agent.ex:97-102, runtime.ex:81,217,283,357,523,531,721,730): name, description, version,
require_authenticated_caller, public_skills, observe_generic_actions, strict_observe_generic_actions,
execution: mode, max_in_flight, rate_limit, cancel_in_flight, events_transport, validate_input_modes,
user_artifacts, adapter, orphan_sweep_interval_ms, orphan_lease_ms.
Plug/Bandit: `AshA2A.Domain.Router` forward (router.ex:5-48) with push_notifications and extended_card
forwarded options; `AshA2A.Protocol.AgentSupervisor` (agent_supervisor.ex:22); Bandit child, loopback default.

## Verifier rules mirrored as gates (zero rows required)

| gate | mirrors |
|---|---|
| L17_100 | verify_skills.ex refused_action_not_found / refused_action_not_public (also covers former L17_101) |
| L17_102 | duplicate skill identifier (pack-level, dsl.ex:195) |
| L17_103 | refused_argument_mapping_target |
| L17_104 | refused_type_not_json_serializable |
| L17_105 | refused_lease_required_no_authorizer |
| L17_106 | consequence enum + observe_on_mutating_action (SEC-04) |
| L17_107 | refused_mode_not_mime (verifier regex verbatim) |
| L17_108 | refused_security_requirement_undeclared (stricter: also resource subjects) |
| L17_109, L17_110 | refused_hddl_multiple_operators, refused_hddl_fact_args |
| L17_111 to L17_113 | pack-level: atom shape, raw-Elixir shape, `#{` interpolation in strings |
| L17_120 | verify_config require_agent_name; unflagged domain facts |
| L17_121, L17_122 | verify_config scheme kinds, unique names, required fields, requirements, scopes |
| L17_123 | verify_config URL and default_mount |
| L17_124 | verify_mounts (path, unique, prefix overlap, agent+binding, agent exists) + compile-order law |
| L17_125 | verify_extensions |
| L17_126 | authority gate enum, hook registry resolution, hook ordering |
| L17_127 to L17_129 | verify_execution, endpoint, boolean and positive-integer option domains |

Not mirrored (cannot be decided from the graph): on_cancel module/function existence (verify_skills.ex:267,
runtime `Code.ensure_compiled`), oauth_flows single-flow validity (`OAuthFlows.validate/1`), whether the
authorizer actually evaluates leases.

## Adversarial findings

1. Compile-order deadlock: `VerifyMounts` calls `Code.ensure_compiled(agent)` while the agent's
   `use AshA2A.Agent, resource_or_domain: Domain` needs the same Domain compiled. A domain can therefore
   never mount an agent that wraps itself. The ontology uses a separate gateway domain (no resources)
   whose mounts reference agents of another domain; L17_124 refuses the self-wrap.
2. `lease_required? true` needs an authorizer that the base resource template never emits. L17 emits
   `authorizers:` via the fragment (`aap:authorizer`). `Ash.Policy.Authorizer` with no policies forbids every
   request, so a policies lane must supply policy blocks before leased skills can run.
3. A `skill` name may not appear on both `aap:Skill` (base template) and `aap:SkillSpec` (L17): Spark
   identifier clash. L17_102 refuses it; use `aap:SkillSpec` for full-option skills.
4. `AshA2A.Domain` sections need `extensions: [AshA2A, AshA2A.Domain]`; the base domain template only lists
   `AshA2A`.
5. `hooks` ids with no registry entry fail the dispatch closed at runtime; L17_126 requires every id to be
   registered, and the registry file is generated. Hook module bodies are not generated (callback
   signature not in the dispatch prompt; not invented).
6. `get?: true` is declarative only in ash_a2a; L17_129 additionally requires a read action (stricter).

## Known gaps

- Domain-level skills (`skill :n, Resource, :action` on a domain, dsl.ex:191) are not modeled; only
  resource-level skills.
- `aap:Skill` (base template) still lacks the extended options; use `aap:SkillSpec`.
- Default-projected action type warnings (verify_skills.ex:95-149) are warnings, not mirrored.
- Hook module implementations, `AshA2A.Transport.GRPC.Server.Endpoint` for `:grpc` mounts (Router answers 501),
  `sign_with`/`force_ssl`/`serve_schemas` Plug options, `config :ash_a2a, :execution`
  and `:require_authenticated_caller` app-env globals are not modeled.
- Group ordering of `security_requirements` relies on Tera `group_by` key order (alphabetical string keys).
- Templates were not rendered; Tera constructs (`group_by`, `json_encode`, `starting_with`) are
  UNVERIFIED against ggen 26.11.5.
