#!/usr/bin/env python3
"""Qualify the exact public-ontology XaaS profile without inventing XaaS terms.

This verifier answers a deliberately narrow question before ggen construction:
which public terms required by the XaaS competency-question hypotheses are
actually present in the exact lock-pinned local corpus?

TERM_COVERAGE is not semantic equivalence.  CQ09/CQ19/CQ20 and the economic
authority questions are fenced explicitly even when adjacent public terms are
present: ODRL permission is not BRCE authority, PROV evidence is not a receipt,
and provenance is not deterministic replay.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tomllib
from typing import Iterable

from rdflib import Graph, URIRef


PROFILE_SCHEMA = "ggen.marketplace.xaas-public-profile-qualification/v1"

# Public vocabulary hypotheses only. These IRIs are competency probes, not
# XaaS ontology declarations and never assert equivalence between vocabularies.
CANDIDATES: dict[str, list[list[str]]] = {
    "CQ01": [["http://www.w3.org/ns/dcat#Resource", "https://w3id.org/function/ontology#Function"]],
    "CQ02": [
        ["https://w3id.org/function/ontology#Parameter"],
        ["https://w3id.org/function/ontology#Output"],
        ["https://w3id.org/function/ontology#expects"],
        ["https://w3id.org/function/ontology#returns"],
    ],
    "CQ03": [
        ["https://w3id.org/function/ontology#Mapping"],
        ["https://w3id.org/function/ontology#Implementation"],
        ["https://w3id.org/function/ontology#function"],
        ["https://w3id.org/function/ontology#implementation"],
    ],
    "CQ04": [
        ["https://w3id.org/function/ontology#Execution"],
        ["https://w3id.org/function/ontology#executes"],
        ["https://w3id.org/function/ontology#uses"],
    ],
    "CQ05": [],  # NML/INDL/OMN topology is not yet admitted into this profile.
    "CQ06": [],  # GeoSPARQL/provider-region semantics are not yet admitted.
    "CQ07": [
        ["http://www.w3.org/ns/org#Organization"],
        ["http://www.w3.org/ns/org#Role"],
        ["http://www.w3.org/ns/org#Membership"],
    ],
    "CQ08": [
        ["http://www.w3.org/ns/odrl/2/Permission"],
        ["http://www.w3.org/ns/odrl/2/Prohibition"],
        ["http://www.w3.org/ns/odrl/2/Duty"],
    ],
    "CQ09": [["http://www.w3.org/ns/odrl/2/Permission"], ["http://www.w3.org/ns/org#Role"]],
    "CQ10": [["http://www.w3.org/ns/sosa/Observation"]],
    "CQ11": [["http://qudt.org/schema/qudt/QuantityValue"], ["http://qudt.org/schema/qudt/Unit"]],
    "CQ12": [
        ["http://purl.org/net/p-plan#Plan"],
        ["http://purl.org/net/p-plan#Step"],
        ["http://www.w3.org/ns/prov#Activity"],
    ],
    "CQ13": [["http://spdx.org/rdf/terms#Package"], ["http://spdx.org/rdf/terms#File"]],
    "CQ14": [["http://qudt.org/schema/qudt/QuantityValue"], ["http://qudt.org/schema/qudt/Unit"]],
    "CQ15": [],  # DPV/UCO profile admission is unfinished.
    "CQ16": [],  # WoT Thing Description is not admitted.
    "CQ17": [["http://www.w3.org/ns/prov#used"], ["http://www.w3.org/ns/prov#wasGeneratedBy"]],
    "CQ18": [["http://www.w3.org/ns/prov#SoftwareAgent"], ["http://www.w3.org/ns/prov#wasAssociatedWith"]],
    "CQ19": [["http://www.w3.org/ns/prov#Entity"], ["http://www.w3.org/ns/prov#wasGeneratedBy"]],
    "CQ20": [["http://www.w3.org/ns/prov#wasDerivedFrom"]],
    "CQ21": [],  # Need/demand semantics not yet admitted.
    "CQ22": [],  # GoodRelations commerce vocabulary not yet admitted by lock.
    "CQ23": [["http://www.w3.org/ns/odrl/2/Duty"]],
    "CQ24": [],  # REA/FIBO accounting semantics not yet admitted by this profile.
    "CQ25": [],  # Tax/nexus/taxable-event semantics not yet admitted.
    "CQ26": [],  # UCO/AIRO risk vocabularies not yet admitted by this profile.
    "CQ27": [["http://www.w3.org/ns/org#Role"], ["http://www.w3.org/ns/odrl/2/Permission"]],
    "CQ28": [["http://qudt.org/schema/qudt/QuantityValue"], ["http://www.w3.org/ns/prov#Activity"]],
}

# Public vocabulary coverage is intentionally insufficient for these questions.
# Never crown adjacency as semantic equivalence.
SEMANTIC_FENCES = {
    "CQ09": "ODRL permission + ORG role do not prove authority to actuate an exact external subject.",
    "CQ14": "QUDT covers quantities/units but not commercial offer, billing and consumption semantics by itself.",
    "CQ19": "PROV entities/lineage are necessary evidence primitives but do not by themselves constitute a BRCE receipt.",
    "CQ20": "PROV derivation does not define deterministic replay identity or replay verification.",
    "CQ23": "ODRL Duty covers duties but is not a complete contract/consideration model.",
    "CQ27": "ORG roles and ODRL permissions do not prove legal/economic authority to bind, mutate or transfer.",
    "CQ28": "QUDT + PROV can represent measured economics over activities but do not define viability/unit-economics closure.",
}

FORCED_GAPS = {
    "CQ20",  # deterministic replay semantics remain a genuine unresolved gap
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def graph_has_term(graph: Graph, iri: str) -> bool:
    term = URIRef(iri)
    if (term, None, None) in graph:
        return True
    if (None, term, None) in graph:
        return True
    if (None, None, term) in graph:
        return True
    return False


def parse_lock(lock_path: Path) -> dict:
    with lock_path.open("rb") as handle:
        data = tomllib.load(handle)
    if "lock" not in data:
        raise ValueError(f"lock table missing: {lock_path}")
    return data["lock"]


def resolve_format(serialization: str, path: Path) -> str | None:
    normalized = serialization.strip().lower()
    if normalized in {"turtle", "ttl"}:
        return "turtle"
    if normalized in {"rdf/xml", "rdfxml", "xml"}:
        return "xml"
    if normalized in {"json-ld", "jsonld"}:
        return "json-ld"
    if path.suffix.lower() in {".ttl"}:
        return "turtle"
    if path.suffix.lower() in {".rdf", ".owl", ".xml"}:
        return "xml"
    return None


def qualify(repo_root: Path, profile_root: Path) -> dict:
    locks_dir = profile_root / "locks"
    lock_paths = sorted(locks_dir.glob("*.lock.toml"))
    if not lock_paths:
        raise ValueError(f"no ontology locks found in {locks_dir}")

    graph = Graph()
    sources = []
    failures = []

    for lock_path in lock_paths:
        lock = parse_lock(lock_path)
        local_path_raw = lock.get("local_path")
        if not local_path_raw:
            failures.append({"lock": str(lock_path.relative_to(repo_root)), "problem": "LOCAL_PATH_MISSING"})
            continue
        local_path = repo_root / str(local_path_raw)
        if not local_path.is_file():
            failures.append({
                "lock": str(lock_path.relative_to(repo_root)),
                "problem": "LOCKED_ARTIFACT_MISSING",
                "local_path": str(local_path_raw),
            })
            continue

        observed_digest = sha256(local_path)
        expected_digest = lock.get("sha256")
        digest_status = "UNPINNED"
        if expected_digest:
            digest_status = "MATCH" if observed_digest == expected_digest else "MISMATCH"
            if digest_status == "MISMATCH":
                failures.append({
                    "lock": str(lock_path.relative_to(repo_root)),
                    "problem": "DIGEST_MISMATCH",
                    "expected": expected_digest,
                    "observed": observed_digest,
                })
                continue

        serialization = str(lock.get("serialization", ""))
        rdf_format = resolve_format(serialization, local_path)
        try:
            graph.parse(local_path, format=rdf_format)
            parse_status = "ALIVE"
        except Exception as exc:  # rdflib emits parser-specific exceptions
            failures.append({
                "lock": str(lock_path.relative_to(repo_root)),
                "problem": "RDF_PARSE_FAILED",
                "detail": f"{type(exc).__name__}: {exc}",
            })
            parse_status = "FAILED"

        sources.append({
            "name": lock.get("name"),
            "canonical_iri": lock.get("canonical_iri"),
            "local_path": str(local_path_raw),
            "sha256": observed_digest,
            "digest_status": digest_status,
            "parse_status": parse_status,
            "publication_status": lock.get("publication_status"),
        })

    coverage = []
    for cq in sorted(CANDIDATES, key=lambda value: int(value[2:])):
        groups = CANDIDATES[cq]
        group_results = []
        for alternatives in groups:
            present = sorted(iri for iri in alternatives if graph_has_term(graph, iri))
            group_results.append({"alternatives": alternatives, "present": present, "satisfied": bool(present)})

        satisfied = sum(1 for group in group_results if group["satisfied"])
        if not groups or cq in FORCED_GAPS:
            term_status = "GAP"
        elif satisfied == len(groups):
            term_status = "TERM_COVERAGE"
        elif satisfied:
            term_status = "PARTIAL"
        else:
            term_status = "GAP"

        semantic_status = term_status
        if cq in SEMANTIC_FENCES and term_status == "TERM_COVERAGE":
            semantic_status = "PARTIAL"
        if cq in FORCED_GAPS:
            semantic_status = "GAP"

        coverage.append({
            "cq": cq,
            "term_status": term_status,
            "semantic_status": semantic_status,
            "groups": group_results,
            "fence": SEMANTIC_FENCES.get(cq),
        })

    summary = {
        "term_coverage": sum(1 for item in coverage if item["term_status"] == "TERM_COVERAGE"),
        "partial": sum(1 for item in coverage if item["semantic_status"] == "PARTIAL"),
        "gaps": sum(1 for item in coverage if item["semantic_status"] == "GAP"),
        "unchecked": 0,
    }

    return {
        "schema": PROFILE_SCHEMA,
        "standing": "BLOCKED" if failures else "PARTIAL_ALIVE",
        "scope": "public-ontology-term-availability-before-equivalence",
        "sources": sources,
        "source_failures": failures,
        "graph_triples": len(graph),
        "coverage": coverage,
        "summary": summary,
        "authority": "NO_EXECUTION_AUTHORITY_DERIVED_FROM_TERM_COVERAGE",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    profile_root = Path(__file__).resolve().parents[1]
    try:
        report = qualify(repo_root, profile_root)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"REFUSED:XAAS_PUBLIC_PROFILE_SOURCE:{exc}", file=sys.stderr)
        return 4

    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")

    if report["source_failures"]:
        print("REFUSED:XAAS_PUBLIC_PROFILE_SOURCE_FAILURE", file=sys.stderr)
        return 4
    print(
        "PARTIAL_ALIVE:XAAS_PUBLIC_PROFILE "
        f"triples={report['graph_triples']} "
        f"term_coverage={report['summary']['term_coverage']} "
        f"partial={report['summary']['partial']} gaps={report['summary']['gaps']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
