#!/usr/bin/env python3
"""Re-runnable check for ggen-self-pack's examples/ and playground/ scaffolding.

Closes a real gap found in commit c7f3aa402: that commit added two
`[[generation.rules]]` entries to `packs/ggen-self-pack/ggen.toml`
(`pack-examples-readme`, `pack-playground-scratch`) and claimed a manual
`ggen sync run` verification, but the verification was done in an ephemeral
scratch directory outside the repo -- there was no committed fixture or
re-runnable check proving the two new rules actually render.

This script runs the REAL `ggen` binary (not a hand-written stand-in) against
a real copy of `packs/ggen-self-pack`, using the pack's own
`qualification/project/input.ttl` fixture, and asserts:

1. All six `generation.rules` outputs are written (not just the original
   four) -- this is exactly the failure mode this check exists to catch: the
   two new templates referenced by ggen.toml did not exist on disk at the
   time of the original commit, so a real `ggen sync run` wrote only 4 of 6
   files and silently succeeded (zero exit code) instead of failing loudly.
2. `examples/README.md` and `playground/SCRATCH.md` byte-for-byte match the
   committed fixture at `qualification/expected/packs/qualification-pack/`,
   which was itself produced by this same real command and reviewed in.

Usage:
    python3 scripts/check_self_pack_scaffolding.py

Exit code 0 = both new files render correctly; non-zero = regression.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import NoReturn

REPO_ROOT = Path(__file__).resolve().parent.parent
PACK_DIR = REPO_ROOT / "packs" / "ggen-self-pack"
EXPECTED_DIR = PACK_DIR / "qualification" / "expected" / "packs" / "qualification-pack"

REQUIRED_OUTPUTS = [
    "packs/qualification-pack/pack.toml",
    "packs/qualification-pack/ontology.ttl",
    "packs/qualification-pack/gates/010_required.rq",
    "packs/qualification-pack/README.md",
    "packs/qualification-pack/examples/README.md",
    "packs/qualification-pack/playground/SCRATCH.md",
]

NEW_SCAFFOLDING_FILES = [
    "packs/qualification-pack/examples/README.md",
    "packs/qualification-pack/playground/SCRATCH.md",
]


def fail(msg: str) -> NoReturn:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    ggen = shutil.which("ggen")
    if ggen is None:
        fail("no `ggen` binary on PATH -- cannot run the real generation pipeline")

    with tempfile.TemporaryDirectory(prefix="ggen-self-pack-scaffolding-") as tmp:
        tmp_path = Path(tmp)
        # Copy exactly what a consumer running `ggen sync run` against this
        # pack profile would have: manifest, ontology, queries, gates,
        # templates -- and the pack's own qualification input as `input.ttl`.
        for name in ("ggen.toml", "ontology.ttl", "pack.toml"):
            shutil.copy2(PACK_DIR / name, tmp_path / name)
        for sub in ("templates", "queries", "gates"):
            shutil.copytree(PACK_DIR / sub, tmp_path / sub)
        shutil.copy2(
            PACK_DIR / "qualification" / "project" / "input.ttl",
            tmp_path / "input.ttl",
        )

        proc = subprocess.run(
            [ggen, "sync", "run", "--format", "json"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            fail(f"ggen sync run exited {proc.returncode}\nstderr:\n{proc.stderr}")

        import json

        # The JSON payload is the last line of stdout (log lines precede it).
        json_line = None
        for line in proc.stdout.splitlines()[::-1]:
            line = line.strip()
            if line.startswith("{"):
                json_line = line
                break
        if json_line is None:
            fail(f"could not find JSON output in ggen stdout:\n{proc.stdout}")

        payload = json.loads(json_line)
        written = set(payload.get("written", []))

        missing = [p for p in REQUIRED_OUTPUTS if p not in written]
        if missing:
            fail(
                "ggen sync run did not write all six generation.rules outputs; "
                f"missing: {missing}. written={sorted(written)}"
            )

        for rel in NEW_SCAFFOLDING_FILES:
            actual = tmp_path / rel
            if not actual.exists():
                fail(f"expected rendered file missing on disk: {rel}")
            expected = EXPECTED_DIR / Path(rel).relative_to("packs/qualification-pack")
            if not expected.exists():
                fail(f"no committed fixture at {expected} to compare against")
            actual_text = actual.read_text()
            expected_text = expected.read_text()
            if actual_text != expected_text:
                fail(
                    f"{rel} does not match committed fixture {expected}\n"
                    f"--- expected ---\n{expected_text}\n--- actual ---\n{actual_text}"
                )

    print("OK: ggen-self-pack's examples/ and playground/ scaffolding rules "
          "render correctly and match the committed fixture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
