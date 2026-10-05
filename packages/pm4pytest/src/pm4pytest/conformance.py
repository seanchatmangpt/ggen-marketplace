"""pm4pytest.conformance

Formal PM4Py Process Conformance Engine:
- Token-Based Replay (TBR) Fitness
- Optimal State Alignments
- Finite State Machine Transition Invariants
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet


@dataclass
class ConformanceResult:
    """Evaluation result for Petri net or FSM conformance."""
    success: bool
    fitness: float
    violations: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)


class ConformanceSpec:
    """Declarative specification for Petri net or FSM conformance."""

    def __init__(
        self,
        petri_net: Optional[PetriNet] = None,
        initial_marking: Optional[Marking] = None,
        final_marking: Optional[Marking] = None,
        min_fitness: float = 1.0,
        allowed_transitions: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self.net = petri_net
        self.im = initial_marking
        self.fm = final_marking
        self.min_fitness = min_fitness
        self.allowed_transitions = allowed_transitions or {}

    @classmethod
    def from_fsm(cls, valid_paths: List[List[str]], min_fitness: float = 1.0) -> ConformanceSpec:
        """Automatically construct a Petri net from valid trace paths."""
        df_rows = []
        for idx, path in enumerate(valid_paths):
            for step_idx, act in enumerate(path):
                df_rows.append({
                    "case:concept:name": f"case_{idx}",
                    "concept:name": act,
                    "time:timestamp": f"2026-10-04 10:0{step_idx}:00",
                })
        df = pd.DataFrame(df_rows)
        df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

        net, im, fm = pm4py.discover_petri_net_inductive(df)
        return cls(petri_net=net, initial_marking=im, final_marking=fm, min_fitness=min_fitness)

    def evaluate(self, events: List[Dict[str, Any]]) -> ConformanceResult:
        """Evaluate a test's sequential trace against the conformance model."""
        if not events:
            return ConformanceResult(success=False, fitness=0.0, violations=["CONFORMANCE_ERROR: Empty event trace."])

        # Build pandas event log
        df = pd.DataFrame(events)
        if "case:concept:name" not in df.columns:
            df["case:concept:name"] = "test_execution_case"
        if "concept:name" not in df.columns and "type" in df.columns:
            df["concept:name"] = df["type"]
        if "time:timestamp" not in df.columns and "time" in df.columns:
            df["time:timestamp"] = pd.to_datetime(df["time"])

        violations: List[str] = []
        diagnostics: Dict[str, Any] = {}
        actual_fitness = 1.0

        # 1. Petri net token-based replay fitness
        if self.net and self.im and self.fm:
            tbr = pm4py.fitness_token_based_replay(df, self.net, self.im, self.fm)
            actual_fitness = float(tbr.get("log_fitness", 0.0))
            diagnostics["tbr_fitness"] = tbr

            if actual_fitness < self.min_fitness:
                # Compute alignments for diagnostic error reporting
                alignments = pm4py.conformance_diagnostics_alignments(df, self.net, self.im, self.fm)
                diagnostics["alignments"] = alignments
                violations.append(
                    f"PETRI_NET_FITNESS_VIOLATION: Log fitness {actual_fitness:.4f} is below minimum {self.min_fitness:.4f}."
                )

        # 2. Strict transition checks
        if self.allowed_transitions:
            activities = df["concept:name"].tolist()
            for i in range(len(activities) - 1):
                src = activities[i]
                nxt = activities[i + 1]
                allowed = self.allowed_transitions.get(src, [])
                if nxt not in allowed:
                    violations.append(
                        f"FSM_INVALID_TRANSITION: Transition '{src}' -> '{nxt}' is unauthorized. Allowed next: {allowed}"
                    )

        success = len(violations) == 0
        return ConformanceResult(success=success, fitness=actual_fitness, violations=violations, diagnostics=diagnostics)
