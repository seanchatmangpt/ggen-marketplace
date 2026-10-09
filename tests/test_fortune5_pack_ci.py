#!/usr/bin/env python3
"""CI wiring for the fortune5-enterprise-architecture-pack test battery.

`packs/fortune5-enterprise-architecture-pack/tests/` holds the pack's real
suite -- 8 files (conformance vectors, DOD9 fences, provider templates,
qualification ladder, resource graph, SHACL shapes x3), 96 tests, ~5.5s --
and it is fully pack-local: every module resolves its fixtures from
`Path(__file__).resolve().parents[1]` (the pack dir), no sibling checkout
is consulted. So unlike the card fleet validator (tests/test_agent_cards_ci.py),
the whole battery is sound in GitHub CI, which checks out this repo alone.

What this wrapper does:

  1. runs the REAL battery, from this checkout alone, via a subprocess
     pinned to the pack directory as cwd (`python3 -m pytest tests/ -q`)
     and asserts exit 0 -- auto-wired by the repo's existing
     `pytest tests/` CI job;
  2. asserts the 96-test count from the pytest tail line, so a silently
     skipped or lost suite file fails here rather than passing vacuously.

Pack suite command (from the pack directory):

    cd packs/fortune5-enterprise-architecture-pack && python3 -m pytest tests/ -q
"""

from __future__ import annotations

import os
import subprocess
import sys
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PACK = os.path.join(REPO_ROOT, "packs", "fortune5-enterprise-architecture-pack")
EXPECTED_TESTS = 96


class TestFortune5PackCI(unittest.TestCase):
    def test_pack_suite_battery_passes(self):
        """The full pack battery (96 tests, 8 suites) exits 0, pack-local."""
        self.assertTrue(
            os.path.isdir(PACK), f"pack directory missing: {PACK}"
        )
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-q"],
            cwd=PACK,
            capture_output=True,
            text=True,
            timeout=120,
        )
        tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
        self.assertEqual(
            proc.returncode,
            0,
            f"pack suite failed (exit {proc.returncode}):\n{proc.stdout[-4000:]}\n{proc.stderr[-2000:]}",
        )
        # Count guard: a lost/skipped suite file must fail here, not pass vacuously.
        self.assertIn(
            f"{EXPECTED_TESTS} passed",
            tail[0],
            f"expected {EXPECTED_TESTS} passing tests, pytest tail: {tail[0]!r}",
        )


if __name__ == "__main__":
    unittest.main()
