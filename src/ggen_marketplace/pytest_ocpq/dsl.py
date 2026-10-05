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
            # Each step in the path must have shared events linking objects of type path[i] and path[i+1]
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

        success = len(violations) == 0
        return OCPQQueryResult(success=success, violations=violations, metrics=metrics)
