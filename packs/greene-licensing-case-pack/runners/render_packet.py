#!/usr/bin/env python3
"""Render the licensing proposal packet through the real ggen CLI.

Builds a throwaway ggen consumer in --consumer (must not exist or be empty)
and runs `ggen sync run` there. Consumer wiring:

  [packs]   greene-licensing-case-pack (+ extra_ontologies = this pack's
            ontology/greene-case.ttl, greene-deck.ttl, cs-pres-bridge.ttl,
            copied into the consumer because ggen loads only a pack's root
            ontology.ttl) and semantic-case-study-pack (its slide-facts and
            case-study-summary templates project the same case).
  ontology  consumer ontology.ttl = pptx-presentation-pack, evidence-standing-
            pack and decision-optionality-pack ontology.ttl. pptx and
            decision-optionality ship zero templates/*.tmpl, so ggen refuses
            them as [packs] entries (FM-PACK-005); evidence-standing's chain
            templates would project unrelated code; all three are imported
            at ontology level instead.

Outputs land under <consumer>/greene-licensing/ (letter.md, rights-table.md,
appendix.md, demo-spec.md) plus the case-study pack's slide-facts.md and
case-study-summary.md. Prints one JSON object with the ggen exit code and the
sha256 of every packet output. Exit 0 only when ggen exits 0 and all four
packet outputs exist. Authority NONE: this writes files in the consumer
directory only and sends nothing anywhere.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

PACK_ROOT = Path(__file__).resolve().parents[1]
PACKET_OUTPUTS = ("letter.md", "rights-table.md", "appendix.md", "demo-spec.md")
EXTRA = ("greene-case.ttl", "greene-deck.ttl", "cs-pres-bridge.ttl")
PACK_DEPENDENCIES = ("semantic-case-study-pack",)
ONTOLOGY_IMPORTS = ("pptx-presentation-pack", "evidence-standing-pack", "decision-optionality-pack")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def toml_string(value: str) -> str:
    return json.dumps(value)


def build_consumer(consumer: Path, packs_dir: Path) -> None:
    if consumer.exists() and any(consumer.iterdir()):
        raise SystemExit(f"REFUSED:CONSUMER_NOT_EMPTY:{consumer}")
    (consumer / "templates").mkdir(parents=True, exist_ok=True)
    (consumer / "extra").mkdir(exist_ok=True)
    for name in EXTRA:
        shutil.copyfile(PACK_ROOT / "ontology" / name, consumer / "extra" / name)
    parts = []
    for name in ONTOLOGY_IMPORTS:
        source = packs_dir / name / "ontology.ttl"
        if not source.is_file():
            raise SystemExit(f"BLOCKED:IMPORT_MISSING:{source}")
        parts.append(source.read_text(encoding="utf-8"))
    (consumer / "ontology.ttl").write_text("\n".join(parts), encoding="utf-8")
    extras = ", ".join(toml_string(f"extra/{name}") for name in EXTRA)
    lines = [
        "[project]",
        'name = "greene-licensing-render"',
        "",
        "[ontology]",
        'source = "ontology.ttl"',
        "",
        "[packs]",
        f'"greene-licensing-case-pack" = {{ path = {toml_string(PACK_ROOT.as_posix())}, extra_ontologies = [{extras}] }}',
    ]
    for name in PACK_DEPENDENCIES:
        path = packs_dir / name
        if not (path / "pack.toml").is_file():
            raise SystemExit(f"BLOCKED:DEPENDENCY_MISSING:{path}")
        lines.append(f'"{name}" = {{ path = {toml_string(path.as_posix())} }}')
    lines += ["", "[templates]", 'dir = "templates"', ""]
    (consumer / "ggen.toml").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--consumer", type=Path, required=True)
    parser.add_argument("--packs-dir", type=Path, default=PACK_ROOT.parent)
    parser.add_argument("--ggen", default="ggen")
    args = parser.parse_args()
    consumer = args.consumer.resolve()
    build_consumer(consumer, args.packs_dir.resolve())
    result = subprocess.run([args.ggen, "sync", "run"], cwd=consumer, text=True, capture_output=True)
    (consumer / "ggen-sync.log").write_text(result.stdout + result.stderr, encoding="utf-8")
    outputs = {}
    for name in PACKET_OUTPUTS:
        path = consumer / "greene-licensing" / name
        outputs[name] = sha256(path) if path.is_file() else None
    ok = result.returncode == 0 and all(outputs.values())
    print(json.dumps({"ggen_exit": result.returncode, "outputs": outputs,
                      "consumer": consumer.as_posix(), "standing": "RENDERED" if ok else "BLOCKED"},
                     indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
