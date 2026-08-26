import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "finalize_project2_request.py"
spec = importlib.util.spec_from_file_location("ocel_digest_finalizer", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


def request_payload(digest=module.SENTINEL):
    return {
        "request_id": "cell1-run-ggen-ecosystem-ocel",
        "operation": "memory.upsert",
        "project": {"owner": "seanchatmangpt", "number": 2},
        "payload": {
            "record": {
                "key": "ggen/ecosystem/ocel/current",
                "body": f"Digest {digest}.",
                "metadata": {
                    "ocel_digest": digest,
                    "manufacturing_ladder": "U->G->O->Q->M",
                    "ggen_first": True,
                    "process_analysis_owner": "wasm4pm",
                },
            }
        },
    }


def write_fixture(tmp_path, request):
    ocel = tmp_path / "run.ocel.json"
    request_path = tmp_path / "request.json"
    ocel.write_bytes(b'{"ocel:events":{},"ocel:objects":{}}\n')
    request_path.write_text(json.dumps(request), encoding="utf-8")
    return ocel, request_path


def test_binds_exact_generated_ocel_bytes_without_mutating_them(tmp_path):
    ocel, request_path = write_fixture(tmp_path, request_payload())
    original = ocel.read_bytes()
    expected = "sha256:" + hashlib.sha256(original).hexdigest()

    assert module.finalize(ocel, request_path) == expected
    assert ocel.read_bytes() == original

    finalized = json.loads(request_path.read_text())
    assert finalized["payload"]["record"]["metadata"]["ocel_digest"] == expected
    assert expected in finalized["payload"]["record"]["body"]
    assert module.SENTINEL not in request_path.read_text()


def test_same_ocel_bytes_produce_same_digest(tmp_path):
    ocel_a, request_a = write_fixture(tmp_path / "a", request_payload())
    ocel_b, request_b = write_fixture(tmp_path / "b", request_payload())
    assert module.finalize(ocel_a, request_a) == module.finalize(ocel_b, request_b)


def test_refuses_prebound_or_fabricated_digest(tmp_path):
    ocel, request_path = write_fixture(tmp_path, request_payload("sha256:" + "0" * 64))
    with pytest.raises(ValueError, match="OCEL_DIGEST_SENTINEL_MISSING_OR_PREBOUND"):
        module.finalize(ocel, request_path)


def test_refuses_missing_body_binding(tmp_path):
    request = request_payload()
    request["payload"]["record"]["body"] = "No digest marker here."
    ocel, request_path = write_fixture(tmp_path, request)
    with pytest.raises(ValueError, match="OCEL_DIGEST_BINDING_INCOMPLETE"):
        module.finalize(ocel, request_path)


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("process_analysis_owner", "ggen", "PROCESS_ANALYSIS_OWNER_DRIFT"),
        ("ggen_first", False, "GGEN_FIRST_DRIFT"),
        ("manufacturing_ladder", "U->G->Q->M", "MANUFACTURING_LADDER_DRIFT"),
    ],
)
def test_refuses_control_contract_drift(tmp_path, field, value, reason):
    request = request_payload()
    request["payload"]["record"]["metadata"][field] = value
    ocel, request_path = write_fixture(tmp_path, request)
    with pytest.raises(ValueError, match=reason):
        module.finalize(ocel, request_path)
