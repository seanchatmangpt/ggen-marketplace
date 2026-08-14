#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tomllib

from rdflib import Graph, Literal, Namespace, RDF, RDFS
from rdflib.namespace import SKOS

ROOT = Path(__file__).resolve().parents[1]
V30 = Namespace("https://ggen.io/marketplace/vision2030#")
Q = Namespace("https://ggen.io/marketplace/vision2030/qualification#")
PROV = Namespace("http://www.w3.org/ns/prov#")
ODRL = Namespace("http://www.w3.org/ns/odrl/2/")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
MUTATING_SPARQL = re.compile(
    r"\b(?:INSERT|DELETE|LOAD|CLEAR|CREATE|DROP|COPY|MOVE|ADD)\b", re.IGNORECASE
)
REMOTE_SPARQL = re.compile(r"\bSERVICE\b", re.IGNORECASE)


class QualificationRefusal(ValueError):
    pass


def refuse(code: str, detail: str) -> None:
    raise QualificationRefusal(f"{code}:{detail}")


def validate_subject_sha(subject_sha: str) -> str:
    if not HEX40.fullmatch(subject_sha):
        refuse("SUBJECT_NOT_IMMUTABLE", subject_sha)
    return subject_sha


def validate_output_path(output_file: str) -> str:
    candidate = Path(output_file)
    if candidate.is_absolute() or ".." in candidate.parts or not candidate.parts:
        refuse("OUTPUT_ESCAPE", output_file)
    return candidate.as_posix()


def validate_query_text(text: str, source: str) -> None:
    if MUTATING_SPARQL.search(text):
        refuse("MUTATING_SPARQL", source)
    if REMOTE_SPARQL.search(text):
        refuse("REMOTE_SPARQL", source)
    if not re.search(r"\bSELECT\b", text, re.IGNORECASE):
        refuse("NON_SELECT_QUERY", source)


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def source_files(root: Path) -> list[Path]:
    fixed = [
        root / "package.toml",
        root / "ggen.toml",
        root / "ontology.ttl",
        root / "shapes.ttl",
        root / "qualification" / "contract.ttl",
        root / "scripts" / "verify.py",
    ]
    dynamic = sorted((root / "queries").glob("*.rq")) + sorted(
        (root / "templates").glob("*.tera")
    )
    files = fixed + dynamic
    missing = [str(path.relative_to(root)) for path in files if not path.is_file()]
    if missing:
        refuse("SOURCE_MISSING", ",".join(missing))
    return files


def source_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in source_files(root):
        relative = path.relative_to(root).as_posix().encode()
        digest.update(len(relative).to_bytes(4, "big"))
        digest.update(relative)
        payload = path.read_bytes()
        digest.update(len(payload).to_bytes(8, "big"))
        digest.update(payload)
    return digest.hexdigest()


def verify_generation_contract(root: Path, ggen: dict) -> list[str]:
    generation = ggen.get("generation", {})
    if generation.get("output_dir") != "generated":
        refuse("OUTPUT_ROOT", str(generation.get("output_dir")))

    outputs: list[str] = []
    for rule in ggen.get("generation", {}).get("rules", []):
        output_file = validate_output_path(str(rule.get("output_file", "")))
        outputs.append(f"generated/{output_file}")

        query_rel = rule.get("query", {}).get("file")
        template_rel = rule.get("template", {}).get("file")
        if not query_rel or not template_rel:
            refuse("RULE_SOURCE_MISSING", str(rule.get("name", "unnamed")))

        query_path = root / str(query_rel)
        template_path = root / str(template_rel)
        if not query_path.is_file() or not template_path.is_file():
            refuse("RULE_SOURCE_MISSING", str(rule.get("name", "unnamed")))
        validate_query_text(query_path.read_text(encoding="utf-8"), str(query_rel))
        if "results" not in template_path.read_text(encoding="utf-8"):
            refuse("TEMPLATE_IGNORES_QUERY", str(template_rel))

    if len(outputs) != len(set(outputs)):
        refuse("DUPLICATE_OUTPUT", ",".join(outputs))

    generated = root / "generated"
    if generated.exists() and any(path.is_file() for path in generated.rglob("*")):
        refuse("PROJECTION_COMMITTED", "generated/")
    return sorted(outputs)


