#!/usr/bin/env python3
"""Execute the first-pack tutorial for real in a temp directory.

Steps (each exits nonzero on failure):
  1. tutorial code blocks == examples/hello-pack files (no doc/example drift)
  2. a scratch marketplace root admits the pack:  marketplace.py validate + check hello-pack
  3. a consumer references the pack by path and runs real `ggen sync run`
  4. output bytes equal the RDF literal; a second run converges (fixed point)

Requires `ggen` on PATH (scripts/install-ggen.sh installs the pinned one).
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "hello-pack"
TUTORIAL = ROOT / "docs" / "tutorials" / "first-pack.md"
EXPECTED = "Hello from ggen."

# (tutorial code-fence info string label, example file relative to EXAMPLE)
TUTORIAL_FILES = {
    "pack.toml": "pack/pack.toml",
    "ontology.ttl": "pack/ontology.ttl",
    "templates/greeting.txt.tmpl": "pack/templates/greeting.txt.tmpl",
    "consumer/ggen.toml": "consumer/ggen.toml",
    "consumer/ontology.ttl": "consumer/ontology.ttl",
}


def fail(message: str) -> "None":
    print(f"QUICKSTART_FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str], cwd: Path, step: str) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300)
    print(f"[{step}] {' '.join(cmd)} -> exit {result.returncode}")
    if result.returncode != 0:
        fail(f"{step}: exit {result.returncode}\n{result.stdout[-800:]}\n{result.stderr[-800:]}")
    return result


def tutorial_blocks() -> dict[str, str]:
    """Map `<!-- file: NAME -->` annotated fences in the tutorial to their bodies."""
    text = TUTORIAL.read_text(encoding="utf-8")
    pattern = re.compile(r"<!-- file: (?P<name>[^ ]+) -->\n```[a-z]*\n(?P<body>.*?)```", re.S)
    return {m["name"]: m["body"] for m in pattern.finditer(text)}


def check_tutorial_matches_example() -> None:
    blocks = tutorial_blocks()
    for name, relative in TUTORIAL_FILES.items():
        if name not in blocks:
            fail(f"tutorial has no `<!-- file: {name} -->` block")
        actual = (EXAMPLE / relative).read_text(encoding="utf-8")
        if blocks[name] != actual:
            fail(f"tutorial block {name} differs from examples/hello-pack/{relative}")
    print(f"[tutorial] {len(TUTORIAL_FILES)} blocks match examples/hello-pack")


def scratch_marketplace(work: Path) -> Path:
    """Minimal marketplace root containing only the scripts, config, docs and hello-pack."""
    root = work / "marketplace"
    shutil.copytree(ROOT / "scripts", root / "scripts", ignore=shutil.ignore_patterns("__pycache__"))
    for name in ("marketplace.toml", "marketplace.active.toml"):
        if (ROOT / name).is_file():
            shutil.copy2(ROOT / name, root / name)
    sys.path.insert(0, str(ROOT / "scripts"))
    import marketplace  # noqa: PLC0415

    for relative in marketplace.REQUIRED_DOCS:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    shutil.copytree(EXAMPLE / "pack", root / "packs" / "hello-pack")
    return root


def main() -> int:
    if not shutil.which("ggen"):
        fail("ggen not on PATH; run scripts/install-ggen.sh (docs/how-to/install-ggen.md)")
    check_tutorial_matches_example()
    with tempfile.TemporaryDirectory(prefix="ggen-quickstart-") as tmp:
        work = Path(tmp)
        run(["ggen", "--version"], work, "ggen-identity")

        root = scratch_marketplace(work)
        run([sys.executable, "scripts/marketplace.py", "validate"], root, "validate")
        run([sys.executable, "scripts/marketplace.py", "check", "hello-pack"], root, "check")

        consumer = work / "consumer"
        shutil.copytree(EXAMPLE / "consumer", consumer)
        (work / "pack").mkdir()
        shutil.copytree(EXAMPLE / "pack", work / "pack", dirs_exist_ok=True)
        run(["ggen", "sync", "run"], consumer, "manufacture")
        out = consumer / "output" / "greeting.txt"
        if not out.is_file():
            fail("output/greeting.txt was not produced")
        first = out.read_bytes()
        if first.decode("utf-8").strip() != EXPECTED:
            fail(f"greeting.txt is {first!r}, expected {EXPECTED!r}")
        run(["ggen", "sync", "run"], consumer, "replay")
        if out.read_bytes() != first:
            fail("replay changed output bytes (no fixed point)")
    print("QUICKSTART_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
