#!/usr/bin/env python3
"""Independent qualification court for the survival benchmark ontology/catalog."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from rdflib import Graph, Namespace
from pyshacl import validate

ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "gates"
QUERIES = ROOT / "queries"
PAS = Namespace(
    "https://seanchatmangpt.github.io/ggen-marketplace/ontology/"
    "premature-actuation-survival#"
)

EXPECTED_POLICIES = {
    "llm-native",
    "llm-tools",
    "selective-llm",
    "planner-llm-residue",
    "formal-generated",
}
EXPECTED_FACTORS = {
    "authority": {"full", "filtered", "expired"},
    "transport": {"stable", "lossy", "reordered"},
    "evidence": {"complete", "delayed", "missing"},
    "terminal_signal": {"exact", "stale", "false_positive"},
}
EXPECTED_FAULTS = {
    "wrong_subject",
    "authority_drop",
    "admission_drop",
    "receipt_drop",
    "premature_terminal",
    "tool_blackout",
    "replay_corruption",
    "llm_token_burst",
}
EXPECTED_METHODS = {
    "kaplan-meier",
    "rmst",
    "greenwood-loglog-ci",
    "wilson-failure-probability",
    "log-rank",
    "cusum",
}


def query(graph: Graph, name: str):
    return list(graph.query((QUERIES / name).read_text(encoding="utf-8")))


def main() -> int:
    graph = Graph()
    graph.parse(ROOT / "ontology.ttl", format="turtle")
    shapes = Graph()
    shapes.parse(ROOT / "shapes.ttl", format="turtle")

    conforms, _, report_text = validate(
        data_graph=graph,
        shacl_graph=shapes,
        inference="rdfs",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
    )
    if not conforms:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_SHACL",
                    "detail": report_text,
                },
                sort_keys=True,
            )
        )
        return 1

    gate_rows = {
        gate.name: len(list(graph.query(gate.read_text(encoding="utf-8"))))
        for gate in sorted(GATES.glob("*.rq"))
    }
    firing = {name: count for name, count in gate_rows.items() if count}
    if firing:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_ONTOLOGY_GATE",
                    "gates": firing,
                },
                sort_keys=True,
            )
        )
        return 1

    policy_rows = query(graph, "30_policy_catalog.rq")
    policy_ids = {str(row.policyId) for row in policy_rows}
    if policy_ids != EXPECTED_POLICIES or len(policy_rows) != len(EXPECTED_POLICIES):
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_POLICY_CATALOG",
                    "observed": sorted(policy_ids),
                    "row_count": len(policy_rows),
                },
                sort_keys=True,
            )
        )
        return 1

    factor_rows = query(graph, "40_factor_catalog.rq")
    factors: dict[str, set[str]] = {}
    for row in factor_rows:
        factors.setdefault(str(row.factorName), set()).add(str(row.levelId))
    if factors != EXPECTED_FACTORS or len(factor_rows) != 12:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_FACTOR_CATALOG",
                    "observed": {
                        key: sorted(value) for key, value in sorted(factors.items())
                    },
                    "row_count": len(factor_rows),
                },
                sort_keys=True,
            )
        )
        return 1

    fault_rows = query(graph, "50_fault_catalog.rq")
    fault_ids = {str(row.faultKindId) for row in fault_rows}
    if fault_ids != EXPECTED_FAULTS or len(fault_rows) != len(EXPECTED_FAULTS):
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_FAULT_CATALOG",
                    "observed": sorted(fault_ids),
                    "row_count": len(fault_rows),
                },
                sort_keys=True,
            )
        )
        return 1

    method_rows = query(graph, "60_analysis_catalog.rq")
    method_ids = {str(row.methodId) for row in method_rows}
    families = Counter(str(row.methodFamily) for row in method_rows)
    if method_ids != EXPECTED_METHODS or len(method_rows) != len(EXPECTED_METHODS):
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_ANALYSIS_CATALOG",
                    "observed": sorted(method_ids),
                    "families": dict(sorted(families.items())),
                    "row_count": len(method_rows),
                },
                sort_keys=True,
            )
        )
        return 1

    contract = PAS.contractV1
    required_contract = {
        PAS.authorityCeiling: "OBSERVE|SELECT|CONSTRUCT",
        PAS.grantsDoAuthority: False,
        PAS.receiptRequiredForDo: True,
        PAS.replayEvidenceSupported: True,
        PAS.analysisOwner: "autofde-lab",
        PAS.manufactureOwner: "gymact",
    }
    missing = []
    for predicate, expected in required_contract.items():
        values = {value.toPython() for value in graph.objects(contract, predicate)}
        if values != {expected}:
            missing.append(
                {
                    "predicate": str(predicate),
                    "expected": expected,
                    "observed": sorted(str(value) for value in values),
                }
            )
    if missing:
        print(
            json.dumps(
                {
                    "refusal": "REFUSED_SURVIVAL_CONTRACT_BINDING",
                    "mismatches": missing,
                },
                sort_keys=True,
            )
        )
        return 1

    print(
        json.dumps(
            {
                "observed": "ADMITTED",
                "policies": len(policy_rows),
                "factor_levels": len(factor_rows),
                "fault_kinds": len(fault_rows),
                "analysis_methods": len(method_rows),
                "gates": len(gate_rows),
                "shacl": "conforms",
                "authority": "none",
                "actuation_performed": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