def verify_authority_contract(root: Path) -> None:
    graph = Graph()
    graph.parse(root / "qualification" / "contract.ttl", format="turtle")
    policy = Q.Vision2030QualificationPolicy
    required = (
        (policy, RDF.type, ODRL.Policy),
        (policy, Q.authorityCeiling, Literal("CONSTRUCT_ONLY")),
        (policy, Q.doAuthority, Literal(False)),
        (policy, Q.requiresExactSubject, Literal(True)),
        (policy, Q.externalExecutionRequired, Literal(True)),
        (policy, Q.selfCertificationAllowed, Literal(False)),
        (Q.QualificationActivity, RDFS.subClassOf, PROV.Activity),
        (Q.QualificationReceipt, RDFS.subClassOf, PROV.Entity),
    )
    for triple in required:
        if triple not in graph:
            refuse("AUTHORITY_CONTRACT", "missing required qualification law")
    if (policy, ODRL.prohibition, Q.NoAmbientDo) not in graph:
        refuse("AUTHORITY_CONTRACT", "ambient DO prohibition missing")
    if (Q.NoAmbientDo, ODRL.action, Q.Actuate) not in graph:
        refuse("AUTHORITY_CONTRACT", "actuation prohibition missing")


def verify_capability_graph(root: Path) -> dict:
    graph = Graph()
    graph.parse(root / "ontology.ttl", format="turtle")
    graph.parse(root / "shapes.ttl", format="turtle")

    capabilities = sorted(set(graph.subjects(RDF.type, V30.Capability)), key=str)
    families = set(graph.subjects(RDF.type, V30.CapabilityFamily))
    if len(capabilities) < 50:
        refuse("CAPABILITY_COUNT", f"expected>=50 observed={len(capabilities)}")
    if len(families) < 10:
        refuse("FAMILY_COUNT", f"expected>=10 observed={len(families)}")

    scores: list[tuple[int, str]] = []
    for capability in capabilities:
        for predicate in (
            SKOS.prefLabel,
            V30.family,
            V30.leverageScore,
            V30.requiredStanding,
            V30.cognitionValueDirection,
        ):
            values = list(graph.objects(capability, predicate))
            if len(values) != 1:
                refuse("CAPABILITY_CARDINALITY", f"{capability}:{predicate}")

        family = next(graph.objects(capability, V30.family))
        if (family, RDF.type, V30.CapabilityFamily) not in graph:
            refuse("UNKNOWN_FAMILY", str(family))

        score = int(next(graph.objects(capability, V30.leverageScore)))
        if not 0 <= score <= 100:
            refuse("LEVERAGE_RANGE", str(capability))

        direction = str(next(graph.objects(capability, V30.cognitionValueDirection)))
        if direction != "more-valuable-as-cognition-abundant":
            refuse("COGNITION_INVERSION", str(capability))

        standing = next(graph.objects(capability, V30.requiredStanding))
        labels = [str(value) for value in graph.objects(standing, SKOS.prefLabel)]
        if labels != ["ALIVE"]:
            refuse("REQUIRED_STANDING", str(capability))

        for predicate in (
            V30.problemEliminated,
            V30.primitiveRequirement,
            V30.ggenRole,
            V30.consequence2030,
        ):
            if not list(graph.objects(family, predicate)):
                refuse("FAMILY_DEFAULT", f"{family}:{predicate}")

        scores.append((score, str(next(graph.objects(capability, SKOS.prefLabel)))))

    scores.sort(reverse=True)
    return {
        "capabilities": len(capabilities),
        "families": len(families),
        "crown_score": scores[0][0],
        "top_capabilities": [name for _, name in scores[:5]],
    }


def verify_package(root: Path, subject_sha: str) -> dict:
    subject_sha = validate_subject_sha(subject_sha)
    package = load_toml(root / "package.toml")
    ggen = load_toml(root / "ggen.toml")

    package_version = str(package.get("package", {}).get("version", ""))
    project_version = str(ggen.get("project", {}).get("version", ""))
    if package_version != project_version:
        refuse("VERSION_SKEW", f"package={package_version} ggen={project_version}")
    if package_version != "0.2.0":
        refuse("VERSION_CONTRACT", package_version)

    outputs = verify_generation_contract(root, ggen)
    verify_authority_contract(root)
    graph = verify_capability_graph(root)

    return {
        "schema": "ggen-marketplace.vision2030-qualification/2",
        "subject_sha": subject_sha,
        "qualification": "PASS",
        "standing": "CANDIDATE",
        "authority_ceiling": "CONSTRUCT_ONLY",
        "do_authority": False,
        "self_certifying": False,
        "external_execution_required": True,
        "source_digest_algorithm": "sha256",
        "source_digest": source_digest(root),
        "generated_outputs": outputs,
        **graph,
    }


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subject-sha", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        receipt = verify_package(ROOT, args.subject_sha)
    except (QualificationRefusal, OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"REFUSED:VISION_2030_QUALIFICATION:{exc}", file=sys.stderr)
        return 2

    rendered = canonical_json(receipt) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
