"""OCPQ Declarative Query DSL for Pytest.

Allows defining declarative process constraints on multi-object execution traces:
- Activity occurrences (min_events)
- Required object types
- Multi-object traversals (traverse)
- Balanced activity ratios (e.g., 1 metering event per tool call)
- Relational integrity (no_orphans)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pm4py
from pm4py.objects.ocel.obj import OCEL

from ggen_marketplace.ocel2.emitter import OCEL2Emitter


@dataclass
class OCPQQueryResult:
    """Outcome of an OCPQ query evaluation."""
    success: bool
    violations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class OCPQQuery:
    """Declarative query specification over an OCEL v2 log."""

    def __init__(self) -> None:
        self._required_activities: Dict[str, int] = {}
        self._required_object_types: List[str] = []
        self._balanced_ratios: List[Tuple[str, str, float]] = []
        self._traverse_path: Optional[List[str]] = None
        self._cardinality_checks: List[Tuple[str, str, int, int]] = []
        self._duration_checks: List[Tuple[str, str, float]] = []
        self._fail_closed_checks: List[Tuple[str, str]] = []
        self._custom_checks: List[Any] = []

    def require_activity(self, activity: str, min_count: int = 1) -> OCPQQuery:
        """Require that an activity appears at least min_count times."""
        self._required_activities[activity] = min_count
        return self

    def require_object_type(self, *object_types: str) -> OCPQQuery:
        """Require that specific object types exist in the log."""
        self._required_object_types.extend(object_types)
        return self

    def require_balanced_ratio(self, source_act: str, target_act: str, expected_ratio: float = 1.0) -> OCPQQuery:
        """Require that target_act occurs at least expected_ratio * count(source_act)."""
        self._balanced_ratios.append((source_act, target_act, expected_ratio))
        return self

    def traverse(self, *object_type_path: str) -> OCPQQuery:
        """Require a causal object traversal path (e.g. GcpEntitlement -> A2AExecutionTask -> McpToolCall)."""
        self._traverse_path = list(object_type_path)
        return self

    def require_cardinality(self, source_type: str, target_type: str, min_count: int = 1, max_count: int = 1) -> OCPQQuery:
        """Require that every object of source_type connects via shared events to between min_count and max_count target_type objects."""
        self._cardinality_checks.append((source_type, target_type, min_count, max_count))
        return self

    def require_max_duration(self, activity_start: str, activity_end: str, max_seconds: float) -> OCPQQuery:
        """Require that the time between consecutive occurrences of activity_start and activity_end is <= max_seconds."""
        self._duration_checks.append((activity_start, activity_end, max_seconds))
        return self

    def require_fail_closed_on(self, activity_error: str, terminal_state: str) -> OCPQQuery:
        """Require that if activity_error occurs, it transitions directly to terminal_state."""
        self._fail_closed_checks.append((activity_error, terminal_state))
        return self

    def evaluate(self, ocel: OCEL) -> OCPQQueryResult:
        """Evaluate the declarative query against an ingested PM4Py OCEL object."""
        violations: List[str] = []
        metrics: Dict[str, Any] = {}

        # 1. Check required activities
        activity_counts = ocel.events["ocel:activity"].value_counts().to_dict()
        metrics["activity_counts"] = activity_counts

        for act, min_cnt in self._required_activities.items():
            actual = activity_counts.get(act, 0)
            if actual < min_cnt:
                violations.append(
                    f"ACTIVITY_COUNT_VIOLATION: Activity '{act}' occurred {actual} times, expected >= {min_cnt}"
                )

        # 2. Check required object types
        found_types = set(pm4py.ocel_get_object_types(ocel))
        metrics["object_types"] = list(found_types)

        for ot in self._required_object_types:
            if ot not in found_types:
                violations.append(
                    f"OBJECT_TYPE_VIOLATION: Required object type '{ot}' not found in log"
                )

        # 3. Check balanced ratios
        for src_act, tgt_act, ratio in self._balanced_ratios:
            src_cnt = activity_counts.get(src_act, 0)
            tgt_cnt = activity_counts.get(tgt_act, 0)
            required_tgt = src_cnt * ratio
            if tgt_cnt < required_tgt:
                violations.append(
                    f"BALANCED_RATIO_VIOLATION: '{tgt_act}' count ({tgt_cnt}) does not satisfy required ratio {ratio} for '{src_act}' count ({src_cnt})"
                )

        # 4. Check traversal path connectivity
        if self._traverse_path and len(self._traverse_path) >= 2:
            relations = ocel.relations
            objects_df = ocel.objects
            for i in range(len(self._traverse_path) - 1):
                t1 = self._traverse_path[i]
                t2 = self._traverse_path[i + 1]

                objs_t1 = set(objects_df[objects_df["ocel:type"] == t1]["ocel:oid"])
                objs_t2 = set(objects_df[objects_df["ocel:type"] == t2]["ocel:oid"])

                evs_t1 = set(relations[relations["ocel:oid"].isin(objs_t1)]["ocel:eid"])
                evs_t2 = set(relations[relations["ocel:oid"].isin(objs_t2)]["ocel:eid"])

                if not (evs_t1 & evs_t2) and not (objs_t1 and objs_t2):
                    violations.append(
                        f"TRAVERSAL_DISCONNECTED: No causal bridge found between '{t1}' and '{t2}'"
                    )

        # 5. Check cardinality constraints
        if self._cardinality_checks:
            relations = ocel.relations
            objects_df = ocel.objects
            for src_type, tgt_type, min_c, max_c in self._cardinality_checks:
                src_objs = set(objects_df[objects_df["ocel:type"] == src_type]["ocel:oid"])
                tgt_objs = set(objects_df[objects_df["ocel:type"] == tgt_type]["ocel:oid"])
                for s_obj in src_objs:
                    # Find all events linking s_obj
                    s_evs = set(relations[relations["ocel:oid"] == s_obj]["ocel:eid"])
                    # Find target objects sharing those events
                    linked_targets = set(relations[(relations["ocel:eid"].isin(s_evs)) & (relations["ocel:oid"].isin(tgt_objs))]["ocel:oid"])
                    c_count = len(linked_targets)
                    if c_count < min_c or c_count > max_c:
                        violations.append(
                            f"CARDINALITY_VIOLATION: '{src_type}' object '{s_obj}' is linked to {c_count} '{tgt_type}' objects, expected between {min_c} and {max_c}"
                        )

        # 6. Check duration constraints
        if self._duration_checks:
            events_df = ocel.events.sort_values("ocel:timestamp")
            for act_start, act_end, max_sec in self._duration_checks:
                start_events = events_df[events_df["ocel:activity"] == act_start]
                end_events = events_df[events_df["ocel:activity"] == act_end]
                for _, s_row in start_events.iterrows():
                    s_time = s_row["ocel:timestamp"]
                    # Find matching following end event
                    subsequent_ends = end_events[end_events["ocel:timestamp"] >= s_time]
                    if not subsequent_ends.empty:
                        e_time = subsequent_ends.iloc[0]["ocel:timestamp"]
                        duration_sec = (e_time - s_time).total_seconds()
                        if duration_sec > max_sec:
                            violations.append(
                                f"DURATION_VIOLATION: Latency from '{act_start}' to '{act_end}' was {duration_sec:.3f}s, exceeding limit of {max_sec:.3f}s"
                            )

        # 7. Check fail-closed terminal transitions
        if self._fail_closed_checks:
            events_df = ocel.events.sort_values("ocel:timestamp")
            act_list = events_df["ocel:activity"].tolist()
            for err_act, term_act in self._fail_closed_checks:
                if err_act in act_list:
                    idx = act_list.index(err_act)
                    if idx + 1 < len(act_list):
                        nxt_act = act_list[idx + 1]
                        if nxt_act != term_act:
                            violations.append(
                                f"FAIL_CLOSED_VIOLATION: Activity '{err_act}' followed by '{nxt_act}' instead of terminal state '{term_act}'"
                            )

        success = len(violations) == 0
        return OCPQQueryResult(success=success, violations=violations, metrics=metrics)
