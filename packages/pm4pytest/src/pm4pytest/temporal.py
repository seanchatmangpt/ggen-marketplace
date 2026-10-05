"""pm4pytest.temporal

Temporal profile and SLA bound conformance checking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TemporalResult:
    """Evaluation result for temporal SLA bounds."""
    success: bool
    violations: List[str] = field(default_factory=list)
    latencies: Dict[str, float] = field(default_factory=dict)


class TemporalSLA:
    """Enforces inter-activity latency ceilings and SLA limits."""

    def __init__(self) -> None:
        self._max_latencies: List[Tuple[str, str, float]] = []

    def require_max_latency(self, source_act: str, target_act: str, max_seconds: float) -> TemporalSLA:
        """Require that the latency between source_act and subsequent target_act <= max_seconds."""
        self._max_latencies.append((source_act, target_act, max_seconds))
        return self

    def evaluate(self, events: List[Dict[str, Any]]) -> TemporalResult:
        """Evaluate temporal SLA bounds across the emitted event sequence."""
        violations: List[str] = []
        latencies: Dict[str, float] = {}

        # Map activities with timestamps
        act_times: Dict[str, List[datetime]] = {}
        for ev in events:
            act = ev.get("concept:name") or ev.get("type")
            t = ev.get("time:timestamp") or ev.get("time")
            if act and t:
                if isinstance(t, str):
                    t_val = datetime.fromisoformat(t.replace("Z", "+00:00"))
                else:
                    t_val = t
                act_times.setdefault(act, []).append(t_val)

        for src, tgt, max_sec in self._max_latencies:
            src_list = act_times.get(src, [])
            tgt_list = act_times.get(tgt, [])

            if src_list and tgt_list:
                # Calculate delta between earliest source and subsequent target
                earliest_src = min(src_list)
                matching_tgts = [t for t in tgt_list if t >= earliest_src]
                if matching_tgts:
                    first_tgt = min(matching_tgts)
                    delta_sec = (first_tgt - earliest_src).total_seconds()
                    pair_key = f"{src}->{tgt}"
                    latencies[pair_key] = delta_sec

                    if delta_sec > max_sec:
                        violations.append(
                            f"TEMPORAL_SLA_BREACH: Latency for '{pair_key}' was {delta_sec:.3f}s, exceeding SLA limit of {max_sec:.3f}s."
                        )

        success = len(violations) == 0
        return TemporalResult(success=success, violations=violations, latencies=latencies)
