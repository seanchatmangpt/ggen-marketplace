# Tutorial: consume a marketplace pack

This tutorial uses a local marketplace checkout so pack source, consumer input, and resulting evidence are inspectable.

## 1. Record the subject

Before execution, record the marketplace commit:

```bash
git rev-parse HEAD
```

Pick a pack and read its `pack.toml`, RDF source, templates/project rules, gates, qualification fixtures, and README. Identify the pack profile and its documented authority ceiling.

## 2. Add the pack to a consumer

In the consumer `ggen.toml`:

```toml
[packs]
ggen-combinatorial-maximalism-pack = { path = "../ggen-marketplace/packs/ggen-combinatorial-maximalism-pack" }
```

Add only the consumer RDF or other admitted input the pack contract requires.

## 3. Manufacture

Run:

```bash
ggen sync run
```

Inspect the manufactured files, but do not treat file existence as behavioral correctness.

## 4. Exercise the native boundary

Run the consumer's real verifier: compiler/tests, service integration, browser test, protocol exchange, simulation court, or other repository-native acceptance command.

This is where the claim moves from "ggen manufactured bytes" toward the behavior the consumer actually cares about.

## 5. Replay

Without changing admitted inputs, rerun:

```bash
ggen sync run
```

For a deterministic pack, the second pass should converge to the same consequence. If the consumer composes `pack-maturity-pack`, run its generated fixed-point court to compare actual filesystem consequences.

## 6. Verify receipts when the consumer uses them

For the standard ggen receipt path:

```bash
ggen receipt verify
```

Receipt validity binds evidence about the manufacture/replay path; it does not confer external DO authority or universal correctness.

## 7. State what you proved

A defensible consumption receipt should identify:

- exact marketplace/pack source;
- consumer subject;
- ggen/toolchain identity;
- inputs admitted;
- consequence manufactured;
- native verifier executed;
- replay result;
- receipt result, when applicable;
- authority ceiling;
- blocked/unsupported boundaries.

Marketplace CI tells you whether the marketplace subject passed its own courts. It cannot substitute for the consumer boundary you just executed.

Next: [Take a pack through a Level-5 promotion slice](level5-promotion.md).
