#!/usr/bin/env python3
from pathlib import Path
import tomllib

PACK = Path(__file__).resolve().parents[1]
config = tomllib.loads((PACK / "ggen.toml").read_text())
rules = {rule["name"]: rule for rule in config["generation"]["rules"]}
required_sparse = {
    "production-function-report",
    "consumer-factor-report",
    "consumer-realization-plan",
}
missing = sorted(required_sparse - rules.keys())
assert not missing, f"missing generation rules: {missing}"
violations = sorted(name for name in required_sparse if rules[name].get("skip_empty") is not True)
assert not violations, f"fixture-backed projection rules must skip empty canonical graphs: {violations}"
for name in sorted(required_sparse):
    rule = rules[name]
    assert rule.get("mode") == "Overwrite", (name, rule.get("mode"))
    assert rule.get("query", {}).get("file"), name
    assert rule.get("template", {}).get("file"), name
    assert rule.get("output_file"), name
print("R59_SPARSE_GENERATION_RULES=3")
print("R59_SPARSE_GENERATION_CONTRACT=ALIVE")
