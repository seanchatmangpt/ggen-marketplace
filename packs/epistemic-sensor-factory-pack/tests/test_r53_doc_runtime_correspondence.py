from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    how_to = (ROOT / "docs" / "r53-how-to.md").read_text()
    # The court that executes these commands lives in the CI court index (ci/courts.json).
    workflow = (ROOT.parents[1] / "ci" / "courts" / "measure-r53-causal-propagation.sh").read_text()
    static_cmd = "python3 packs/epistemic-sensor-factory-pack/tests/test_r53_static_contract.py"
    rdf_cmd = "python3 packs/epistemic-sensor-factory-pack/tests/test_r53_causal_propagation.py"
    assert static_cmd in how_to and static_cmd in workflow
    assert rdf_cmd in how_to and rdf_cmd in workflow
    assert "python3 -m pytest" not in how_to
    print("R53 documentation/runtime correspondence: PASS")


if __name__ == "__main__":
    main()
