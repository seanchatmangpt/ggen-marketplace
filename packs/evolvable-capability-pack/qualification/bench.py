#!/usr/bin/env python3
"""Deterministic admission benchmark for evolvable-capability-pack.

Builds a conforming evolution history of N capability generations (each
generation is a released champion followed by a promoted candidate backed by
paired evidence, all frozen into one execution closure), then times the full
gate set (every ``gates/*.rq``) over it with the real rdflib SPARQL engine.

The synthetic graph is a pure function of N, so the admitted/refused verdict
is reproducible; only wall-clock varies by machine. Correctness is asserted
on every run (zero rows on the conforming graph; a single injected defect is
refused), so a benchmark cannot report a fast time for a vacuous gate set.

Usage:
    python3 bench.py [--sizes 50,200,800] [--repeats 3] [--receipt out.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import verify  # noqa: E402  (sibling module, real collaborator)

PREFIXES = """@prefix ecap: <https://seanchatmangpt.github.io/packs/evolvable-capability#> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
"""

# Regression bounds, applied to the largest measured size only (small sizes
# are dominated by fixed SPARQL parse cost). Measured 2026-09-25 on Apple
# silicon / CPython 3.14 / rdflib 7.6.0: ~0.0057 s per generation at N=800
# (see qualification/bench-receipt.json). The absolute bound carries ~9x
# headroom for slower runners; the scaling bound refuses super-linear growth:
# time(largest)/time(next) may not exceed SCALING_SLACK x the size ratio
# (linear = 1.0x, quadratic = size-ratio x), so a gate going quadratic trips
# it even on a fast machine.
MAX_SECONDS_PER_GENERATION = 0.050
SCALING_SLACK = 2.0


def digest(label: str) -> str:
    return "sha256:" + hashlib.sha256(label.encode("utf-8")).hexdigest()


def history(generations: int) -> str:
    """Turtle for a conforming N-generation evolution history."""
    lines = [PREFIXES]
    members: list[str] = []
    for index in range(generations):
        champion = f"<urn:bench:cap:{index}:champion>"
        candidate = f"<urn:bench:cap:{index}:candidate>"
        for node, version in ((champion, 2 * index + 1), (candidate, 2 * index + 2)):
            lines.append(
                f"{node} a ecap:Capability ; ecap:lifecycleState ecap:Released ;"
                f' dcterms:hasVersion "{version}" ;'
                f' ecap:implementationDigest "{digest(node)}" ;'
                f" ecap:admissionEvidence {node[:-1]}:admission> ;"
                f" ecap:releaseEvidence {node[:-1]}:release> ."
            )
            lines.append(f"{node[:-1]}:admission> a prov:Entity .")
            lines.append(f"{node[:-1]}:release> a prov:Entity .")
            members.append(node)
        pair = f"<urn:bench:pair:{index}>"
        lines.append(
            f"{pair} a ecap:PairedEvidence ; ecap:champion {champion} ; ecap:candidate {candidate} ;"
            f' ecap:cohortDigest "{digest(pair + ":cohort")}" ;'
            f' ecap:evidenceDigest "{digest(pair + ":evidence")}" .'
        )
        lines.append(
            f"<urn:bench:promotion:{index}> a ecap:Promotion ;"
            f" ecap:pairedEvidence {pair} ; ecap:promotes {candidate} ."
        )
    lines.append(
        f'<urn:bench:closure> a ecap:ExecutionClosure ; ecap:closureDigest "{digest("closure")}" ;'
        f" ecap:closureMember {' , '.join(members)} ."
    )
    return "\n".join(lines) + "\n"


def defect() -> str:
    """One injected defect: a candidate smuggled into the closure."""
    return (
        PREFIXES
        + '<urn:bench:smuggled> a ecap:Capability ; ecap:lifecycleState ecap:Candidate ;'
        + ' dcterms:hasVersion "0" ;'
        + f' ecap:implementationDigest "{digest("smuggled")}" .\n'
        + "<urn:bench:closure> ecap:closureMember <urn:bench:smuggled> .\n"
    )


def measure(generations: int, repeats: int) -> dict[str, object]:
    text = history(generations)
    graph = verify.load_graph(text)
    samples: list[float] = []
    per_gate: dict[str, list[float]] = {gate.stem: [] for gate in verify.gates()}
    for _ in range(repeats):
        total = 0.0
        for gate in verify.gates():
            start = time.perf_counter()
            found = verify.rows(gate, graph)
            elapsed = time.perf_counter() - start
            per_gate[gate.stem].append(elapsed)
            total += elapsed
            if found:
                raise AssertionError(f"conforming history refused at N={generations}: {gate.stem}")
        samples.append(total)
    poisoned = verify.refusing_gates(verify.load_graph(text, defect()))
    if set(poisoned) != {"030_closure_released_only"}:
        raise AssertionError(f"injected defect not isolated at N={generations}: {poisoned}")
    median = statistics.median(samples)
    return {
        "generations": generations,
        "triples": len(graph),
        "gates": len(verify.gates()),
        "repeats": repeats,
        "median_seconds": round(median, 6),
        "min_seconds": round(min(samples), 6),
        "seconds_per_generation": round(median / generations, 6),
        "input_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "gate_median_seconds": {
            stem: round(statistics.median(values), 6) for stem, values in sorted(per_gate.items())
        },
    }


def run(sizes: list[int], repeats: int) -> dict[str, object]:
    results = [measure(size, repeats) for size in sorted(sizes)]
    largest = results[-1]
    per_generation_ok = float(largest["seconds_per_generation"]) <= MAX_SECONDS_PER_GENERATION
    scaling: dict[str, object] = {"checked": False}
    scaling_ok = True
    if len(results) >= 2:
        previous = results[-2]
        size_ratio = int(largest["generations"]) / int(previous["generations"])
        time_ratio = float(largest["median_seconds"]) / max(float(previous["median_seconds"]), 1e-9)
        scaling_ok = time_ratio <= SCALING_SLACK * size_ratio
        scaling = {
            "checked": True,
            "size_ratio": round(size_ratio, 3),
            "time_ratio": round(time_ratio, 3),
            "max_time_ratio": round(SCALING_SLACK * size_ratio, 3),
        }
    return {
        "schema": "ggen.evolvable-capability-pack.bench/1",
        "engine": {"python": platform.python_version(), "rdflib": __import__("rdflib").__version__},
        "machine": {"system": platform.system(), "machine": platform.machine()},
        "bound_seconds_per_generation": MAX_SECONDS_PER_GENERATION,
        "results": results,
        "scaling": scaling,
        "standing": "ALIVE" if per_generation_ok and scaling_ok else "REFUSED",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sizes", default="50,200,800")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    report = run([int(item) for item in args.sizes.split(",")], args.repeats)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.receipt:
        args.receipt.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["standing"] == "ALIVE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
