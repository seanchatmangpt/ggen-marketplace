"""Court for scripts/profile_intake.py (Phase 2 intake; Chicago style).

Real files, real subprocess, real rdflib parses -- no mocks.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from rdflib import Graph, Literal, Namespace, RDF

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "profile_intake.py"

AAIF = Namespace("https://aaif.io/ontology#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace("https://schema.org/")

JSON_FIXTURE = {
    "name": "Ada Lovelace",
    "headline": "Analytical Engine Engineer",
    "summary": "Wrote the first algorithm intended for implementation on Babbage's "
               "analytical engine and saw far beyond its intended arithmetic purpose.",
    "url": "https://example.com/ada",
    "experience": [
        {
            "title": "Principal Mathematician",
            "company": "Analytical Engines Ltd",
            "period": "1843 - Present",
        }
    ],
    "skills": ["algorithms", "computation", "poetry"],
}

TEXT_FIXTURE = """Ada Lovelace
Analytical Engine Engineer
ada@example.com
https://example.com/ada

Wrote the first algorithm intended for implementation on Babbage's analytical
engine and saw far beyond its intended arithmetic purpose.

Principal Mathematician
Analytical Engines Ltd
1843 - Present

Skills: algorithms, computation, poetry
"""


@pytest.fixture
def json_input(tmp_path: Path) -> Path:
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(JSON_FIXTURE), encoding="utf-8")
    return path


@pytest.fixture
def text_input(tmp_path: Path) -> Path:
    path = tmp_path / "profile.txt"
    path.write_text(TEXT_FIXTURE, encoding="utf-8")
    return path


def run_intake(*cli_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *cli_args],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_json_input_produces_normalized_shape(tmp_path: Path, json_input: Path) -> None:
    out = tmp_path / "out"
    result = run_intake(str(json_input), "--out", str(out))
    assert result.returncode == 0, result.stderr

    normalized = json.loads((out / "profile.json").read_text(encoding="utf-8"))
    assert normalized["name"] == "Ada Lovelace"
    assert normalized["headline"] == "Analytical Engine Engineer"
    assert normalized["url"] == "https://example.com/ada"
    assert normalized["positions"] == [
        {
            "title": "Principal Mathematician",
            "organization": "Analytical Engines Ltd",
            "period": "1843 - Present",
        }
    ]
    assert normalized["skills"] == ["algorithms", "computation", "poetry"]
    assert normalized["schema"] == "https://ggen.dev/marketplace/profile-intake/v1"
    # sort_keys normalization
    raw = (out / "profile.json").read_text(encoding="utf-8")
    assert raw.index('"headline"') < raw.index('"name"') < raw.index('"positions"')


def test_emitted_ttl_parses_with_foaf_person_and_aaif_agent(
    tmp_path: Path, json_input: Path
) -> None:
    out = tmp_path / "out"
    result = run_intake(str(json_input), "--out", str(out))
    assert result.returncode == 0, result.stderr

    graph = Graph().parse(out / "profile.ttl", format="turtle")
    person = AAIF.AdaLovelace
    assert (person, RDF.type, FOAF.Person) in graph
    assert (person, SCHEMA.jobTitle, None) in graph
    assert (person, SCHEMA.knowsAbout, None) in graph

    agents = list(graph.subjects(RDF.type, AAIF.Agent))
    assert agents, "no aaif:Agent individual emitted"
    agent = agents[0]
    assert (agent, AAIF.name, None) in graph
    assert (agent, AAIF.description, None) in graph
    assert (agent, AAIF.url, None) in graph
    assert (agent, AAIF.version, None) in graph


def test_text_input_extracts_name_headline_skills(
    tmp_path: Path, text_input: Path
) -> None:
    out = tmp_path / "out"
    result = run_intake(str(text_input), "--out", str(out))
    assert result.returncode == 0, result.stderr

    normalized = json.loads((out / "profile.json").read_text(encoding="utf-8"))
    assert normalized["name"] == "Ada Lovelace"
    assert normalized["headline"] == "Analytical Engine Engineer"
    assert normalized["email"] == "ada@example.com"
    assert normalized["positions"] == [
        {
            "title": "Principal Mathematician",
            "organization": "Analytical Engines Ltd",
            "period": "1843 - Present",
        }
    ]
    assert normalized["skills"] == ["algorithms", "computation", "poetry"]

    graph = Graph().parse(out / "profile.ttl", format="turtle")
    assert (AAIF.AdaLovelace, RDF.type, FOAF.Person) in graph


def test_html_input_extracts_name_and_headline(tmp_path: Path) -> None:
    html_input = tmp_path / "profile.html"
    html_input.write_text(
        "<html><head><title>Ada Lovelace - Analytical Engine Engineer</title></head>"
        "<body><script>ignored()</script>"
        "<p>Ada Lovelace</p>"
        "<p>Analytical Engine Engineer</p>"
        "<p>Principal Mathematician at Analytical Engines Ltd 1843 - Present</p>"
        "<p>Skills: algorithms, computation</p>"
        "<a href='mailto:ada@example.com'>email</a></body></html>",
        encoding="utf-8",
    )
    out = tmp_path / "out"
    result = run_intake(str(html_input), "--out", str(out))
    assert result.returncode == 0, result.stderr

    normalized = json.loads((out / "profile.json").read_text(encoding="utf-8"))
    assert normalized["name"] == "Ada Lovelace"
    assert normalized["headline"] == "Analytical Engine Engineer"
    assert normalized["email"] == "ada@example.com"

    graph = Graph().parse(out / "profile.ttl", format="turtle")
    assert (AAIF.AdaLovelace, RDF.type, FOAF.Person) in graph


def test_empty_file_refused_exit_2(tmp_path: Path) -> None:
    empty = tmp_path / "empty.json"
    empty.write_text("", encoding="utf-8")
    result = run_intake(str(empty), "--out", str(tmp_path / "out"))
    assert result.returncode == 2
    assert "REFUSED:PROFILE_EMPTY" in result.stderr
    assert not (tmp_path / "out" / "profile.json").exists()


def test_nameless_profile_refused_exit_2(tmp_path: Path) -> None:
    nameless = tmp_path / "nameless.json"
    nameless.write_text(
        json.dumps({"headline": "Mystery Engineer", "skills": ["rust"]}),
        encoding="utf-8",
    )
    result = run_intake(str(nameless), "--out", str(tmp_path / "out"))
    assert result.returncode == 2
    assert "REFUSED:PROFILE_NO_NAME" in result.stderr
    assert not (tmp_path / "out" / "profile.json").exists()


def test_malformed_json_refused_exit_2(tmp_path: Path) -> None:
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")
    result = run_intake(str(broken), "--out", str(tmp_path / "out"))
    assert result.returncode == 2
    assert "REFUSED:PROFILE_UNREADABLE" in result.stderr


def test_missing_file_refused_exit_2(tmp_path: Path) -> None:
    result = run_intake(str(tmp_path / "nope.json"), "--out", str(tmp_path / "out"))
    assert result.returncode == 2
    assert "REFUSED:PROFILE_UNREADABLE" in result.stderr


def test_residency_region_lock_emitted_on_aaif_agent(tmp_path: Path) -> None:
    with_lock = tmp_path / "locked.json"
    with_lock.write_text(
        json.dumps(
            {
                **JSON_FIXTURE,
                "deployment": {
                    "namespace": "aaif-enterprise",
                    "residencyRegionLock": "us-central1",
                },
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    result = run_intake(str(with_lock), "--out", str(out))
    assert result.returncode == 0, result.stderr

    normalized = json.loads((out / "profile.json").read_text(encoding="utf-8"))
    assert normalized["residencyRegionLock"] == "us-central1"

    graph = Graph().parse(out / "profile.ttl", format="turtle")
    agents = list(graph.subjects(RDF.type, AAIF.Agent))
    assert agents, "no aaif:Agent individual emitted"
    assert (agents[0], AAIF.residencyRegionLock, Literal("us-central1")) in graph


def test_no_residency_region_lock_means_no_triple(tmp_path: Path, json_input: Path) -> None:
    out = tmp_path / "out"
    result = run_intake(str(json_input), "--out", str(out))
    assert result.returncode == 0, result.stderr

    normalized = json.loads((out / "profile.json").read_text(encoding="utf-8"))
    assert "residencyRegionLock" not in normalized

    graph = Graph().parse(out / "profile.ttl", format="turtle")
    assert (None, AAIF.residencyRegionLock, None) not in graph


def test_lock_digest_deterministic(tmp_path: Path, json_input: Path) -> None:
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    assert run_intake(str(json_input), "--out", str(out_a), "--lock").returncode == 0
    assert run_intake(str(json_input), "--out", str(out_b), "--lock").returncode == 0

    lock_a = json.loads((out_a / "profile.lock.json").read_text(encoding="utf-8"))
    lock_b = json.loads((out_b / "profile.lock.json").read_text(encoding="utf-8"))
    assert lock_a["digest"] == lock_b["digest"]
    assert lock_a["digest"].startswith("sha256:")

    # The lock digest covers the actual output bytes: tamper with one output
    # and a recomputed fingerprint no longer matches the recorded lock.
    sys.path.insert(0, str(ROOT / "scripts"))
    import profile_intake

    assert lock_a["digest"] == (
        "sha256:" + profile_intake.fingerprint_paths(
            [out_a / "profile.json", out_a / "profile.ttl"], out_a
        )
    )
    (out_b / "profile.ttl").write_text(
        (out_b / "profile.ttl").read_text(encoding="utf-8") + "\n# tampered\n",
        encoding="utf-8",
    )
    tampered = profile_intake.fingerprint_paths(
        [out_b / "profile.json", out_b / "profile.ttl"], out_b
    )
    assert "sha256:" + tampered != lock_b["digest"]
