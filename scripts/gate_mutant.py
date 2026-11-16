#!/usr/bin/env python3
"""Gate-mutant court: prove a pack's .rq gate can flip.

For each requested pack and gate: copy the pack to a temp dir, run the gate
(`ggen sync run --dry-run`, gates list narrowed to that one gate) as BASELINE
(must exit 0), drop an ontology triple the gate's text names, run again
(MUTANT, must exit non-zero), restore the ontology byte-exact and verify
sha256 against the original (fail-closed).

Verdicts per gate: PASS (flipped), FAIL (could not flip, or restore mismatch),
SKIP (loud, with reason: baseline red, no candidate triple, rdflib/ggen absent).
Exit 1 on any FAIL, or on --strict with any SKIP. The self-check (always run
first, or alone with --self-check) corrupts a restore on a real temp copy and
requires the restore check to detect it.

Usage:
  gate_mutant.py --pack packs/aaif-profile-tailoring-pack [--pack ...] [--gate NAME]
  gate_mutant.py --self-check
Env: GGEN_BIN overrides the ggen binary.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

TIMEOUT = 300
PRED_RE = re.compile(r"(?<![\w?$<])([A-Za-z][\w-]*):([a-z][\w-]*)\b")
PREFIX_RE = re.compile(r"^\s*PREFIX\s+([A-Za-z][\w-]*)?:\s*<([^>]*)>", re.I | re.M)


class Refusal(Exception):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore_checked(original_bytes: bytes, target: Path, expected_sha: str) -> None:
    """Write original bytes back, then verify sha256; raise on mismatch."""
    target.write_bytes(original_bytes)
    got = sha256(target)
    if got != expected_sha:
        raise Refusal(f"RESTORE MISMATCH {target}: expected {expected_sha} got {got}")


def run_gate(ggen: str, pack: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [ggen, "sync", "run", "--dry-run"],
        cwd=pack, capture_output=True, text=True, timeout=TIMEOUT, check=False,
    )


def narrow_gates(pack: Path, gate_rel: str) -> None:
    cfg = pack / "ggen.toml"
    text = cfg.read_text(encoding="utf-8")
    new, n = re.subn(r"(?ms)^gates\s*=\s*\[.*?\]", f'gates = ["{gate_rel}"]', text, count=1)
    if n != 1:
        raise Refusal("ggen.toml has no `gates = [...]` array to narrow")
    cfg.write_text(new, encoding="utf-8")


def gate_predicates(gate: Path) -> list[str]:
    text = gate.read_text(encoding="utf-8")
    prefixes = {p or "": u for p, u in PREFIX_RE.findall(text)}
    out: list[str] = []
    for pfx, local in PRED_RE.findall(text):
        if pfx in prefixes:
            iri = prefixes[pfx] + local
            if iri not in out:
                out.append(iri)
    return out


def mutants(ontology: Path, gate: Path):
    """Yield (label, mutated_turtle_bytes): per predicate, drop one triple, then all."""
    try:
        import rdflib  # type: ignore
    except ImportError as e:
        raise Refusal("rdflib not installed") from e
    g = rdflib.Graph()
    g.parse(ontology, format="turtle")
    for iri in gate_predicates(gate):
        triples = sorted(g.triples((None, rdflib.URIRef(iri), None)), key=lambda t: tuple(map(str, t)))
        if not triples:
            continue
        one = rdflib.Graph()
        for p, u in g.namespaces():
            one.bind(p, u)
        for t in g:
            if t != triples[0]:
                one.add(t)
        yield f"drop-one {iri}", one.serialize(format="turtle").encode()
        if len(triples) > 1:
            allg = rdflib.Graph()
            for p, u in g.namespaces():
                allg.bind(p, u)
            for t in g:
                if t[1] != rdflib.URIRef(iri):
                    allg.add(t)
            yield f"drop-all {iri}", allg.serialize(format="turtle").encode()


def court_gate(ggen: str, pack_src: Path, gate: Path) -> tuple[str, str]:
    gate_rel = gate.relative_to(pack_src).as_posix()
    cfg = tomllib.loads((pack_src / "ggen.toml").read_text(encoding="utf-8"))
    onto_rel = cfg.get("ontology", {}).get("source")
    if not onto_rel:
        return "SKIP", "no [ontology] source in ggen.toml"
    with tempfile.TemporaryDirectory(prefix="gate-mutant-") as tmp:
        pack = Path(tmp) / pack_src.name
        shutil.copytree(pack_src, pack)
        narrow_gates(pack, gate_rel)
        onto = pack / onto_rel
        original = onto.read_bytes()
        base_sha = hashlib.sha256(original).hexdigest()
        if base_sha != sha256(pack_src / onto_rel):
            return "FAIL", "temp copy differs from source before mutation"
        base = run_gate(ggen, pack)
        if base.returncode != 0:
            return "SKIP", f"baseline red (exit {base.returncode}); gate cannot be judged"
        try:
            cands = list(mutants(onto, gate))
        except Refusal as e:
            return "SKIP", str(e)
        if not cands:
            return "SKIP", "no ontology triple matches a predicate named in the gate"
        tried: list[str] = []
        flipped = None
        try:
            for label, data in cands:
                onto.write_bytes(data)
                r = run_gate(ggen, pack)
                tried.append(f"{label}->exit {r.returncode}")
                if r.returncode != 0:
                    flipped = label
                    break
        finally:
            restore_checked(original, onto, base_sha)  # raises Refusal -> FAIL
        if flipped is None:
            return "FAIL", "gate cannot flip: " + "; ".join(tried)
        after = run_gate(ggen, pack)
        if after.returncode != 0:
            return "FAIL", f"AFTER-restore run still red (exit {after.returncode})"
        return "PASS", f"flipped by {flipped}; restore sha256 {base_sha[:12]} byte-exact"


def self_check() -> bool:
    """Corrupt a restore on a real temp copy; the restore check must refuse."""
    with tempfile.TemporaryDirectory(prefix="gate-mutant-self-") as tmp:
        f = Path(tmp) / "ontology.ttl"
        original = b"@prefix ex: <http://e/> .\nex:a ex:p ex:b .\n"
        f.write_bytes(original)
        sha = hashlib.sha256(original).hexdigest()
        f.write_bytes(b"mutated\n")
        restore_checked(original, f, sha)  # honest restore must pass
        try:
            restore_checked(original + b"\n# corrupt", f, sha)
        except Refusal:
            return True
        print("[SELF-CHECK FAIL] corrupted restore was not detected (VACUOUS)", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pack", action="append", type=Path, default=[])
    ap.add_argument("--gate", help="gate file stem or name to restrict to")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--strict", action="store_true", help="SKIP counts as failure")
    ap.add_argument("--ggen", default=os.environ.get("GGEN_BIN") or shutil.which("ggen"))
    args = ap.parse_args()

    if not self_check():
        return 1
    print("[SELF-CHECK PASS] corrupted restore detected")
    if args.self_check and not args.pack:
        return 0
    if not args.ggen:
        print("[SKIP] ggen binary not found (set GGEN_BIN); no gate judged", file=sys.stderr)
        return 1 if args.strict else 0

    counts = {"PASS": 0, "FAIL": 0, "SKIP": 0}
    for pack in args.pack:
        pack = pack.resolve()
        gates = sorted(
            p for p in (pack / "gates").glob("*") if p.suffix in {".rq", ".sparql"}
            and (not args.gate or args.gate in (p.name, p.stem))
        )
        if not gates:
            print(f"[SKIP] {pack.name}: no .rq gates selected")
            counts["SKIP"] += 1
            continue
        for gate in gates:
            try:
                verdict, why = court_gate(args.ggen, pack, gate)
            except Refusal as e:
                verdict, why = "FAIL", str(e)
            except subprocess.TimeoutExpired:
                verdict, why = "FAIL", "ggen timed out"
            counts[verdict] += 1
            print(f"[{verdict}] {pack.name}/{gate.name}: {why}")
    print(f"SUMMARY pass={counts['PASS']} fail={counts['FAIL']} skip={counts['SKIP']}")
    return 1 if counts["FAIL"] or (args.strict and counts["SKIP"]) else 0


if __name__ == "__main__":
    sys.exit(main())
