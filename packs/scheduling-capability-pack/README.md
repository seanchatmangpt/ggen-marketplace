# scheduling-capability-pack

Qualified capability contracts for the **scheduling family** (lane 3,
v26.9.30 capability ecology wave). The consumer is a capability-resolution
engine (ash_pplan v26.9.30): plans name capabilities; providers are resolved
against realizations — never the reverse.

- Namespace: `https://ggen.dev/ontology/scheduling-capability#` (`scap:`)
- Version: 0.1.0 (SemVer, `pack.toml`)
- Profile: semantic; gates are violation-row SELECTs (rows mean refusal)

## Capabilities (pinned + minted)

| identity (`dcterms:identifier` = `rdfs:label`, the resolver join key) | family | temporal kind | source |
|---|---|---|---|
| `Schedule.At` | scheduling-instant | one-shot | pinned (RESOLUTIONS.md) |
| `Schedule.Cron` | scheduling-calendar | recurring | pinned |
| `Schedule.Delay` | scheduling-relative | one-shot | pinned |
| `Schedule.Interval` | scheduling-instant | recurring | minted sibling (lane 3) |

Temporal semantics encoded per capability: `scap:temporalKind`
(one-shot | recurring), `scap:timezoneAnchoring` (none | utc | named-zone;
named-zone is DST-aware calendar anchoring — exactly what a fixed offset
cannot do), `scap:missedFirePolicy` (catch_up | skip | drop),
`scap:durability` (in-memory | durable-store). Every capability carries
input/output contracts, precondition, postcondition, typed outcomes, an
evidence requirement and — being consequence-DO — a bound authority
requirement. **Precondition as law: Schedule.At on a consequential target
requires authority**; a schedule is a policy, never a grant.

## Realizations (provider metadata: cited, never fabricated)

| realization | realizes | provider coordinates | basis |
|---|---|---|---|
| `scap:real-oban` | At, Delay, Cron, Interval | hex `oban` 2.24.1, https://hex.pm/packages/oban, https://github.com/oban-bg/oban | hex.pm citation: "Robust job processing, backed by modern PostgreSQL, SQLite3, and MySQL."; hexdocs: scheduled jobs "down to the second", `Oban.Cron` ("Automatically enqueue jobs on a cron-like schedule. Duplicate jobs are never enqueued"), `Oban.Lifeline` (orphan rescue) |
| `scap:real-quantum` | Cron | hex `quantum` 3.5.3, https://hex.pm/packages/quantum, https://github.com/quantum-elixir/quantum-core | hex.pm citation only: "Cron-like job scheduler for Elixir." No timezone/missed-job feature claims beyond that; in-memory surface means missed firings are structurally `drop` unless persistence is composed and re-qualified |
| `scap:real-otp-timer` | Delay | Erlang/OTP (`Process.send_after/3`, `:timer`), https://github.com/erlang/otp | public OTP stdlib API; pin OTP 26+ |

All carry `scap:qualificationCondition`, `scap:versionPinPolicy`, a
`scap:missedFirePolicy` declaration grounded in the cited surface, and
`qce:admitted false` until a receipted run binds an `scap:evidenceReference`.
Honest limits are recorded, not papered over: oban's missed-cron-INSERTION
semantics (occurrences missed while fully down) are NOT witnessed in the
cited docs and must be qualified at consumption before `catch_up` is claimed
for calendar patterns.

## Gates and their witnessed refusals (anti-vacuity)

Every gate is a violation-row SELECT. Each has same-stem pass/fail witnesses
(`witnesses/pass`, `witnesses/fail`; structural court `gate-court.toml`) and a
named negative fixture that fires it and only it
(`qualification/verify.py`, exit non-zero on any mismatch):

