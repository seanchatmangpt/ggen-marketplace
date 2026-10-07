"""pm4pytest.ocpq

Object-Centric Process Querying (OCPQ) DSL for declaring multi-object process invariants.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pm4py
from pm4py.objects.ocel.obj import OCEL


@dataclass
class OCPQResult:
    """Evaluation result for an OCPQ query."""
    success: bool
    violations: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class OCPQ:
    """Declarative query builder for Object-Centric Process Mining."""

    def __init__(self) -> None:
        self._required_activities: Dict[str, int] = {}
        self._required_object_types: List[str] = []
        self._balanced_ratios: List[Tuple[str, str, float]] = []
        self._traverse_path: Optional[List[str]] = None
        self._cardinality_checks: List[Tuple[str, str, int, int]] = []
        self._duration_checks: List[Tuple[str, str, float]] = []
        self._fail_closed_checks: List[Tuple[str, str]] = []

    def require_activity(self, activity: str, min_count: int = 1) -> OCPQ:
        """Require an activity to appear at least min_count times."""
        self._required_activities[activity] = min_count
        return self

    def require_object_type(self, *object_types: str) -> OCPQ:
        """Require domain object types to be present."""
        self._required_object_types.extend(object_types)
        return self

    def require_balanced_ratio(self, source_act: str, target_act: str, expected_ratio: float = 1.0) -> OCPQ:
        """Require that target_act occurs at least expected_ratio * count(source_act)."""
        self._balanced_ratios.append((source_act, target_act, expected_ratio))
        return self

    def traverse(self, *object_type_path: str) -> OCPQ:
        """Require a multi-object causal traversal path (e.g., A -> B -> C)."""
        self._traverse_path = list(object_type_path)
        return self

    def require_cardinality(self, source_type: str, target_type: str, min_count: int = 1, max_count: int = 1) -> OCPQ:
        """Require that every object of source_type connects via shared events to between min_count and max_count target_type objects."""
        self._cardinality_checks.append((source_type, target_type, min_count, max_count))
        return self

    def require_max_duration(self, activity_start: str, activity_end: str, max_seconds: float) -> OCPQ:
        """Require that the time between consecutive occurrences of activity_start and activity_end is <= max_seconds."""
        self._duration_checks.append((activity_start, activity_end, max_seconds))
        return self

    def require_fail_closed_on(self, activity_error: str, terminal_state: str) -> OCPQ:
        """Require that if activity_error occurs, it transitions directly to terminal_state."""
        self._fail_closed_checks.append((activity_error, terminal_state))
        return self

    def evaluate(self, ocel: OCEL) -> OCPQResult:
        """Evaluate the OCPQ query against an OCEL object."""
        violations: List[str] = []
        metrics: Dict[str, Any] = {}

        # 1. Activities
        activity_counts = ocel.events["ocel:activity"].value_counts().to_dict()
        metrics["activity_counts"] = activity_counts

        for act, min_cnt in self._required_activities.items():
            actual = activity_counts.get(act, 0)
            if actual < min_cnt:
                violations.append(
                    f"OCPQ_ACTIVITY_VIOLATION: Activity '{act}' occurred {actual} times, expected >= {min_cnt}"
                )

        # 2. Object types
        found_types = set(pm4py.ocel_get_object_types(ocel))
        metrics["object_types"] = list(found_types)

        for ot in self._required_object_types:
            if ot not in found_types:
                violations.append(
                    f"OCPQ_OBJECT_TYPE_VIOLATION: Required object type '{ot}' not found in log"
                )

        # 3. Balanced ratios
        for src_act, tgt_act, ratio in self._balanced_ratios:
            src_cnt = activity_counts.get(src_act, 0)
            tgt_cnt = activity_counts.get(tgt_act, 0)
            required_tgt = src_cnt * ratio
            if tgt_cnt < required_tgt:
                violations.append(
                    f"OCPQ_RATIO_VIOLATION: '{tgt_act}' ({tgt_cnt}) does not satisfy required ratio {ratio} for '{src_act}' ({src_cnt})"
                )

        # 4. Traversal path
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
                        f"OCPQ_TRAVERSAL_DISCONNECTED: No causal bridge found between '{t1}' and '{t2}'"
                    )

        # 5. Cardinality constraints
        if self._cardinality_checks:
            relations = ocel.relations
            objects_df = ocel.objects
            for src_type, tgt_type, min_c, max_c in self._cardinality_checks:
                src_objs = set(objects_df[objects_df["ocel:type"] == src_type]["ocel:oid"])
                tgt_objs = set(objects_df[objects_df["ocel:type"] == tgt_type]["ocel:oid"])
                for s_obj in src_objs:
                    s_evs = set(relations[relations["ocel:oid"] == s_obj]["ocel:eid"])
                    linked_targets = set(relations[(relations["ocel:eid"].isin(s_evs)) & (relations["ocel:oid"].isin(tgt_objs))]["ocel:oid"])
                    c_count = len(linked_targets)
                    if c_count < min_c or c_count > max_c:
                        violations.append(
                            f"OCPQ_CARDINALITY_VIOLATION: '{src_type}' object '{s_obj}' linked to {c_count} '{tgt_type}' objects, expected between {min_c} and {max_c}"
                        )

        # 6. Duration constraints
        if self._duration_checks:
            events_df = ocel.events.sort_values("ocel:timestamp")
            for act_start, act_end, max_sec in self._duration_checks:
                start_events = events_df[events_df["ocel:activity"] == act_start]
                end_events = events_df[events_df["ocel:activity"] == act_end]
                for _, s_row in start_events.iterrows():
                    s_time = s_row["ocel:timestamp"]
                    subsequent_ends = end_events[end_events["ocel:timestamp"] >= s_time]
                    if not subsequent_ends.empty:
                        e_time = subsequent_ends.iloc[0]["ocel:timestamp"]
                        duration_sec = (e_time - s_time).total_seconds()
                        if duration_sec > max_sec:
                            violations.append(
                                f"OCPQ_DURATION_VIOLATION: Latency from '{act_start}' to '{act_end}' was {duration_sec:.3f}s, exceeding limit of {max_sec:.3f}s"
                            )

        # 7. Fail-closed terminal transitions
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
                                f"OCPQ_FAIL_CLOSED_VIOLATION: Activity '{err_act}' followed by '{nxt_act}' instead of terminal state '{term_act}'"
                            )

        success = len(violations) == 0
        return OCPQResult(success=success, violations=violations, metrics=metrics)
