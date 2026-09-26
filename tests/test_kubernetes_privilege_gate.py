"""SEC-PRIV-001: kubernetes-workload-pack refuses privileged containers at generate-time.

Evaluates the pack's own gate queries against every fixture, and a spelling
sweep of privilege-bearing securityContext blocks, on two independent SPARQL
engines (Oxigraph and rdflib). A row from any gate means ggen refuses the
graph; zero rows from every gate means it is admitted.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PACK = Path(__file__).resolve().parents[1] / "packs" / "kubernetes-workload-pack"
GATES = sorted((PACK / "gates").glob("*.rq"))

# fixture directory -> set of (gate stem, violation) rows expected, empty = ADMITTED
EXPECTED = {
    "examples/minimal-secure-workload": set(),
    "examples/high-assurance-workload": set(),
    "examples/xaas-workload": set(),
    "examples/privileged-typed-exception": set(),
    "playground": set(),
    "playground/scenarios/legitimate-exception": set(),
    "playground/scenarios/mutable-image": set(),
    "examples/negative-controls/mutable-image-tag-KNOWN_GAP": set(),
    "examples/negative-controls/missing-resources": {("010_required", None)},
    "examples/negative-controls/missing-security-context": {("010_required", None)},
    "playground/scenarios/missing-resources": {("010_required", None)},
    "examples/negative-controls/privileged-container": {("020_privilege_refusal", "PRIVILEGE_UNWAIVED")},
    "playground/scenarios/privileged-container": {("020_privilege_refusal", "PRIVILEGE_UNWAIVED")},
    "examples/negative-controls/privileged-incomplete-exception": {
        ("020_privilege_refusal", "EXCEPTION_INCOMPLETE"),
        ("020_privilege_refusal", "PRIVILEGE_UNWAIVED"),
    },
    "examples/negative-controls/scalar-newline-injection": {("020_privilege_refusal", "SCALAR_LINE_BREAK")},
    "examples/negative-controls/obfuscated-privilege-key": {
        ("020_privilege_refusal", "SECURITY_BLOCK_OBFUSCATION"),
    },
}


def _oxigraph(turtle: list[str]):
    ox = pytest.importorskip("pyoxigraph")
    store = ox.Store()
    for text in turtle:
        store.load(input=text, format=ox.RdfFormat.TURTLE)
    return lambda query: [[str(term.value) if term is not None else None for term in row] for row in store.query(query)]


def _rdflib(turtle: list[str]):
    rdflib = pytest.importorskip("rdflib")
    graph = rdflib.Graph()
    for text in turtle:
        graph.parse(data=text, format="turtle")
    return lambda query: [[str(term) if term is not None else None for term in row] for row in graph.query(query)]


ENGINES = {"oxigraph": _oxigraph, "rdflib": _rdflib}


def _verdict(engine: str, facts: str) -> set[tuple[str, str | None]]:
    run = ENGINES[engine]([(PACK / "ontology.ttl").read_text(encoding="utf-8"), facts])
    rows: set[tuple[str, str | None]] = set()
    for gate in GATES:
        for row in run(gate.read_text(encoding="utf-8")):
            rows.add((gate.stem, row[1] if gate.stem == "020_privilege_refusal" else None))
    return rows


def _facts_path(directory: Path) -> Path:
    facts = directory / "facts.ttl"
    return facts if facts.exists() else directory / "baseline.ttl"


def test_expected_matrix_covers_every_fixture() -> None:
    discovered = {
        str(toml.parent.relative_to(PACK))
        for toml in PACK.rglob("ggen.toml")
        if _facts_path(toml.parent).exists()
    }
    assert discovered == set(EXPECTED)


@pytest.mark.parametrize("engine", sorted(ENGINES))
@pytest.mark.parametrize("fixture", sorted(EXPECTED))
def test_fixture_verdict(engine: str, fixture: str) -> None:
    facts = _facts_path(PACK / fixture).read_text(encoding="utf-8")
    assert _verdict(engine, facts) == EXPECTED[fixture]


GRAPH = """@prefix k8s: <http://seanchatmangpt.github.io/packs/kubernetes#> .
@prefix ex: <https://example.com/sweep#> .
ex:w a k8s:Workload ; k8s:workloadName "w" ; k8s:fileName "w.yaml" ;
  k8s:podSecurityContextBlock \"\"\"runAsNonRoot: true\"\"\" .
