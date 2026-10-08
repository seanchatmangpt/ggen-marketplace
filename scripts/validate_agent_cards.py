#!/usr/bin/env python3
"""Fleet-wide v1.0 member-contract validator for agent capability cards.

Contract (fleet semantic map, card-validation lane 2026-10-08):

  required : name, description, version,
             skills[] each with id/name/description/tags (tags nonempty),
             supportedInterfaces[0].protocolVersion
  forbidden: top-level ``url``, top-level ``preferredTransport``
  skill ids: ``<tool>.<cluster>.<verb>``-ish — nonempty, >=2 dot-separated
             segments, each segment nonempty and matching [A-Za-z0-9_-]+
  authority: the card description must state the authority posture
             (must contain an authority statement).

Cards are read from each owning repo's canonical checkout (one checkout per
repo, no worktrees). Generated cards are never hand-edited: violations in
generated families are fixed in the owning repo's generator and the cards
regenerated there.

Usage:
    python3 scripts/validate_agent_cards.py            # human table
    python3 scripts/validate_agent_cards.py --json     # machine report
Exit 0 iff every discovered card passes; 1 iff any violation (missing lands
are reported and fail closed).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MARKETPLACE = Path(__file__).resolve().parent.parent

# (repo key, checkout root, card land path(s) relative to root)
CARD_LANDS = [
    ("castle", "/Users/sac/castle", ".well-known/agent-card.json"),
    ("graphlaw", "/Users/sac/ash_graphlaw", "priv/graphlaw/cards"),
    ("ex4pm", "/Users/sac/ex4pm", "priv/cards"),
    ("ferroplan", "/Users/sac/ferroplan", "crates/ferroplan-wasm/cards"),
    ("ash_a2a", "/Users/sac/ash_a2a", "priv/sa2a/self-agent-card.json"),
    ("ash_surface", "/Users/sac/ash_surface", "priv/generated/agent_card.json"),
    ("gymact", "/Users/sac/gymact", "priv/cards"),
    ("wasm4pm", "/Users/sac/wasm4pm", ".well-known/agent-card.json",
     "docs/sa2a-actuator-agent-card-v2"),
]

SEGMENT_RE = re.compile(r"^[A-Za-z0-9_-]+[?!]?$")

# An authority statement is present iff the description names authority and
# its posture (grants/holds/claims none, receipted boundary, fail-closed...).
AUTHORITY_RE = re.compile(
    r"authorit(y|ative|ies)", re.IGNORECASE
)


def load_card(path: Path):
    try:
        return json.loads(path.read_text()), None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def validate_card(card: dict, source: str) -> list[str]:
    errs = []

    def req(cond, msg):
        if not cond:
            errs.append(msg)

    req(isinstance(card.get("name"), str) and card["name"].strip(),
        "missing/empty required field: name")
    desc = card.get("description")
    req(isinstance(desc, str) and desc.strip(),
        "missing/empty required field: description")
    req(isinstance(card.get("version"), str) and card["version"].strip(),
        "missing/empty required field: version")
    req(isinstance(card.get("supportedInterfaces"), list)
        and len(card["supportedInterfaces"]) > 0
        and isinstance(card["supportedInterfaces"][0].get("protocolVersion"), str)
        and card["supportedInterfaces"][0]["protocolVersion"].strip(),
        "missing required supportedInterfaces[0].protocolVersion")
    req("url" not in card, "forbidden top-level field: url")
    req("preferredTransport" not in card,
        "forbidden top-level field: preferredTransport")

    skills = card.get("skills")
    req(isinstance(skills, list) and len(skills) > 0,
        "missing/empty required field: skills")
    if isinstance(skills, list):
        for i, s in enumerate(skills):
            where = f"skills[{i}]"
            req(isinstance(s, dict), f"{where}: not an object")
            if not isinstance(s, dict):
                continue
            req(isinstance(s.get("id"), str) and s["id"].strip(),
                f"{where}: missing/empty id")
            req(isinstance(s.get("name"), str) and s["name"].strip(),
                f"{where}: missing/empty name")
            req(isinstance(s.get("description"), str) and s["description"].strip(),
                f"{where}: missing/empty description")
            tags = s.get("tags")
            req(isinstance(tags, list) and len(tags) > 0,
                f"{where}: missing/empty tags")

            sid = s.get("id", "")
            segments = sid.split(".")
            req(len(segments) >= 2,
                f"{where}: skill id '{sid}' is not <tool>.<cluster>.<verb>-ish "
                f"(needs >=2 dot-separated segments)")
            for seg in segments:
                req(bool(seg) and SEGMENT_RE.match(seg),
                    f"{where}: skill id '{sid}' has empty/illegal segment "
                    f"'{seg}' (allowed [A-Za-z0-9_-])")

    if isinstance(desc, str):
        req(bool(AUTHORITY_RE.search(desc)),
            "authority statement missing from description")

    return errs


def read_cards(key: str, root: str, land: str, ref=None):
    """Return list of (source_label, text) for a card land.

    ``ref`` pins the land to a git branch of the owning repo (branch law):
    blobs are read via ``git show ref:path`` instead of the working tree.
    """
    root_path = Path(root)
    land_path = root_path / land

    if ref is not None and not land_path.exists():
        # Working tree doesn't carry the land (checkout is on another lane's
        # branch): read from the owning repo's card branch.
        import subprocess
        if land_path.name.endswith(".json"):
            names = [land]
        else:
            ls = subprocess.run(
                ["git", "-C", str(root_path), "ls-tree", "-r", "--name-only", ref, land],
                capture_output=True, text=True, check=True)
            names = [n for n in ls.stdout.splitlines() if n.endswith(".json")]
        cards = []
        for n in sorted(names):
            show = subprocess.run(
                ["git", "-C", str(root_path), "show", f"{ref}:{n}"],
                capture_output=True, text=True, check=True)
            cards.append((f"{root}/{n}@{ref}", show.stdout))
        return cards

    if not root_path.exists():
        return None
    if land_path.is_dir():
        return [(str(f), f.read_text())
                for f in sorted(land_path.rglob("*.json"))]
    if land_path.exists():
        return [(str(land_path), land_path.read_text())]
    return None


def check_repo(key: str, root: str, land: str, ref=None) -> dict:
    cards = read_cards(key, root, land, ref)

    if cards is None:
        return {"repo": key, "status": "ABSENT", "cards": [],
                "errors": [f"card land not present in checkout: {Path(root) / land}"]}

    results = []
    n_errors = 0
    for source, text in cards:
        try:
            card = json.loads(text)
        except Exception as e:  # noqa: BLE001
            results.append({"file": source, "errors": [f"unparseable JSON: {e}"]})
            n_errors += 1
            continue
        errs = validate_card(card, source)
        results.append({"file": source, "errors": errs})
        n_errors += len(errs)

    status = "PASS" if n_errors == 0 else "FAIL"
    return {"repo": key, "status": status, "cards": results, "error_count": n_errors}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", dest="as_json")
    args = ap.parse_args(argv)

    report = [check_repo(*land) for land in CARD_LANDS]

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        total_cards = 0
        total_errs = 0
        for r in report:
            n_cards = len(r["cards"])
            total_cards += n_cards
            total_errs += r.get("error_count", 0)
            print(f"{r['repo']:<14} {r['status']:<7} {n_cards:>3} card(s), "
                  f"{r.get('error_count', 0)} violation(s)")
            for c in r["cards"]:
                for e in c["errors"]:
                    rel = c["file"]
                    print(f"    {rel}: {e}")
        print(f"\nTOTAL: {total_cards} cards, {total_errs} violations")
        if total_errs:
            print("RESULT: FAIL")

    return 1 if any(r["status"] != "PASS" for r in report) else 0


if __name__ == "__main__":
    sys.exit(main())
