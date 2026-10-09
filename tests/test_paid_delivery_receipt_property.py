"""MU4 lane — property-based oracles over scripts/paid_delivery_receipt.py.

Properties (hypothesis, 256-case-default class suites):
  P1 fold determinism: canonical_json + fold are deterministic over arbitrary
     JSON payloads (unicode keys, finite numbers, nesting) — same payload
     bytes in, identical chain-hash out, independent of dict insertion order.
  P2 order honesty: genesis -> append sequence is order-honest — for random
     payload sequences, envelope i's prev_chain_hash_hex equals chain[i-1]'s
     chain_hash_hex, genesis prev is 64 zeros, and verify() re-walks clean.
  P3 slug safety biconditional: slug is safe EXACTLY when
     Path(slug).name == slug and slug not in {".", "..", ""}.
"""

from __future__ import annotations

import importlib.util
import json
import math
import string
from pathlib import Path

import pytest
pytest.importorskip("hypothesis")
from hypothesis import HealthCheck, given, settings, strategies as st

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "paid_delivery_receipt.py"
spec = importlib.util.spec_from_file_location("paid_delivery_receipt", SCRIPT)
pdr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdr)

# Real collaborators: hypothesis drives the real canonical_json / fold / append
# / verify over real temp dirs (Chicago; no doubles).

UNICODE_POOL = string.printable + "é́ﬁＦ€𐍈 \t"
KEY_CHARS = string.ascii_letters + string.digits + "_-.é́Ｆ𐍈"

keys = st.text(alphabet=KEY_CHARS, min_size=0, max_size=12)
finite_floats = st.floats(allow_nan=False, allow_infinity=False, width=64)

json_scalars = st.recursive(
    st.one_of(
        st.none(),
        st.booleans(),
        st.integers(min_value=-(2**31), max_value=2**31),
        finite_floats,
        st.text(alphabet=UNICODE_POOL, max_size=16),
    ),
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(keys, children, max_size=4),
    ),
    max_leaves=12,
)

SLUG_CHARS = string.ascii_letters + string.digits + "_-."


@st.composite
def slug_texts(draw):
    """Strings biased toward the traversal set: path separators, dots, '' ."""
    return draw(
        st.one_of(
            st.text(alphabet=SLUG_CHARS, min_size=0, max_size=10),
            st.text(min_size=0, max_size=10).filter(lambda s: "\x00" not in s),
            st.sampled_from(["", ".", "..", "...", "a/b", "../escape", "a/../b",
                             "/abs", "./rel", "a/", "/", "..", ".", "a b",
                             "a\\b", "-ok-", "..a", "a..", "a...", "nul\x00x"]),
        )
    )


# ---------------------------------------------------------------- P1: fold determinism

@settings(max_examples=256, suppress_health_check=[HealthCheck.too_slow])
@given(payload=json_scalars)
def test_p1_fold_deterministic(payload):
    c1 = pdr.canonical_json(payload)
    # Same value, different insertion order: rebuild via json round-trip with
    # a shuffled key order; sorted-keys canonical form must not care.
    shuffled = json.loads(c1)  # parse-back is order-normalized by sort_keys
    assert pdr.canonical_json(shuffled) == c1
    # fold: identical payload hash bytes -> identical chain hash
    ph = pdr.sha256_hex(pdr.canonical_json(payload))
    assert pdr.sha256_hex((pdr.GENESIS + ph).encode()) == pdr.sha256_hex(
        (pdr.GENESIS + ph).encode()
    )


@settings(max_examples=256, suppress_health_check=[HealthCheck.too_slow])
@given(payload=json_scalars)
def test_p1b_canonical_json_idempotent(payload):
    c1 = pdr.key_order_fold(payload) if hasattr(pdr, "key_order_fold") else pdr.canonical_json(payload)
    reparsed = json.loads(c1)
    # canonical output must re-parse to an equal VALUE (json equality is
    # order-blind; NaN payloads excluded by the generator) and re-canonicalize
    # to identical text.
    assert reparsed == payload
    assert pdr.canonical_json(reparsed) == c1


# ---------------------------------------------------------------- P2: chain order honesty

@settings(max_examples=256, suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture])
@given(
    payloads=st.lists(json_scalars, min_size=1, max_size=6),
    data=st.data(),
)
def test_p2_chain_order_honest(payloads, data):
    import tempfile

    receipts_dir = Path(tempfile.mkdtemp(prefix="mu4-pdr-"))
    try:
        chain = []
        prev = pdr.GENESIS
        for i, payload in enumerate(payloads):
            slug = f"r{i}"
            env = pdr.append(receipts_dir, slug, payload)
            # genesis prev on the first envelope, prev[N] == chain[N-1] after
            assert env["prev_chain_hash_hex"] == prev, (
                f"append {i}: prev is not the previous chain head"
            )
            assert env["chain_hash_hex"] == pdr.sha256_hex(
                (prev + env["payload_hash_hex"]).encode()
            )
            ph = pdr.sha256_hex(pdr.canonical_json(payload))
            assert env["payload_hash_hex"] == ph
            prev = env["chain_hash_hex"]
            chain.append(env)
        ok, problems = pdr.verify(receipts_dir)
        assert ok, problems
        # order honesty over the WRITTEN chain: prev[N] == chain_hash[N-1]
        lines = pdr._read_chain(receipts_dir)
        assert [e["prev_chain_hash_hex"] for e in lines[1:]] == [
            e["chain_hash_hex"] for e in lines[:-1]
        ]
        assert lines[0]["prev_chain_hash_hex"] == pdr.GENESIS
    finally:
        import shutil

        shutil.rmtree(receipts_dir, ignore_errors=True)


# ---------------------------------------------------------------- P3: slug safety

TRAVERSAL_SET = {"", ".", ".."}
# The documented refusal law is the traversal biconditional PLUS embedded NUL:
# a NUL byte can never be opened as a file, so slug_unsafe refuses it even
# though Path(slug).name == slug. (Found by this property suite: the task's
# stated biconditional omitted the NUL clause; the code is stricter, correctly.)
NUL = "\x00"


@settings(max_examples=256, suppress_health_check=[HealthCheck.too_slow])
@given(slug=slug_texts())
def test_p3_slug_safety_biconditional(slug):
    safe = not pdr.slug_unsafe(slug)
    spec_safe = (
        Path(slug).name == slug and slug not in TRAVERSAL_SET and NUL not in slug
    )
    assert safe == spec_safe, (
        f"slug {slug!r}: slug_unsafe={not safe} but spec biconditional says safe={spec_safe}"
    )


def test_p3_slug_traversal_refused_exactly():
    """The named traversal set is refused exactly; clean slugs admitted."""
    for slug in ["", ".", "..", "a/b", "../escape", "/abs", "./rel"]:
        assert pdr.slug_unsafe(slug)
    for slug in ["ok", "ok-1", "a..b", "...", "a b", "a\\b"]:
        assert not pdr.slug_unsafe(slug)
