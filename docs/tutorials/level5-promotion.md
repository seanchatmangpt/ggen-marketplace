# Tutorial: take a pack through a Level-5 promotion slice

This tutorial demonstrates the **promotion method**, not a universal claim that the example pack becomes globally Level 5. You will establish exact subject identity, close a mechanical maturity slice with `pack-maturity-pack`, exercise deterministic manufacture, verify a receipt, and produce the four Diátaxis quadrants that a domain pack must then specialize with its own facts and runtime evidence.

## What you will learn

You will move through:

```text
observe → admit → compose → manufacture → verify → receipt → replay → standing
```

The tutorial stops at filesystem/consumer evidence. It does not grant external DO authority.

## 1. Choose and inspect a real pack

Pick a pack you can safely compose into a disposable consumer. Record the exact marketplace commit before you begin:

```bash
git rev-parse HEAD
```

Read the pack's `pack.toml`, RDF source, templates/project rules, gates, qualification fixtures, and README. Write down what you think is authoritative and what you expect it to manufacture.

If you cannot identify canonical semantic source, stop: that is the first maturity gap.

## 2. Create a disposable consumer

Create a small consumer project with a `ggen.toml`. Reference the chosen pack and `pack-maturity-pack` by path:

```toml
[project]
name = "level5-promotion-lab"

[packs]
my-pack = { path = "../ggen-marketplace/packs/my-pack" }
pack-maturity-pack = { path = "../ggen-marketplace/packs/pack-maturity-pack" }
```

Add only the consumer RDF required by `my-pack`. Do not invent external observations merely to make qualification pass; fixtures are synthetic admitted inputs and must be treated as such.

## 3. Manufacture once

Run the real manufacturer:

```bash
ggen sync run
```

Inspect the resulting files. This proves only that the admitted manufacturer produced those consequences for this bounded subject.

Run the consumer's native verifier next. For a Rust consumer that may be:

```bash
cargo test
```

Use the actual repository-native verifier for your pack instead of substituting a convenient unit test.

## 4. Prove the fixed point

Run manufacture again without changing inputs:

```bash
ggen sync run
```

Then run the generated `pack_maturity_regeneration` test supplied by `pack-maturity-pack` in the consumer's native test suite. It compares actual filesystem consequences across repeated manufacture.

If the bytes change, treat the failure as a real nondeterminism signal until you have a concrete explanation. Do not simply relax the court.

## 5. Verify the receipt

Run:

```bash
ggen receipt verify
```

The generated receipt court from `pack-maturity-pack` expects the receipt chain to verify. A valid receipt proves the receipt property it checks; it does not prove every domain claim in the generated artifact.

## 6. Inspect the generated Level-5 docs

The maturity pack projects four documentation surfaces under the consumer's Level-5 docs area:

- Tutorial;
- How-to;
- Reference;
- Explanation.

Run the generated Level-5 Diátaxis court. Its structural checks should refuse if a quadrant or required semantic/authority/replay/falsifier marker is missing.

Now read the four files. Notice that the generic pack can provide the **shape**, but it cannot truthfully fill in your domain-specific invariants, negative witnesses, external consequence, or authority ceiling. Add those facts at the composing pack's canonical semantic/documentation source, then regenerate rather than hand-editing generated consequences.

## 7. Score the 5 × 7 matrix

Use [the Level-5 maturity contract](../reference/level5-maturity-contract.md). For the pack you exercised, score:

- semantic source;
- admission;
- manufacture;
- execution;
- receipt/replay;
- authority fence;
- composition.

Your mechanical regeneration and receipt slices may now have strong evidence while domain execution or composition remains L2/L3/L4. Keep those dimensions separate.

## 8. Add one real negative witness

Choose one invalid domain state already represented by the pack's admission logic. Mutate the disposable consumer to produce that state and run the actual gate/manufacturing path.

The correct result is a deterministic refusal. Restore the positive subject afterward and rerun the positive court.

If no meaningful invalid state can be named, record that as a domain admission gap instead of fabricating one.

## 9. State the authority ceiling

For this tutorial, the default ceiling is:

```text
SELECT / CONSTRUCT only
```

unless the chosen consumer has an explicitly admitted, separately receipted DO path. Generated Terraform, GitHub Actions, MCP intents, API payloads, or deployment specifications remain construction artifacts until the responsible runtime admits and executes them.

## 10. Produce a scoped promotion receipt

Your final note should include:

```text
repository + exact SHA
pack + version + profile
consumer identity
semantic source inspected
ggen/toolchain identity
commands and exit codes
fixed-point result
native verifier result
negative witness + refusal
receipt/replay result
Diátaxis result
authority ceiling
remaining 5×7 gaps
standing
```

If only the bounded consumer slice executed successfully, claim only that slice. The correct outcome of this tutorial is not necessarily `L5`; it is an evidence-backed maturity map that makes the next gate obvious.

Next: [How to promote a pack to Level 5](../how-to/promote-a-pack-to-level5.md).
