# Ash Extension Vision 2040

## Canonical manufacturer

`ash-extension-pack` is the one canonical reusable manufacturer for Ash/Spark extensions.

The abstraction is:

```text
Semantic contract
  x capability profile
  x qualified realizations
        |
        v
ash-extension-pack
        |
        v
Spark extension specification
        |
        +-- transformers
        +-- verifiers
        +-- Info/introspection
        +-- structured errors
        +-- Igniter installation
        +-- Reactor realization
        +-- lifecycle/activation adapters
        +-- durability/replay
        +-- observation/evidence
        +-- usage/documentation projections
```

A newly discovered reusable Ash pattern extends this manufacturer. It does not create
another generic Ash-extension pack.

## Consolidation law

The decision order is mandatory:

```text
REUSE -> COMPOSE -> EXTEND -> INVENT
```

1. **REUSE** an existing capability family when it already represents the requirement.
2. **COMPOSE** existing capability families when their cross product represents it.
3. **EXTEND** the canonical ontology/templates/gates when a reusable semantic delta remains.
4. **INVENT** only an irreducible semantic concept that is outside the closure of the
   existing families. Even then, add it to `ash-extension-pack`; do not create a sibling
   generic Ash manufacturer.

Pack proliferation is therefore an invalid plan for reusable Ash-extension semantics.

Domain-specific packs remain legitimate when they own independent domain meaning. GraphLaw,
R2RML, P-PLAN, PROV-O, OCEL, SA2A, and similar authorities are not absorbed into the Ash
ontology. Their Ash projections are consumers/profiles of this manufacturer.

## Spark semantic waist

For semantic facts:

```text
Spark <=> implementation
```

Qualification must establish both:

```text
implementation_semantics - spark_semantics = {}
spark_semantics - consumed_semantics = {}
```

The first difference detects hidden implementation semantics. The second detects decorative
or dead DSL. Only explicitly admitted mechanical details that carry no independent semantic
meaning may remain outside Spark.

## Generalizable capability families

The canonical manufacturer grows by capability family rather than package name:

- **Declarative surface** — sections, entities, nested entities, schemas, positional args,
  singleton entities, resource/domain targets.
- **Compilation** — transformers, ordering, normalization, persistence, derived metadata.
- **Admission** — verifiers, composition constraints, satisfiability constraints, refusals.
- **Introspection** — Info getters, result/bang/predicate forms, semantic digests.
- **Error model** — invalid, forbidden, conflict, unavailable, execution classifications.
- **Installation** — dependencies, extension registration, formatter registration,
  configuration mutation, migration, idempotence.
- **Execution** — Ash action boundary, Reactor workflow/steps, dependencies, retry,
  compensation, undo, return.
- **Context** — actor, tenant, authorization, trace context, exact subject identity.
- **Lifecycle** — state, transition, transition constraints.
- **Activation** — schedule, queue, retry policy, uniqueness, durable activation.
- **Durability** — checkpoint, replay, signal, migration, idempotency, recovery.
- **Observation** — telemetry, traces, events, OCEL projection, receipts.
- **Knowledge projection** — UsageRules, skills, documentation, diagrams.

Named frameworks are realizations of these families. For example, AshOban may realize
durable activation; AshStateMachine may realize lifecycle; Splode may realize the structured
error model; Reactor may realize execution. Capability identity remains stable when a
realization changes.

## HDDL lifecycle

The root task is `manufacture_ash_extension`:

```text
OBSERVE
  -> ADMIT-SEMANTICS
  -> PLAN-EXTENSION
  -> CONSTRUCT-SPARK-SURFACE
  -> PROJECT-IMPLEMENTATION
  -> COMPOSE
  -> QUALIFY
  -> STAND
  -> LEARN
```

The planner resolves every requested capability through REUSE/COMPOSE/EXTEND/INVENT before
projection.

## Qualification and burn-in

Burn-in is a qualification method, not a sibling pack:

```text
QUALIFY
  -> static courts
  -> composition courts
  -> Spark/implementation parity
  -> mutation league
  -> regeneration
  -> temporal burn-in
```

Temporal burn-in composes real work with history, concurrency, failure, recovery, replay,
restart, regeneration, reinstall, resource pressure, semantic-digest parity, and evidence.

A process remaining alive is not sufficient for PASS.

## Recursive learning

A surviving reusable gap executes:

```text
preserve failing witness
  -> classify semantic vs mechanical
  -> generalize missing capability
  -> extend ash-extension-pack
  -> regenerate
  -> requalify
  -> rerun burn-in
```

The fixed point is a canonical manufacturer whose reusable semantic closure grows while
consumer-specific handwritten semantic code trends toward zero.
