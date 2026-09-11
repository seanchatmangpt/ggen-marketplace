import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hosted_startup_failure_is_wrapper_andon_not_semantic_refusal():
    observations = json.loads((ROOT / "fixtures/hosted-startup-observations.json").read_text())
    assert {x["repo"] for x in observations} == {"pm4wasm", "a2a-rs"}
    assert all(x["standing"] == "BUILD_BROKEN[HOSTED_ACTIONS_STARTUP_FAILURE]" for x in observations)
    assert all(x["semantic_subject_present"] is True for x in observations)
    assert all(x["hosted_wrapper_required_for_semantic_standing"] is False for x in observations)


def test_startup_andon_preserves_exact_subject_identity():
    observations = json.loads((ROOT / "fixtures/hosted-startup-observations.json").read_text())
    heads = {x["repo"]: x["consumer_head"] for x in observations}
    assert heads["pm4wasm"] == "7f32a77fa5e84f2038b3c18beca570ad90b58566"
    assert heads["a2a-rs"] == "eac59d1a89896d05ef0c28751d95a415c6a93749"
