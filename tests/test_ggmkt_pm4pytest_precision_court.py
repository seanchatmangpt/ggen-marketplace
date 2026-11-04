"""Precision court for pm4pytest ConformanceSpec (FIBO matrix: fitness AND precision = 1.0).

Verifies:
1. Valid trace: TBR fitness == 1.0 AND TBR precision == 1.0 under min_precision=1.0.
2. Unmodeled-side-effect trace: an extra event variant not in the net drops
   precision below 1.0 while fitness may stay 1.0 — the non-vacuity proof
   that the precision gate adds signal beyond the fitness gate.
3. Default min_precision=None leaves evaluation unchecked (no precision replay).

ZERO MOCKS. Real pm4py token-based replay over real pandas event logs.
"""

from __future__ import annotations

import pytest

pytest.importorskip("pm4pytest", reason="optional dependency not installed")
pytest.importorskip("pm4py", reason="optional dependency not installed")

import pandas as pd

from pm4pytest import ConformanceSpec

VALID_PATH = ["CLI_INVOKED", "COMMAND_DISPATCHED", "REGISTRY_LOADED", "OUTPUT_RENDERED"]
# Side-effect variant: an extra event injected mid-trace, not on the happy path.
SIDE_EFFECT_PATH = [
    "CLI_INVOKED",
    "COMMAND_DISPATCHED",
    "UNMODELED_SIDE_EFFECT",
    "REGISTRY_LOADED",
    "OUTPUT_RENDERED",
]


def _events(variants: list[list[str]]) -> list[dict]:
    rows = []
    for case_idx, path in enumerate(variants):
        for step_idx, act in enumerate(path):
            rows.append(
                {
                    "case:concept:name": f"case_{case_idx}",
                    "concept:name": act,
                    "time:timestamp": pd.Timestamp(f"2026-10-23 10:{step_idx:02d}:00"),
                }
            )
    return rows


class TestPrecisionCourt:
    """Fitness=1.0 alone is necessary but not sufficient; precision closes the gap."""

    def test_valid_trace_fitness_and_precision_1(self) -> None:
        """A trace matching the modeled lifecycle scores 1.0 on both axes."""
        spec = ConformanceSpec.from_fsm(
            valid_paths=[VALID_PATH], min_fitness=1.0, min_precision=1.0
        )
        res = spec.evaluate(_events([VALID_PATH]))
        assert res.fitness == 1.0
        assert res.precision == 1.0
        assert res.success is True
        assert res.violations == []

    def test_unmodeled_side_effect_drops_precision_not_fitness(self) -> None:
        """Net permitting an unmodeled side-effect branch: precision < 1.0 while fitness stays 1.0.

        pm4py precision measures the net against the log: a net that permits an
        extra event variant (side-effect branch after the happy path) is imprecise
        for a log that stays on the happy path, yet every observed trace replays
        perfectly — so the fitness gate alone would admit it.
        """
        spec = ConformanceSpec.from_fsm(
            valid_paths=[VALID_PATH, SIDE_EFFECT_PATH],
            min_fitness=1.0,
            min_precision=1.0,
        )
        res = spec.evaluate(_events([VALID_PATH]))
        assert res.fitness == 1.0, "fitness gate alone would admit this log"
        assert res.precision < 1.0
        assert res.success is False
        assert any(v.startswith("PETRI_NET_PRECISION_VIOLATION") for v in res.violations)

    def test_min_precision_none_unchecked(self) -> None:
        """Default min_precision=None skips the precision gate entirely."""
        spec = ConformanceSpec.from_fsm(valid_paths=[VALID_PATH])
        res = spec.evaluate(_events([VALID_PATH, VALID_PATH + ["UNMODELED_SIDE_EFFECT"]]))
        assert res.fitness == 1.0
        assert res.success is True
        assert "tbr_precision" not in res.diagnostics

    def test_precision_violation_string_formats_minimum(self) -> None:
        """The violation string mirrors the fitness one and names the minimum."""
        spec = ConformanceSpec.from_fsm(
            valid_paths=[VALID_PATH, SIDE_EFFECT_PATH],
            min_fitness=1.0,
            min_precision=0.99,
        )
        res = spec.evaluate(_events([VALID_PATH]))
        violation = next(v for v in res.violations if "PRECISION" in v)
        assert "below minimum 0.9900" in violation
