from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

_marketplace_spec = importlib.util.spec_from_file_location("marketplace", SCRIPTS / "marketplace.py")
assert _marketplace_spec is not None and _marketplace_spec.loader is not None
_marketplace = importlib.util.module_from_spec(_marketplace_spec)
sys.modules[_marketplace_spec.name] = _marketplace
_marketplace_spec.loader.exec_module(_marketplace)
Pack = _marketplace.Pack

SCRIPT = SCRIPTS / "qualify_packs.py"
spec = importlib.util.spec_from_file_location("qualify_packs", SCRIPT)
assert spec is not None and spec.loader is not None
qp = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = qp
spec.loader.exec_module(qp)


def make_pack(tmp_path: Path, name: str = "demo-pack") -> Pack:
    pack_dir = tmp_path / name
    pack_dir.mkdir()
    ontology_path = pack_dir / "ontology.ttl"
    ontology_path.write_text("@prefix ex: <http://example.org/ns#> .\n", encoding="utf-8")
    return Pack(
        name=name,
        version="0.1.0",
        description="test",
        path=pack_dir,
        ontologies=(ontology_path,),
        templates=(),
        native_gates=(),
        verifier_gates=(),
    )


# --- pack_source_fingerprint / snapshot_tree / snapshot_digest ------------


def test_pack_source_fingerprint_stable_across_calls(tmp_path: Path):
    pack = make_pack(tmp_path)
    assert qp.pack_source_fingerprint(pack) == qp.pack_source_fingerprint(pack)


def test_pack_source_fingerprint_changes_when_file_content_changes(tmp_path: Path):
    pack = make_pack(tmp_path)
    before = qp.pack_source_fingerprint(pack)
    (pack.path / "ontology.ttl").write_text("@prefix ex: <http://example.org/other#> .\n", encoding="utf-8")
    after = qp.pack_source_fingerprint(pack)
    assert before != after


def test_snapshot_tree_ignores_runtime_roots(tmp_path: Path):
    root = tmp_path / "capsule"
    (root / ".git").mkdir(parents=True)
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (root / "real.txt").write_text("kept\n", encoding="utf-8")
    records = qp.snapshot_tree(root)
    paths = {path for path, _ in records}
    assert paths == {"real.txt"}


def test_snapshot_digest_is_order_independent_of_input_but_content_sensitive(tmp_path: Path):
    root = tmp_path / "capsule"
    root.mkdir()
    (root / "a.txt").write_text("aaa\n", encoding="utf-8")
    (root / "b.txt").write_text("bbb\n", encoding="utf-8")
    records_one = qp.snapshot_tree(root)
    digest_one = qp.snapshot_digest(records_one)

    (root / "b.txt").write_text("ccc\n", encoding="utf-8")
    records_two = qp.snapshot_tree(root)
    digest_two = qp.snapshot_digest(records_two)

    assert digest_one != digest_two
    # re-snapshotting identical content reproduces the same digest
    assert qp.snapshot_digest(qp.snapshot_tree(root)) == digest_two


# --- qualification_extra_ontologies ---------------------------------------


def test_qualification_extra_ontologies_absent_contract_returns_empty(tmp_path: Path):
    pack = make_pack(tmp_path)
    assert qp.qualification_extra_ontologies(pack) == ()


def test_qualification_extra_ontologies_resolves_real_files(tmp_path: Path):
    pack = make_pack(tmp_path)
    extra = pack.path / "extra.ttl"
    extra.write_text("@prefix ex: <http://example.org/extra#> .\n", encoding="utf-8")
    (pack.path / "qualification.toml").write_text(
        'consumer.extra_ontologies = ["extra.ttl"]\n', encoding="utf-8"
    )
    result = qp.qualification_extra_ontologies(pack)
    assert result == (extra,)


