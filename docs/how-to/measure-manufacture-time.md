# How to measure manufacture time across toolchain changes

Use this when you want evidence for or against "manufacturing got faster" for unchanged pack sources. It does not measure correctness; see the [timing contract](../reference/manufacture-timing-contract.md) for what the numbers exclude.

## 1. Produce a baseline report

Admit configuration and install the admitted ggen as in [Qualify all packs](qualify-all-packs.md), then:

```bash
python3 scripts/qualify_packs.py --report /tmp/qualification-baseline.json
python3 scripts/manufacture_timing.py summarize /tmp/qualification-baseline.json
```

Keep the baseline's worker count fixed for every later run you intend to compare.

## 2. Change exactly one thing

Change the toolchain (for example the admitted ggen pin via `marketplace.toml` and re-admission) or the generator/pack under study. Do not edit pack sources you want to compare: a changed `source_sha256` excludes that pack from pairing.

## 3. Produce the candidate report and compare

```bash
python3 scripts/qualify_packs.py --report /tmp/qualification-candidate.json
python3 scripts/manufacture_timing.py compare \
  /tmp/qualification-baseline.json /tmp/qualification-candidate.json --json
```

## 4. Read the result conservatively

- Check `caveats.toolchain_changed` and `caveats.workers_match` first.
- Repeat each side several times; wall-clock depends on host load. A single pair of runs is an anecdote.
- Read `excluded`: a large excluded set means the comparison covers few subjects.
- A pack REFUSED in the candidate is a regression to fix, not a timing datum.

## 5. Record, without over-claiming

Record the two report paths, both `ggen` identity strings, worker counts, and the ratios. State only what the measured boundary supports: bounded ggen manufacture/replay wall-clock for the paired ALIVE packs on that host. Do not turn it into a statement about reach, consumers, or authority.