ex:c a k8s:Container ; k8s:inWorkload ex:w ; k8s:containerName "c" ;
  k8s:resourceRequestsBlock \"\"\"cpu: 1m\"\"\" ; k8s:resourceLimitsBlock \"\"\"cpu: 2m\"\"\" ;
  k8s:containerSecurityContextBlock \"\"\"{block}\"\"\" {extra}.
"""

EXCEPTION = """; k8s:privilegeException ex:x .
ex:x a k8s:SecurityException ; k8s:exceptionControl "SEC-PRIV-001" ;
  k8s:exceptionRationale "r" ; k8s:compensatingControl "c" ; k8s:approvedBy "a" """

# Every spelling here names privilege; each must be refused without an exception.
PRIVILEGED = [
    "privileged: true",
    "privileged: True",
    'privileged: "true"',
    "privileged: yes",
    "privileged: !!bool true",
    "privileged:   true   ",
    "{privileged: true}",
    '"privileged": true',
    "Privileged: true",
    "allowPrivilegeEscalation: true",
    "allowPrivilegeEscalation: false\nprivileged: true",
    "privileged: false\nprivileged: true",
    "privileged: false # but see below\nallowPrivilegeEscalation: 1",
]

LAWFUL = [
    "allowPrivilegeEscalation: false",
    "privileged: false",
    "allowPrivilegeEscalation: false\nprivileged: false\nreadOnlyRootFilesystem: true",
    'allowPrivilegeEscalation: false\ncapabilities:\n  drop: ["ALL"]',
    "  privileged: false  \r\nallowPrivilegeEscalation: false",
]


def _sweep(block: str, extra: str = "") -> str:
    return GRAPH.replace("{block}", block.replace('"', '\\"')).replace("{extra}", extra)


@pytest.mark.parametrize("engine", sorted(ENGINES))
@pytest.mark.parametrize("block", PRIVILEGED)
def test_privileged_spelling_is_refused(engine: str, block: str) -> None:
    assert ("020_privilege_refusal", "PRIVILEGE_UNWAIVED") in _verdict(engine, _sweep(block))


@pytest.mark.parametrize("engine", sorted(ENGINES))
@pytest.mark.parametrize("block", PRIVILEGED)
def test_complete_typed_exception_admits(engine: str, block: str) -> None:
    assert _verdict(engine, _sweep(block, EXCEPTION)) == set()


@pytest.mark.parametrize("engine", sorted(ENGINES))
@pytest.mark.parametrize("block", LAWFUL)
def test_lawful_spelling_is_admitted(engine: str, block: str) -> None:
    assert _verdict(engine, _sweep(block)) == set()


@pytest.mark.parametrize("engine", sorted(ENGINES))
@pytest.mark.parametrize(
    "block",
    [
        '"privil\\\\x65ged": true',
        "base: &b {x: 1}",
        "<<: *b",
        "privileged: *t",
    ],
)
def test_obfuscation_is_refused_even_with_exception(engine: str, block: str) -> None:
    rows = _verdict(engine, _sweep(block, EXCEPTION))
    assert ("020_privilege_refusal", "SECURITY_BLOCK_OBFUSCATION") in rows


@pytest.mark.parametrize("engine", sorted(ENGINES))
@pytest.mark.parametrize("field", ["name", "fields"])
def test_exception_missing_field_is_refused(engine: str, field: str) -> None:
    partial = EXCEPTION.replace('k8s:approvedBy "a" ', "") if field == "fields" else EXCEPTION.replace(
        '"SEC-PRIV-001"', '"SEC-OTHER-001"'
    )
    rows = _verdict(engine, _sweep("privileged: true", partial))
    assert ("020_privilege_refusal", "EXCEPTION_INCOMPLETE") in rows
    assert ("020_privilege_refusal", "PRIVILEGE_UNWAIVED") in rows
