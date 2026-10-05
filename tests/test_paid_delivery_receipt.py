"""Court for the paid-delivery receipt chain: append/verify round-trip, tamper
refusal naming the slug, out-of-order append refusal, determinism. Real files in
tmp_path; no mocks."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import paid_delivery_receipt as pdr


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
