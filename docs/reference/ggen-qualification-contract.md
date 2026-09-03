# Reference: ggen qualification contract

The marketplace has distinct acceptance layers. `python3 scripts/marketplace.py validate` establishes structural/source/catalog admission. `python3 scripts/qualify_packs.py` establishes bounded load/manufacture/replay qualification through the real ggen runtime.

Neither layer is a substitute for a pack's domain/runtime court or consequential DO authority.

## Runtime identity

The canonical qualification rail obtains the ggen release version, exact release commit, platform archive names, and SHA-256 digests from **admitted `marketplace.toml`**. `scripts/install-ggen.sh` verifies release identity and the selected asset digest before accepting the binary.

Operational docs and wrappers must not duplicate a particular ggen version. The current version is executable configuration and can change independently of prose.

Supported platforms are whatever complete asset matrix is admitted by `marketplace.toml` and the installer contract. Unsupported platform/runtime combinations refuse rather than selecting an unverified fallback.

## Configuration admission

Before qualification:

```bash
bash scripts/admit-config.sh marketplace.toml /tmp/ggen-marketplace-admitted.json
```

Qualification worker counts and timeout bounds are read from this admitted artifact. Raw configuration is observation, not executable authority.

## Subject selection

The qualification subject is exactly the admitted pack set returned by the marketplace source calculus. There is no second hand-maintained inventory and no pack-name exception table.

The derived packaging profile determines the capsule shape:

- `projection` — create an isolated consumer, reference the marketplace pack through ggen's local `[packs]` contract, add a graph-load probe, and union only pack-owned positive consumer facts/extra ontologies;
- `semantic` — create an isolated declarative ggen project, load the pack's native ontology files directly, attach native SPARQL gates, and manufacture a probe through an explicit generation rule;
- `project` — copy the complete pack into an isolated project capsule, overlay only pack-owned `qualification/project/**` positive inputs, and run that pack's own `ggen.toml`.

## Pack-owned qualification inputs

A capability that needs positive consumer facts owns the specimen. The generic court must not learn special pack names.

Recognized surfaces include:

```text
qualification/consumer.ttl
qualification/consumer/*.ttl
qualification/project/**
qualification.toml
```

Paths named by a qualification contract must remain relative and inside the owning pack. Absolute paths, traversal, missing files, malformed TOML, or malformed tables refuse.

Qualification fixtures are **synthetic admitted inputs**. They can prove that a compiler/gate path accepts a bounded positive subject; they cannot become an external observation, customer consequence, benchmark result, cloud receipt, or authority grant.

## Per-pack law

For every admitted pack `p`, the court establishes the configured bounded form of:

```text
source_digest_before(p)
→ isolated capsule(p)
→ ggen sync run
→ consequence_1
→ ggen sync run
→ consequence_2
→ consequence_1 == consequence_2
→ source_digest_after(p) == source_digest_before(p)
```

Timeout/concurrency numeric values come from admitted configuration. Pack isolation prevents one pack's HOME/XDG/runtime residue from becoming another pack's input.

Runtime-only roots may be excluded from consequence comparison when they are explicitly part of the qualification contract; canonical marketplace source and manufactured non-runtime consequences remain observable.

Projection/semantic packs additionally manufacture a trivial marketplace probe. The probe proves the selected graph was loaded and manufacture completed; it does not promote RDF claims to external truth.

## Repository-level law

The permanent GitHub qualification rail should establish:

1. checkout of the exact PR head or exact default-branch subject, not an accidental synthetic merge subject;
2. mechanical exact-SHA assertion;
3. admitted marketplace configuration;
4. structural + repository Diátaxis validation;
5. deterministic catalog projection;
6. admitted-corpus fingerprinting;
7. digest/identity-verified ggen installation;
8. complete all-pack qualification;
9. clean source tree after qualification;
10. absence of temporary migration/diagnostic actuators that are not part of the repository contract.

Permanent CI remains read-only with respect to pack source. CI must not rewrite the branch to make a court pass.

## Report

With `--report PATH`, qualification emits deterministic-shape JSON describing the exact pack records and status. Timing measurements should not become semantic marketplace state when scheduler noise would make the receipt nondeterministic.

A successful record binds pack identity/profile, source identity, consequence identity/count, and the bounded court result. Failures carry typed refusal information.

## Refusals

Representative refusal families cover:

- missing/invalid admitted runtime/configuration;
- invalid timeout/worker law;
- malformed qualification contract;
- pack timeout;
- ggen sync failure;
- missing probe;
- nondeterministic replay;
- canonical-source mutation.

The complete corpus run exits nonzero when any admitted pack refuses. Partial success cannot masquerade as complete marketplace qualification standing.

## Relationship to Level 5

This court primarily closes the **manufacture/replay** dimension for the exact marketplace subject. A pack's Level-5 promotion still requires its domain-specific semantic/admission completeness, meaningful negative witnesses, claimed real consumer/runtime execution, receipt semantics, authority fencing, composition/class closure, and Diátaxis correspondence.

`pack-maturity-pack` can compose reusable fixed-point/receipt/Diátaxis courts into a consumer, but it cannot manufacture domain execution evidence.

See [Level-5 maturity contract](level5-maturity-contract.md).

## Authority boundary

The qualification rail exercises ggen's bounded filesystem manufacturer. It does **not** execute manufactured applications, Terraform, emitted GitHub Actions, MCP calls, cloud APIs, physical actuators, or arbitrary external effects.

Therefore exact-head all-pack qualification may establish deterministic pack load/manufacture/replay standing for the admitted marketplace subject. It cannot establish generated-program runtime correctness, customer acceptance, benchmark SOTA, cloud authority, physical-world consequence, organizational acceptance, or BRCE DO standing.