def test_qualification_extra_ontologies_rejects_absolute_path(tmp_path: Path):
    pack = make_pack(tmp_path)
    (pack.path / "qualification.toml").write_text(
        'consumer.extra_ontologies = ["/etc/passwd"]\n', encoding="utf-8"
    )
    with pytest.raises(qp.QualificationContractError):
        qp.qualification_extra_ontologies(pack)


def test_qualification_extra_ontologies_rejects_parent_traversal(tmp_path: Path):
    pack = make_pack(tmp_path)
    (pack.path / "qualification.toml").write_text(
        'consumer.extra_ontologies = ["../secret.ttl"]\n', encoding="utf-8"
    )
    with pytest.raises(qp.QualificationContractError):
        qp.qualification_extra_ontologies(pack)


def test_qualification_extra_ontologies_rejects_missing_file(tmp_path: Path):
    pack = make_pack(tmp_path)
    (pack.path / "qualification.toml").write_text(
        'consumer.extra_ontologies = ["nope.ttl"]\n', encoding="utf-8"
    )
    with pytest.raises(qp.QualificationContractError):
        qp.qualification_extra_ontologies(pack)


def test_qualification_extra_ontologies_rejects_malformed_toml(tmp_path: Path):
    pack = make_pack(tmp_path)
    (pack.path / "qualification.toml").write_text("not = [valid toml", encoding="utf-8")
    with pytest.raises(qp.QualificationContractError):
        qp.qualification_extra_ontologies(pack)


def test_qualification_extra_ontologies_rejects_non_string_list(tmp_path: Path):
    pack = make_pack(tmp_path)
    (pack.path / "qualification.toml").write_text(
        "consumer.extra_ontologies = [1, 2]\n", encoding="utf-8"
    )
    with pytest.raises(qp.QualificationContractError):
        qp.qualification_extra_ontologies(pack)


# --- combine_rdf ------------------------------------------------------------


def test_combine_rdf_concatenates_sources_with_headers_and_extra(tmp_path: Path):
    one = tmp_path / "one.ttl"
    one.write_text("ex:a ex:b ex:c .", encoding="utf-8")
    two = tmp_path / "two.ttl"
    two.write_text("ex:d ex:e ex:f .\n", encoding="utf-8")
    combined = qp.combine_rdf((one, two), extra="ex:g ex:h ex:i .\n")
    assert "QUALIFICATION SOURCE: " in combined
    assert "ex:a ex:b ex:c ." in combined
    assert "ex:d ex:e ex:f ." in combined
    assert combined.endswith("ex:g ex:h ex:i .\n")


def test_combine_rdf_empty_paths_returns_only_extra(tmp_path: Path):
    assert qp.combine_rdf((), extra="only-extra") == "only-extra"


# --- copy_composed_packs ----------------------------------------------------


def test_copy_composed_packs_no_ggen_toml_is_a_noop(tmp_path: Path):
    pack = make_pack(tmp_path)
    capsule = tmp_path / "capsule"
    capsule.mkdir()
    qp.copy_composed_packs(pack, capsule)
    assert list(capsule.iterdir()) == []


def test_copy_composed_packs_copies_real_sibling(tmp_path: Path):
    packs_root = tmp_path / "packs"
    packs_root.mkdir()
    sibling = packs_root / "sibling-pack"
    sibling.mkdir()
    (sibling / "marker.txt").write_text("sibling-content\n", encoding="utf-8")

    pack_dir = packs_root / "composer-pack"
    pack_dir.mkdir()
    (pack_dir / "ggen.toml").write_text(
        '[packs]\nsibling-pack = { path = "../sibling-pack" }\n', encoding="utf-8"
    )
    pack = Pack(
        name="composer-pack",
        version="0.1.0",
        description="test",
        path=pack_dir,
        ontologies=(),
        templates=(),
        native_gates=(),
        verifier_gates=(),
    )
    capsule = tmp_path / "capsule"
    capsule.mkdir()
    qp.copy_composed_packs(pack, capsule)
    copied = capsule / "sibling-pack" / "marker.txt"
    assert copied.is_file()
    assert copied.read_text(encoding="utf-8") == "sibling-content\n"