| gate | refuses | firing negative fixture |
|---|---|---|
| `gates/010_capability_requires_realization.rq` | capability without any realization | `qualification/fixtures/negative-capability-without-realization.ttl` (unrealized `Schedule.Window`) |
| `gates/020_realization_requires_qualification.rq` | realization without a qualification condition | `qualification/fixtures/negative-realization-without-qualification.ttl` |
| `gates/030_missed_fire_policy_required.rq` | capability or realization without a declared missed-fire policy (catch_up / skip / drop) | `qualification/fixtures/negative-missed-fire-policy-missing.ttl` (policy-less `Schedule.Hourly`) |
| `gates/040_consequential_requires_authority.rq` | consequence-DO capability without bound authority (Policy != Authority, ProviderAvailable != Authorized) | `qualification/fixtures/negative-authority-unbound.ttl` (unbound `Schedule.Reminder`) |
| `gates/050_capability_identity_impl_free.rq` | implementation token inside a capability identity (CAPABILITY != IMPLEMENTATION) | `qualification/fixtures/negative-provider-token-identity.ttl` (`Oban.Nightly`) |
| `gates/060_recurring_requires_timezone_anchoring.rq` | recurring capability/realization without a timezone anchor | `qualification/fixtures/negative-recurring-without-timezone.ttl` (anchor-less `Schedule.Nightly`) |

Positive fixture: `qualification/fixtures/positive.ttl` adds one fully-lawful
capability + realization binding (`Schedule.Weekdays`, named-zone recurring)
and must keep every gate at zero rows.

## Encoded invariants

`scap:plan-not-execution`, `scap:policy-not-authority`,
`scap:provider-available-not-authorized`, `scap:projection-not-source`,
`scap:generated-not-admitted` (skos:Concepts in `ontology.ttl`); mechanically
enforced where checkable by gates 020, 030, 040, 050.

## Search-ladder record: failed edges (nothing silently pruned)

1. `failed(edge_reuse_no_scheduling_family)` — no admitted pack in `packs/`
   expresses time-anchored capability contracts.
   `repository-factory-scheduler-pack` schedules repository *work* (agent
   waves/lanes), not clock-anchored capability firings, and carries no
   temporal-semantics vocabulary. Topology, not graph failure: this pack is
   the additive family.
2. `failed(edge_cross_pack_gate_union)` — `process-capability-pack` (same
   lane) is a sibling family with a near-identical contract skeleton. Its
   properties were deliberately **mirrored** into `scap:` rather than
   imported, because scoped real-ggen qualification evaluates ONE pack graph
   in isolation; cross-pack gates would need a union graph the scoped check
   does not build. N-squared drift risk is recorded and accepted for this
   wave; a shared capability-contract kernel pack is the named follow-up.
3. `failed(edge_public_vocab_temporal)` — prov/earl/dcterms/skos have no
   missed-fire-policy, timezone-anchoring or temporal-kind property; the
   TIME ontology family (time:TemporalEntity) expresses instants and
   intervals, not firing policies over schedules. Hence the scap: terms.
4. `failed(edge_ash_reactor_scheduling_steps)` — Ash.Reactor exposes Ash
   action/changeset/notification surfaces; it has no scheduling step. The
   realization surface is oban / quantum / OTP timers, cited above.
5. qce: is COMPOSED, not extended: capabilities are `rdfs:subClassOf
   qce:CapabilityVersion` and realizations reuse `qce:admitted` unchanged.
   dcp:'s closed consequence convention ("READ"|"DO") is reused as a
   convention.

## Evidence boundary

Marketplace admission and real-ggen qualification only. SELECT/CONSTRUCT
semantics; this pack grants **no DO authority**; BRCE remains the sole
consequential actuation boundary. Declaring a schedule never actuates one.

## Verification

```bash
python3.11 scripts/marketplace.py check scheduling-capability-pack   # real ggen, scoped
python3.11 packs/scheduling-capability-pack/qualification/verify.py  # anti-vacuity court
python3.11 scripts/check_gate_witness_courts.py --packs packs        # structural court
python3.11 -m pytest tests/test_scheduling_capability_pack.py        # execution falsifiers
```
