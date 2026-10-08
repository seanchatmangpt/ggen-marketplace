#!/usr/bin/env python3
"""CI wiring for the fleet card v1.0 contract validator.

`scripts/validate_agent_cards.py` validates cards from each owning repo's
canonical checkout (CARD_LANDS: castle, ash_graphlaw, ex4pm, ferroplan,
ash_a2a, ash_surface, gymact, wasm4pm -- absolute /Users/sac/<repo> roots).
GitHub CI checks out ONLY this repo, so the full fleet run is unsound there:
every sibling land would be ABSENT, and ABSENT fails closed, so wiring the
fleet command directly into a workflow would guarantee a red CI. The fleet
run stays a local command (documented below and in
docs/reference/FLEET-SEMANTIC-MAP.md).

What CI can and does verify, from this checkout alone:

  1. the validator's contract logic itself, against a small in-repo fixture
     corpus (a fully-compliant card plus one card per violation class --
     required fields, forbidden fields, skill-id shape, authority statement),
     so contract drift in validate_agent_cards.py fails the suite;
  2. the fleet run's fail-closed behavior is pinned by assertion on the real
     CARD_LANDS table (every land is an absolute sibling path, so a checkout
     that silently stopped shipping the validator cannot pass here);
  3. the fleet command, when sibling checkouts ARE present (local runs),
     exits 0 across all 8 repos.

Fleet run command (local, one canonical checkout per repo, no worktrees):

    python3 scripts/validate_agent_cards.py            # human table
    python3 scripts/validate_agent_cards.py --json     # machine report

Exit 0 iff every discovered card passes; ABSENT lands fail closed.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_agent_cards.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_agent_cards", VALIDATOR)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


COMPLIANT_CARD = {
    "name": "fixture-card",
    "description": "Fixture actuator; authority: holds none, grants none, "
                   "receipted boundary, fails closed.",
    "version": "1.0.0",
    "supportedInterfaces": [{"protocolVersion": "1.0"}],
    "skills": [{
        "id": "fixture.cluster.verb",
        "name": "Fixture skill",
        "description": "Does a fixture thing.",
        "tags": ["fixture"],
    }],
}


class TestCardContract(unittest.TestCase):
    """Contract logic against the fixture corpus (runs anywhere)."""

    @classmethod
    def setUpClass(cls):
        cls.v = _load_validator()

    def test_compliant_card_passes(self):
        self.assertEqual(self.v.validate_card(dict(COMPLIANT_CARD), "fixture"), [])

    def test_missing_required_fields(self):
        card = {k: v for k, v in COMPLIANT_CARD.items() if k != "version"}
        errs = self.v.validate_card(card, "fixture")
        self.assertTrue(any("version" in e for e in errs), errs)

    def test_forbidden_top_level_fields(self):
        card = dict(COMPLIANT_CARD, url="https://x", preferredTransport="grpc")
        errs = self.v.validate_card(card, "fixture")
        joined = "; ".join(errs)
        self.assertIn("url", joined)
        self.assertIn("preferredTransport", joined)

    def test_empty_skills_rejected(self):
        card = dict(COMPLIANT_CARD, skills=[])
        errs = self.v.validate_card(card, "fixture")
        self.assertTrue(any("skills" in e for e in errs), errs)

    def test_skill_missing_tags(self):
        card = dict(COMPLIANT_CARD)
        del card["skills"][0]["tags"]
        errs = self.v.validate_card(card, "fixture")
        self.assertTrue(any("tags" in e for e in errs), errs)

    def test_skill_id_needs_dot_segments(self):
        card = dict(COMPLIANT_CARD)
        card["skills"][0]["id"] = "nodots"
        errs = self.v.validate_card(card, "fixture")
        self.assertTrue(any("dot-separated" in e for e in errs), errs)

    def test_skill_id_illegal_segment(self):
        card = dict(COMPLIANT_CARD)
        card["skills"][0]["id"] = "fixture.bad seg!.verb"
        errs = self.v.validate_card(card, "fixture")
        self.assertTrue(any("illegal segment" in e for e in errs), errs)

    def test_elixir_predicate_skill_id_allowed(self):
        card = dict(COMPLIANT_CARD)
        card["skills"][0]["id"] = "fixture.cluster.verb!"
        self.assertEqual(self.v.validate_card(card, "fixture"), [])

    def test_authority_statement_required(self):
        card = dict(COMPLIANT_CARD)
        card["description"] = "Just does things; no posture declared."
        errs = self.v.validate_card(card, "fixture")
        self.assertTrue(any("authority" in e for e in errs), errs)


class TestFleetWiring(unittest.TestCase):
    """The fleet run itself: local-real, honestly skipped in CI."""

    @classmethod
    def setUpClass(cls):
        cls.v = _load_validator()

    def test_lands_are_sibling_checkouts(self):
        # Pins the fail-closed CI precondition: every land root is an absolute
        # path outside this repo, so GitHub CI (this checkout alone) cannot
        # satisfy the fleet run and wiring it directly would be permanently red.
        for land in self.v.CARD_LANDS:
            root = Path(land[1])
            self.assertTrue(root.is_absolute(), land)
            self.assertNotEqual(root, REPO_ROOT, land)

    def test_fleet_run_passes_when_checkouts_present(self):
        if not all(Path(land[1]).exists() for land in self.v.CARD_LANDS):
            self.skipTest(
                "sibling fleet checkouts not present "
                "(CI checks out this repo alone); fleet run is a local command"
            )
        proc = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(
            proc.returncode, 0,
            f"fleet card validation failed:\n{proc.stdout}\n{proc.stderr}",
        )


if __name__ == "__main__":
    unittest.main()
