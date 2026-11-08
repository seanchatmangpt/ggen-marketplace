# CSCB honest-comparison fixture — stage-3 counterpart workload profile.
# All thresholds here are derived from this fixture's own defaults and
# BEAM realities, NOT copied from the RFC's illustrative table.
[
  workload: [
    ops: 2_000,
    payload_bytes: 256,
    latency_us: 20
  ],
  court: [
    # BEAM has background GC; the pack path's GC delta is judged against
    # a ratio of the measured status-quo delta, never against literal 0.
    gc_delta_threshold_ratio: 0.01,
    require_pack_reductions_lower: true
  ]
]
