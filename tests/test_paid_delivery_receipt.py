"""Court for the paid-delivery receipt chain: append/verify round-trip, tamper
refusal naming the slug, out-of-order append refusal, determinism. Real files in
tmp_path; no mocks."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import scripts.paid_delivery_receipt as pdr


def payload(name: str) -> dict:
    return {
        "graph_hash": f"sha256:{name}",
        "outputs": {f"dist/{name}.yaml": "a" * 64},
        "consequence_sha256": "b" * 64,
        "packs": {"aaif-vanilla-pack": "c" * 64},
        "closure": {"declared": 3, "witnessed": 3},
        "monetization": {
            "billing_authority": "GOOGLE_CLOUD_MARKETPLACE",
            "entitlement_name": f"ent-{name}",
            "entitlement_state": "ACTIVE",
            "backend_standing": "PARTIAL_ALIVE",
            "plan": "enterprise",
            "unit_price_usd": 1000,
        },
        "actuation": {"target": "kind", "target_standing": "PARTIAL_ALIVE", "plan_digest": "d" * 64},
    }


def test_append_three_then_verify_ok(tmp_path: Path):
    for i in range(3):
        env = pdr.append(tmp_path, f"delivery-{i}", payload(f"p{i}"))
        assert env["schema"] == "ggen-receipt/v2"
        assert env["chain_rule"] == "paid-delivery-chain/v1"
        assert env["ts_ns"] == 0
        assert env["activity"] == "aaif.paid-delivery"
        assert len(env["payload_hash_hex"]) == 64
        assert len(env["chain_hash_hex"]) == 64
    chain = (tmp_path / "receipts" / "paid-delivery" / "chain.jsonl").read_text().splitlines()
    assert len(chain) == 3
    envs = [json.loads(l) for l in chain]
    assert envs[0]["prev_chain_hash_hex"] == "0" * 64
    assert envs[1]["prev_chain_hash_hex"] == envs[0]["chain_hash_hex"]
    assert envs[2]["prev_chain_hash_hex"] == envs[1]["chain_hash_hex"]
    for i in range(3):
        slug_file = tmp_path / "receipts" / "paid-delivery" / f"delivery-{i}.json"
        assert slug_file.is_file()
    ok, problems = pdr.verify(tmp_path)
    assert ok, problems
    assert problems == []


def test_tamper_middle_payload_fails_naming_slug(tmp_path: Path):
    for i in range(3):
        pdr.append(tmp_path, f"delivery-{i}", payload(f"p{i}"))
    chain_file = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    lines = chain_file.read_text().splitlines()
    env = json.loads(lines[1])
    env["payload"]["consequence_sha256"] = "f" * 64
    lines[1] = json.dumps(env, sort_keys=True, separators=(",", ":"))
    chain_file.write_text("\n".join(lines) + "\n")
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert any("delivery-1" in p and "PAYLOAD_HASH_MISMATCH" in p for p in problems)


def test_out_of_order_append_refused(tmp_path: Path):
    pdr.append(tmp_path, "delivery-0", payload("p0"))
    env1 = pdr.append(tmp_path, "delivery-1", payload("p1"))
    assert env1["prev_chain_hash_hex"] != "0" * 64
    chain_file = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    lines = chain_file.read_text().splitlines()
    # Drop the genesis line: delivery-1 now sits at position 0 claiming a prev
    # it cannot have — the out-of-order append shape.
    chain_file.write_text(lines[1] + "\n")
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert any("delivery-1" in p and "PREV_CHAIN_MISMATCH" in p for p in problems)
    # delivery-0 is off-chain, not corrupt — it produces no problem entry
    assert not any("delivery-0" in p for p in problems)


def test_same_payload_twice_identical_payload_hash(tmp_path: Path):
    p = payload("same")
    e1 = pdr.append(tmp_path / "a", "delivery", p)
    e2 = pdr.append(tmp_path / "b", "delivery", p)
    assert e1["payload_hash_hex"] == e2["payload_hash_hex"]
    assert e1["chain_hash_hex"] == e2["chain_hash_hex"]


def test_verify_empty_dir_ok(tmp_path: Path):
    ok, problems = pdr.verify(tmp_path)
    assert ok
    assert problems == []


def test_cli_append_and_verify(tmp_path: Path):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload("cli")))
    rc = pdr.main(["append", str(tmp_path), "delivery-cli", "--payload", str(payload_file)])
    assert rc == 0
    rc = pdr.main(["verify", str(tmp_path)])
    assert rc == 0
    env = json.loads(
        (tmp_path / "receipts" / "paid-delivery" / "chain.jsonl").read_text().splitlines()[0]
    )
    assert env["slug"] == "delivery-cli"


@pytest.mark.parametrize("n", [5])
def test_long_chain_verify_ok(tmp_path: Path, n: int):
    for i in range(n):
        pdr.append(tmp_path, f"d-{i}", payload(f"p{i}"))
    ok, problems = pdr.verify(tmp_path)
    assert ok, problems


# ---------------------------------------------------------------------------
# Slug safety (AE2 2b) + HEAD anchor (AE2 2 partial)
# ---------------------------------------------------------------------------

def test_traversal_slug_refused_at_append(tmp_path: Path):
    for bad in ("../escape", "a/b", "..", ".", ""):
        with pytest.raises(pdr.SlugUnsafe) as ei:
            pdr.append(tmp_path, bad, payload("x"))
        assert "REFUSED_SLUG_UNSAFE" in str(ei.value)
    # nothing written outside the receipts root
    assert not (tmp_path / "escape.json").exists()
    assert not (tmp_path / "receipts").exists() or not any(
        (tmp_path / "receipts").rglob("a.json")
    )


def test_cli_append_unsafe_slug_exit_2(tmp_path: Path):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload("cli")))
    rc = pdr.main(["append", str(tmp_path), "../evil", "--payload", str(payload_file)])
    assert rc == 2
    assert not (tmp_path.parent / "evil.json").exists()


def test_verify_flags_unsafe_slug_in_chain(tmp_path: Path):
    chain = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    chain.parent.mkdir(parents=True)
    env = json.loads(json.dumps({
        "schema": pdr.SCHEMA,
        "activity": pdr.ACTIVITY,
        "slug": "../evil",
        "ts_ns": 0,
        "payload": {},
        "payload_hash_hex": pdr.sha256_hex(pdr.canonical_json({})),
        "prev_chain_hash_hex": pdr.GENESIS,
        "chain_hash_hex": pdr.sha256_hex((pdr.GENESIS + pdr.sha256_hex(pdr.canonical_json({})))),
        "chain_rule": pdr.CHAIN_RULE,
    }))
    chain.write_text(pdr.canonical_json(env) + "\n", encoding="utf-8")
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert any("REFUSED_SLUG_UNSAFE" in p for p in problems)


def test_head_anchor_written_and_updated(tmp_path: Path):
    e1 = pdr.append(tmp_path, "d-0", payload("p0"))
    head = tmp_path / "receipts" / "paid-delivery" / "HEAD"
    assert head.is_file()
    assert head.read_text().strip() == e1["chain_hash_hex"]
    e2 = pdr.append(tmp_path, "d-1", payload("p1"))
    assert head.read_text().strip() == e2["chain_hash_hex"]
    assert e2["chain_hash_hex"] != e1["chain_hash_hex"]


def test_cli_append_echoes_head_anchor(tmp_path: Path, capsys):
    payload_file = tmp_path / "payload.json"
    payload_file.write_text(json.dumps(payload("cli")))
    rc = pdr.main(["append", str(tmp_path), "delivery-cli", "--payload", str(payload_file)])
    assert rc == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert out["head_anchor"] == str(
        tmp_path / "receipts" / "paid-delivery" / "HEAD"
    )


def test_verify_with_matching_anchor_ok(tmp_path: Path):
    e1 = pdr.append(tmp_path, "d-a0", payload("a0"))
    e2 = pdr.append(tmp_path, "d-a1", payload("a1"))
    ok, problems = pdr.verify(tmp_path, anchor_hash=e2["chain_hash_hex"])
    assert ok
    assert problems == []


def test_verify_with_stale_anchor_refused(tmp_path: Path):
    e1 = pdr.append(tmp_path, "d-s0", payload("s0"))
    pdr.append(tmp_path, "d-s1", payload("s1"))
    ok, problems = pdr.verify(tmp_path, anchor_hash=e1["chain_hash_hex"])
    assert not ok
    assert any(
        "REFUSED_ANCHOR_MISMATCH" in p
        and f"expected={e1['chain_hash_hex']}" in p
        for p in problems
    )


def test_verify_anchor_detects_tampered_chain(tmp_path: Path):
    # fully re-forged chain: every hash recomputed, so the internal fold is
    # self-consistent -- only the out-of-band anchor exposes the tampering.
    pdr.append(tmp_path, "d-t0", payload("original-0"))
    head = tmp_path / "receipts" / "paid-delivery" / "HEAD"
    good_head = head.read_text().strip()
    chain = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    env = json.loads(chain.read_text().splitlines()[0])
    env["payload"] = payload("tampered")
    env["payload_hash_hex"] = pdr.sha256_hex(pdr.canonical_json(env["payload"]))
    env["chain_hash_hex"] = pdr.sha256_hex(
        (env["prev_chain_hash_hex"] + env["payload_hash_hex"]).encode("utf-8")
    )
    chain.write_text(pdr.canonical_json(env) + "\n", encoding="utf-8")
    ok, problems = pdr.verify(tmp_path, anchor_hash=good_head)
    assert not ok
    assert any("REFUSED_ANCHOR_MISMATCH" in p for p in problems)


def test_verify_anchor_from_head_file_path(tmp_path: Path):
    pdr.append(tmp_path, "d-h", payload("h"))
    head = tmp_path / "receipts" / "paid-delivery" / "HEAD"
    ok, problems = pdr.verify(tmp_path, anchor_hash=head.read_text().strip())
    assert ok


def test_cli_verify_with_anchor_flag_hex(tmp_path: Path, capsys):
    p = tmp_path / "p.json"
    p.write_text(json.dumps(payload("cli-a")))
    env = pdr.append(tmp_path, "d-cli-a", payload("cli-a"))
    assert p.is_file()
    rc = pdr.main(["verify", str(tmp_path), "--anchor", env["chain_hash_hex"]])
    assert rc == 0
    assert "ALIVE" in capsys.readouterr().out


def test_cli_verify_with_anchor_flag_head_file(tmp_path: Path, capsys):
    pdr.append(tmp_path, "d-cli-h", payload("cli-h"))
    head = tmp_path / "receipts" / "paid-delivery" / "HEAD"
    rc = pdr.main(["verify", str(tmp_path), "--anchor", str(head)])
    assert rc == 0
    assert "ALIVE" in capsys.readouterr().out


def test_cli_verify_anchor_mismatch_exit_2(tmp_path: Path, capsys):
    e1 = pdr.append(tmp_path, "d-cli-m", payload("cli-m"))
    pdr.append(tmp_path, "d-cli-m2", payload("cli-m2"))
    rc = pdr.main(["verify", str(tmp_path), "--anchor", e1["chain_hash_hex"]])
    assert rc == 2
    assert "REFUSED_ANCHOR_MISMATCH" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Mutation-hardening courts (exact golden hashes, exact bytes, exact problems)
# ---------------------------------------------------------------------------

def _golden_payload_hash(payload: dict) -> str:
    """Independently computed: sha256 over sorted-keys/compact-separator JSON."""
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _golden_chain_hash(prev_hex: str, payload: dict) -> str:
    ph = _golden_payload_hash(payload)
    return hashlib.sha256((prev_hex + ph).encode("utf-8")).hexdigest()


def test_append_nested_dir_golden_hashes_exact_bytes(tmp_path: Path):
    # receipts_dir does not exist yet: parents must be created (mutants that
    # drop parents=True fail with FileNotFoundError here)
    receipts_dir = tmp_path / "deep" / "nested"
    p0 = payload("g0")
    env = pdr.append(receipts_dir, "d-g0", p0)
    assert env["prev_chain_hash_hex"] == "0" * 64
    assert env["payload_hash_hex"] == _golden_payload_hash(p0)
    assert env["chain_hash_hex"] == _golden_chain_hash("0" * 64, p0)
    # chain line is exact compact sorted JSON bytes with trailing newline
    chain_file = receipts_dir / "receipts" / "paid-delivery" / "chain.jsonl"
    line = chain_file.read_bytes().decode("utf-8")
    assert line == pdr.canonical_json(env) + "\n"
    # slug file is exact two-space-indent sorted JSON with trailing newline
    slug_file = receipts_dir / "receipts" / "paid-delivery" / "d-g0.json"
    assert slug_file.read_bytes().decode("utf-8") == (
        json.dumps(env, indent=2, sort_keys=True) + "\n"
    )
    head = receipts_dir / "receipts" / "paid-delivery" / "HEAD"
    assert head.read_bytes().decode("utf-8") == env["chain_hash_hex"] + "\n"


def test_slug_unsafe_nul_byte_refused(tmp_path: Path):
    with pytest.raises(pdr.SlugUnsafe) as ei:
        pdr.append(tmp_path, "a\x00b", payload("nul"))
    assert "REFUSED_SLUG_UNSAFE" in str(ei.value)


def _bad_env_min() -> dict:
    return {"schema": "other/v1", "chain_rule": "other", "ts_ns": 5}


def test_verify_problem_strings_exact(tmp_path: Path):
    chain = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    chain.parent.mkdir(parents=True)
    chain.write_text(pdr.canonical_json(_bad_env_min()) + "\n", encoding="utf-8")
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert problems == [
        "chain[0]:<missing>:REFUSED_MISSING_FIELD:payload_hash_hex",
        "chain[0]:<missing>:REFUSED_MISSING_FIELD:prev_chain_hash_hex",
        "chain[0]:<missing>:REFUSED_MISSING_FIELD:chain_hash_hex",
        "chain[0]:<missing>:REFUSED_MISSING_FIELD:payload",
        "chain[0]:<missing>:REFUSED_BAD_SCHEMA:other/v1",
        "chain[0]:<missing>:REFUSED_BAD_CHAIN_RULE:other",
        "chain[0]:<missing>:REFUSED_NONZERO_TS_NS",
        "chain[0]:<missing>:REFUSED_PREV_CHAIN_MISMATCH",
    ]


def test_verify_chain_fold_mismatch_exact_problems(tmp_path: Path):
    pdr.append(tmp_path, "d-0", payload("f0"))
    pdr.append(tmp_path, "d-1", payload("f1"))
    chain_file = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    lines = chain_file.read_text().splitlines()
    env0 = json.loads(lines[0])
    env0["chain_hash_hex"] = "e" * 64
    lines[0] = pdr.canonical_json(env0)
    chain_file.write_text("\n".join(lines) + "\n")
    ok, problems = pdr.fold = pdr.verify(tmp_path)
    assert not ok
    assert problems == [
        "chain[0]:d-0:REFUSED_CHAIN_FOLD_MISMATCH",
        "chain[1]:d-1:REFUSED_PREV_CHAIN_MISMATCH",
        "chain[0]:d-0:REFUSED_SLUG_FILE_DRIFT",
    ]


def test_verify_unsafe_slugs_continue_scanning(tmp_path: Path):
    chain = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    chain.parent.mkdir(parents=True)
    bad1 = {"slug": "../e0"}
    bad2 = {"slug": "../e1"}
    chain.write_text(
        pdr.canonical_json(bad1) + "\n" + pdr.canonical_json(b2 := bad2) + "\n",
        encoding="utf-8",
    )
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert problems == [
        "chain[0]:<unsafe>:REFUSED_SLUG_UNSAFE:../e0",
        "chain[1]:<unsafe>:REFUSED_SLUG_UNSAFE:../e1",
    ]


def test_verify_non_string_slug_valid_envelope_ok(tmp_path: Path):
    # slug key present but not a string: never build a path from it
    env = {
        "schema": pdr.SCHEMA,
        "activity": pdr.ACTIVITY,
        "slug": 123,
        "ts_ns": 0,
        "payload": {"x": 1},
        "payload_hash_hex": _golden_payload_hash({"x": 1}),
        "prev_chain_hash_hex": pdr.GENESIS,
        "chain_hash_hex": _golden_chain_hash(pdr.GENESIS, {"x": 1}),
        "chain_rule": pdr.CHAIN_RULE,
    }
    chain = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    chain.parent.mkdir(parents=True)
    chain.write_text(pdr.canonical_json(env) + "\n", encoding="utf-8")
    ok, problems = pdr.verify(tmp_path)
    assert ok, problems
    assert problems == []


def test_verify_missing_slug_file_exact_problem(tmp_path: Path):
    pdr.append(tmp_path, "d-0", payload("m0"))
    pdr.append(tmp_path, "d-1", payload("m1"))
    d = tmp_path / "receipts" / "paid-delivery"
    (d / "d-0.json").unlink()
    (d / "d-1.json").unlink()
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert problems == [
        "chain[0]:d-0:REFUSED_MISSING_SLUG_FILE",
        "chain[1]:d-1:REFUSED_MISSING_SLUG_FILE",
    ]


def test_verify_unsafe_then_safe_missing_file(tmp_path: Path):
    pdr.append(tmp_path, "d-1", payload("u1"))
    chain_file = tmp_path / "receipts" / "paid-delivery" / "chain.jsonl"
    lines = chain_file.read_text().splitlines()
    unsafe = {"slug": "../e0"}
    chain_file.write_text(
        pdr.canonical_json(unsafe) + "\n" + lines[0] + "\n", encoding="utf-8"
    )
    (tmp_path / "receipts" / "paid-delivery" / "d-1.json").unlink()
    ok, problems = pdr.verify(tmp_path)
    assert not ok
    assert problems == [
        "chain[0]:<unsafe>:REFUSED_SLUG_UNSAFE:../e0",
        "chain[1]:d-1:REFUSED_MISSING_SLUG_FILE",
    ]


# ---------------------------------------------------------------------------
# CLI mutation-hardening courts
# ---------------------------------------------------------------------------

def test_cli_help_texts_exact(tmp_path: Path, capsys):
    with pytest.raises(SystemExit) as ei:
        pdr.main(["--help"])
    assert ei.value.code == 0
    out = capsys.readouterr().out
    assert re.search(r"Paid-delivery receipt chain \(append/verify\)\.(?!X)", out)
    assert re.search(r"append a receipt from a JSON payload file(?!X)", out)
    assert re.search(r"verify the whole chain(?!X)", out)
    with pytest.raises(SystemExit) as ei:
        pdr.main(["append", "--help"])
    assert ei.value.code == 0
    out = capsys.readouterr().out
    assert re.search(r"path to payload JSON file(?!X)", out)
    with pytest.raises(SystemExit) as ei:
        pdr.main(["verify", "--help"])
    assert ei.value.code == 0
    out = capsys.readouterr().out
    assert re.search(r"expected final chain hash: raw hex, or path to a HEAD file(?!X)", out)


def test_cli_missing_arguments_exit_2(tmp_path: Path, capsys):
    with pytest.raises(SystemExit) as ei:
        pdr.main([])
    assert ei.value.code == 2
    capsys.readouterr()
    with pytest.raises(SystemExit) as ei:
        pdr.main(["append", str(tmp_path), "d-x"])  # no --payload
    assert ei.value.code == 2
    capsys.readouterr()


def test_cli_append_output_exact(tmp_path: Path, capsys):
    p = tmp_path / "payload.json"
    p.write_text(json.dumps(payload("gold")))
    rc = pdr.main(["append", str(tmp_path), "d-gold", "--payload", str(p)])
    assert rc == 0
    out = capsys.readouterr().out
    got = json.loads(out.strip())
    assert got == {
        "chain_hash_hex": _golden_chain_hash("0" * 64, payload("gold")),
        "slug": "d-gold",
        "head_anchor": str(tmp_path / "receipts" / "paid-delivery" / "HEAD"),
    }


def test_cli_append_unsafe_slug_stderr_exact(tmp_path: Path, capsys):
    p = tmp_path / "payload.json"
    p.write_text(json.dumps(payload("x")))
    rc = pdr.main(["append", str(tmp_path), "../evil", "--payload", str(p)])
    assert rc == 2
    captured = capsys.readouterr()
    assert captured.err.strip() == "REFUSED_SLUG_UNSAFE:'../evil'"
    assert captured.out == ""


def test_cli_alive_line_exact(tmp_path: Path, capsys):
    p = tmp_path / "payload.json"
    p.write_text(json.dumps(payload("alive")))
    pdr.main(["append", str(tmp_path), "d-alive", "--payload", str(p)])
    capsys.readouterr()
    rc = pdr.main(["verify", str(tmp_path)])
    assert rc == 0
    assert capsys.readouterr().out.strip() == "ALIVE: paid-delivery chain verified"


def test_cli_verify_anchor_hex_literal_not_read_as_file(tmp_path: Path, capsys, monkeypatch):
    p = tmp_path / "payload.json"
    p.write_text(json.dumps(payload("anch")))
    env = pdr.append(tmp_path, "d-anch", payload("anch"))
    # a file whose NAME is a valid 64-hex literal must not be consulted when
    # the anchor argument is itself valid hex
    decoy_name = "A" * 64  # uppercase hex defeats a lowercase-only alphabet mutant
    (tmp_path / decoy_name).write_text("b" * 64)
    monkeypatch.chdir(tmp_path)
    rc = pdr.main(["verify", str(tmp_path), "--anchor", decoy_name])
    captured = capsys.readouterr()
    assert rc == 2
    assert f"expected={decoy_name.lower()}" in captured.err
    assert "b" * 64 not in captured.err
    assert env["chain_hash_hex"]  # keeps env used
    # and the lowercase mirror: a lowercase hex anchor must also stay a
    # literal even when a same-named decoy file exists (kills an
    # uppercase-only hex-alphabet mutant)
    lower_decoy = "a" * 64
    (tmp_path / lower_decoy).write_text("c" * 64)
    rc = pdr.main(["verify", str(tmp_path), "--anchor", lower_decoy])
    captured = capsys.readouterr()
    assert rc == 2
    assert f"expected={lower_decoy}" in captured.err
    assert "c" * 64 not in captured.err


def test_cli_verify_anchor_short_hex_reads_named_file(tmp_path: Path, capsys, monkeypatch):
    pdr.append(tmp_path, "d-s", payload("s"))
    (tmp_path / "abc").write_text("b" * 64)
    monkeypatch.chdir(tmp_path)
    rc = pdr.main(["verify", str(tmp_path), "--anchor", "abc"])
    captured = capsys.readouterr()
    assert rc == 2
    assert f"expected={'b' * 64}" in captured.err


def test_cli_verify_anchor_x_name_reads_file(tmp_path: Path, capsys, monkeypatch):
    pdr.append(tmp_path, "d-x", payload("x"))
    (tmp_path / ("X" * 64)).write_text("b" * 64)
    monkeypatch.chdir(tmp_path)
    rc = pdr.main(["verify --anchor".split()[0], str(tmp_path), "--anchor", "X" * 64])
    captured = capsys.readouterr()
    assert rc == 2
    assert f"expected={'b' * 64}" in captured.err


def test_cli_verify_stale_head_file_anchor_refused(tmp_path: Path, capsys):
    e1 = pdr.append(tmp_path, "d-c0", payload("c0"))
    head = tmp_path / "receipts" / "paid-delivery" / "HEAD"
    head.write_text("9" * 64 + "\n")
    rc = pdr.main(["verify", str(tmp_path), "--anchor", str(head)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "REFUSED_ANCHOR_MISMATCH" in captured.err
    assert f"expected={'9' * 64}" in captured.err
    assert e1["chain_hash_hex"]


def test_cli_verify_anchor_stale_hex_mismatch_stderr(tmp_path: Path, capsys):
    e1 = pdr.append(tmp_path, "d-m0", payload("m0"))
    pdr.append(tmp_path, "d-m1", payload("m1"))
    rc = pdr.main(["verify", str(tmp_path), "--anchor", e1["chain_hash_hex"]])
    captured = capsys.readouterr()
    assert rc == 2
    assert f"expected={e1['chain_hash_hex']}" in captured.err
    assert ",actual=" in captured.err
