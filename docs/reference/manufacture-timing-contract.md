# Reference: manufacture timing contract

Exact contract for the wall-clock observation carried by qualification reports and the tool that consumes it. Timing is an observation; it never changes a pack's standing. Rationale: [Why manufacture time and standing time are different clocks](../explanation/manufacture-time-vs-standing-time.md).

## Report field

`scripts/qualify_packs.py --report <path>` adds a top-level `timings` object beside the existing `packs` array:

```json
"timings": {
  "schema": "https://ggen.dev/marketplace/qualification-timings/v1",
  "workers": <int>,
  "pack_seconds": { "<pack-name>": <non-negative number>, ... }
}
```

- `pack_seconds[name]` is the monotonic wall-clock for that pack's whole bounded qualification (capsule preparation, both ggen passes, snapshots, and any opt-in generated-crate verification), rounded to milliseconds.
- Timings are deliberately **outside** the per-pack records, so those records remain a deterministic function of the subject. The `timings` object is non-deterministic by nature.
- Every qualified pack has an entry, whatever its status. REFUSED/SKIPPED/WARN timings are recorded but excluded from ALIVE distributions.

## `scripts/manufacture_timing.py`

```text
manufacture_timing.py summarize <report> [--json]
manufacture_timing.py compare <baseline> <candidate> [--json]
```

Exit `0` on success; `2` with a typed refusal on stderr otherwise.

### Refusals

- `REFUSED:TIMING_REPORT_UNREADABLE` — file missing or not JSON;
- `REFUSED:TIMING_REPORT_SCHEMA` — not a qualification `v1` report;
- `REFUSED:TIMING_REPORT_HAS_NO_TIMINGS` — produced before timings existed, or schema mismatch;
- `REFUSED:TIMING_REPORT_PACK_SECONDS_INVALID` — a non-numeric or negative duration.

### `summarize`

Reports pack count, status counts, and over ALIVE packs only: count, `p50`, `p95` (nearest-rank), max, and serial total, plus `workers` and the `ggen` identity string recorded in the report.

### `compare`

A pack is **paired** only when it is `ALIVE` in both reports with identical `source_sha256`. Otherwise it is listed under `excluded` with one of: `missing_in_baseline`, `missing_in_candidate`, `not_alive_in_both:<a>-><b>`, `source_changed`, `timing_missing`. Excluded packs never enter a ratio.

Output (`--json`, schema `https://ggen.dev/marketplace/manufacture-timing/v1`):

- `pairs[]` — `name`, `before_seconds`, `after_seconds`, `ratio` (`null` when the baseline is 0);
- `comparable` — `count`, `before_total_serial`, `after_total_serial`, `total_ratio`, `median_ratio`;
- `caveats.toolchain_changed` — the two reports' `ggen` identity strings differ;
- `caveats.workers_match` — both runs used the same worker count;
- `claims_not_made[]` — fixed statements of what the numbers do not establish.

A ratio below 1 is attributable to a toolchain or generator change only when `toolchain_changed` is true, `workers_match` is true, and the result repeats across runs.

## Not established

Timing does not establish correctness, consumer or runtime behavior, external consequence, customer acceptance, or `DO` authority, and it does not define a service-level objective.
