# Tutorial: consume a marketplace pack

A guided walk through consuming a pack from a local marketplace checkout, ending with a receipt you could defend. It reuses the consumer from [`examples/hello-pack`](../../examples/hello-pack/README.md) so every command below runs as written. For the terse recipe (catalog archives, authority, standing), see [How to consume a pack](../how-to/consume-a-pack.md).

Prerequisite: `ggen` on `PATH` ([Install ggen](../how-to/install-ggen.md)).

## 1. Record the subject

Before executing anything, record the exact marketplace commit and toolchain:

```bash
git rev-parse HEAD
ggen --version
```

Read the pack you will consume: `pack.toml`, RDF source, templates, gates, and any README. Note the profile (`project`, `projection`, or `semantic`) and the documented authority ceiling. Those two facts decide what a consumer must supply.

## 2. Copy the example consumer

```bash
cp -R examples/hello-pack /tmp/consume-tutorial
cd /tmp/consume-tutorial/consumer
```

Open `ggen.toml`. The `[packs]` table is the only link between consumer and pack:

```toml
[packs]
hello-pack = { path = "../pack" }
```

To consume a real marketplace pack instead, point `path` at `packs/<name>` in your checkout and add only the consumer RDF that pack's contract requires.

## 3. Manufacture

```bash
ggen sync run
```

You should see `output/greeting.txt`. File existence is not behavioral correctness; it only says ggen wrote bytes.

## 4. Exercise the native boundary

Run the consumer's real verifier. Here the boundary is a byte comparison:

```bash
test "$(cat output/greeting.txt)" = "Hello from ggen."
```

For a real consumer this is the compiler, test suite, service integration, browser test, protocol exchange, or simulation court that establishes the behavior you care about.

## 5. Replay

Without changing admitted inputs, run again and compare bytes:

```bash
cp output/greeting.txt ../greeting.first && ggen sync run && cmp output/greeting.txt ../greeting.first
```

A deterministic pack converges. For larger consumers compose `pack-maturity-pack` and run its generated fixed-point court.

## 6. Verify receipts, if your consumer emits them

```bash
ggen receipt verify
```

The tiny example emits no receipt, so skip this here. Where receipts exist, validity binds evidence about the manufacture/replay path; it confers neither external DO authority nor universal correctness.

## 7. State what you proved

A defensible consumption receipt names: exact marketplace/pack source, consumer subject, ggen identity, admitted inputs, consequence manufactured, native verifier executed, replay result, receipt result (when applicable), authority ceiling, and blocked/unsupported boundaries.

Marketplace CI reports on the marketplace subject only; it cannot substitute for the consumer boundary you just ran.

## See Also

- [How to consume a pack](../how-to/consume-a-pack.md)
- [Tutorial: build your first ggen pack](first-pack.md)
- [Take a pack through a Level-5 promotion slice](level5-promotion.md)
