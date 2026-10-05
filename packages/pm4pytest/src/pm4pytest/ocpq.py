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

        success = len(violations) == 0
        return OCPQResult(success=success, violations=violations, metrics=metrics)