def test_copy_composed_packs_rejects_escape_outside_packs_root(tmp_path: Path):
    packs_root = tmp_path / "packs"
    packs_root.mkdir()
    outside = tmp_path / "outside-pack"
    outside.mkdir()
    (outside / "marker.txt").write_text("nope\n", encoding="utf-8")

    pack_dir = packs_root / "composer-pack"
    pack_dir.mkdir()
    (pack_dir / "ggen.toml").write_text(
        '[packs]\nescaper = { path = "../../outside-pack" }\n', encoding="utf-8"
    )
    pack = Pack(
        name="composer-pack",
        version="0.1.0",
        description="test",
        path=pack_dir,
        ontologies=(),
        templates=(),
        native_gates=(),
        verifier_gates=(),
    )
    capsule = tmp_path / "capsule"
    capsule.mkdir()
    with pytest.raises(qp.QualificationContractError):
        qp.copy_composed_packs(pack, capsule)


def test_copy_composed_packs_rejects_nonexistent_sibling(tmp_path: Path):
    packs_root = tmp_path / "packs"
    packs_root.mkdir()
    pack_dir = packs_root / "composer-pack"
    pack_dir.mkdir()
    (pack_dir / "ggen.toml").write_text(
        '[packs]\nghost = { path = "../ghost-pack" }\n', encoding="utf-8"
    )
    pack = Pack(
        name="composer-pack",
        version="0.1.0",
        description="test",
        path=pack_dir,
        ontologies=(),
        templates=(),
        native_gates=(),
        verifier_gates=(),
    )
    capsule = tmp_path / "capsule"
    capsule.mkdir()
    with pytest.raises(qp.QualificationContractError):
        qp.copy_composed_packs(pack, capsule)


# --- shard -------------------------------------------------------------------


def test_shard_partitions_every_pack_into_exactly_one_shard(tmp_path: Path):
    packs = [make_pack(tmp_path, name=f"pack-{i}") for i in range(7)]
    count = 3
    shards = [qp.shard(packs, index, count) for index in range(count)]
    recombined = sorted((p.name for shard_list in shards for p in shard_list))
    assert recombined == sorted(p.name for p in packs)
    total = sum(len(shard_list) for shard_list in shards)
    assert total == len(packs)


def test_shard_is_deterministic_and_stable_by_position(tmp_path: Path):
    packs = [make_pack(tmp_path, name=f"pack-{i}") for i in range(5)]
    first = qp.shard(packs, 0, 2)
    second = qp.shard(packs, 0, 2)
    assert [p.name for p in first] == [p.name for p in second]


def test_shard_rejects_non_positive_count(tmp_path: Path):
    packs = [make_pack(tmp_path)]
    with pytest.raises(qp.QualificationContractError):
        qp.shard(packs, 0, 0)


def test_shard_rejects_index_out_of_range(tmp_path: Path):
    packs = [make_pack(tmp_path)]
    with pytest.raises(qp.QualificationContractError):
        qp.shard(packs, 2, 2)


# --- compact_output ------------------------------------------------------------


def test_compact_output_joins_nonempty_stderr_and_stdout():
    result = qp.CommandResult(returncode=1, stdout="out-line", stderr="err-line")
    assert qp.compact_output(result) == "err-line\nout-line"


def test_compact_output_truncates_to_last_3000_chars():
    long_stdout = "x" * 5000
    result = qp.CommandResult(returncode=0, stdout=long_stdout, stderr="")
    compacted = qp.compact_output(result)
    assert len(compacted) == 3000
    assert compacted == long_stdout[-3000:]


def test_compact_output_replaces_null_bytes():
    result = qp.CommandResult(returncode=0, stdout="a\x00b", stderr="")
    assert qp.compact_output(result) == "a<NUL>b"
