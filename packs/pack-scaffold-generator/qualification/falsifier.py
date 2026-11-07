#!/usr/bin/env python3
"""Executed falsifier for pack-scaffold-generator (lane C4).

Proves the generator manufactures a conforming pack:
  1. builds a consumer graph declaring a scratch pack under tmp/ (never packs/),
  2. runs the REAL `ggen sync run` twice and asserts byte-identical replay,
  3. asserts all 8 scaffold files render non-empty,
  4. parses the generated Turtle,
  5. proves the generated identity gate FLIPS (0 rows pass / >=1 row fail),
  6. runs the repo stem court over the generated pack.

Exit 0 = PASS; any failure exits non-zero with a typed refusal.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PACK = Path(__file__).resolve().parents[1]
SCRATCH = REPO / "tmp" / "c4-demo"

SPEC = """@prefix psg: <https://seanchatmangpt.github.io/packs/pack-scaffold-generator#> .

psg:scratch-pack a psg:PackScaffold ;
    psg:packName "scratch-pack" ;
    psg:packIri "https://seanchatmangpt.github.io/packs/scratch-pack#" ;
    psg:packProfile "semantic" ;
    psg:packDescription "Scratch scaffold order executed by qualification/falsifier.py; structure only, born UNVERIFIED." ;
    psg:capabilityUrn "urn:ggen:pack:scratch-pack" .
"""

GGEN_TOML = """[project]
name = "c4-demo"

[ontology]
source = "spec.ttl"

[packs]
"pack-scaffold-generator" = { path = "PACK_PATH" }

[templates]
dir = "templates"
"""

EXPECTED = [
    "generated/scratch-pack/pack.toml",
    "generated/scratch-pack/ontology.ttl",
    "generated/scratch-pack/README.md",
    "generated/scratch-pack/RECEIPT.md",
    "generated/scratch-pack/gate-court.toml",
    "generated/scratch-pack/gates/010_capability_identity.rq",
    "generated/scratch-pack/witnesses/pass/010_capability_identity.ttl",
    "generated/scratch-pack/witnesses/fail/010_capability_identity.ttl",
]


def refuse(code: str, detail: str) -> int:
    print(f"REFUSED:PACK_SCAFFOLD_FALSIFIER:{code}:{detail}", file=sys.stderr)
    return 2


def snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


def main() -> int:
    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)
    (SCRATCH / "spec.ttl").write_text(SPEC, encoding="utf-8")
    (SCRATCH / "templates").mkdir()
    (SCRATCH / "ggen.toml").write_text(GGEN_TOML.replace("PACK_PATH", PACK.as_posix()), encoding="utf-8")

    snapshots = []
    for pass_no in (1, 2):
        proc = subprocess.run(
            ["ggen", "sync", "run", "--skip-ea-admission"],
            cwd=SCRATCH, capture_output=True, text=True, timeout=300,
        )
        if proc.returncode != 0:
            return refuse("GGEN_SYNC_FAILED", f"pass={pass_no} exit={proc.returncode} stderr={proc.stderr[-400:]!r}")
        snapshots.append(snapshot(SCRATCH / "generated"))

    if snapshots[0] != snapshots[1]:
        return refuse("NONDETERMINISTIC_REPLAY", "pass1 != pass2")

    generated = SCRATCH / "generated" / "scratch-pack"
    for rel in EXPECTED:
        p = generated / Path(rel).relative_to("generated/scratch-pack")
        if not p.is_file() or p.stat().st_size == 0:
            return refuse("MISSING_OR_EMPTY_OUTPUT", rel)

    try:
        import rdflib
    except ImportError:
        return refuse("RDFLIB_REQUIRED", "pip install rdflib")

    import logging
    logging.getLogger("rdflib").setLevel("ERROR")
    gate_text = (generated / "gates" / "010_capability_identity.rq").read_text(encoding="utf-8")

    def rows(ttl_path: Path) -> int:
        graph = rdflib.Graph().parse(ttl_path, format="turtle")
        return len(list(graph.query(gate_text)))

    pass_rows = rows(generated / "witnesses" / "pass" / "010_capability_identity.ttl")
    fail_rows = rows(generated / "witnesses" / "fail" / "010_capability_identity.ttl")
    if pass_rows != 0 or fail_rows < 1:
        return refuse("GATE_DOES_NOT_FLIP", f"pass_rows={pass_rows} fail_rows={fail_rows}")

    receipt = (generated / "RECEIPT.md").read_text(encoding="utf-8")
    if "Standing: UNVERIFIED" not in receipt:
        return refuse("RECEIPT_STANDING_MISSING", "RECEIPT.md lacks Standing: UNVERIFIED")

    court = subprocess.run(
        [sys.executable, "scripts/check_gate_witness_courts.py", "--packs", "generated"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    if court.returncode != 0:
        return refuse("STEM_COURT_REFUSED", court.stderr[-400:])

    print(json.dumps({
        "standing": "PASS",
        "pack": PACK.name,
        "scratch_pack": generated.as_posix(),
        "files": len(EXPECTED),
        "gate_flip": {"pass_rows": pass_rows, "fail_rows": fail_rows},
        "deterministic_replay": True,
        "stem_court": "ALIVE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
