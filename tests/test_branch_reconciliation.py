from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class BranchReconciliationTests(unittest.TestCase):
    def test_dsrust_v02_semantic_intent_is_present(self) -> None:
        pack = ROOT / "packs" / "dsrust-pack"
        manifest = (pack / "pack.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.2.0"', manifest)
        for required in (
            "enterprise.ttl",
            "execution.ttl",
            "gates/015_execution_policy.rq",
            "gates/020_enterprise_binding.rq",
            "qualification/consumer.ttl",
            "templates/dsrust_optimize.rs.tmpl",
            "templates/dsrust_parallel.rs.tmpl",
        ):
            self.assertTrue((pack / required).is_file(), required)

    def test_dsrust_consumer_code_is_injected_or_typed_refusal(self) -> None:
        pack = ROOT / "packs" / "dsrust-pack" / "templates"
        optimizer = (pack / "dsrust_optimize.rs.tmpl").read_text(encoding="utf-8")
        program = (pack / "dsrust_program.rs.tmpl").read_text(encoding="utf-8")
        forbidden_placeholder = "not " + "implemented"
        for text in (optimizer, program):
            self.assertNotIn(forbidden_placeholder, text.lower())
            self.assertNotIn('panic!("consumer-owned DsRust', text)
        self.assertIn("metric: MetricFn", optimizer)
        self.assertIn("feedback_metric: FeedbackMetricFn", optimizer)
        self.assertIn("REFUSED:CONSUMER_TOOL_BODY_REQUIRED", program)
        self.assertIn("REFUSED:CONSUMER_REWARD_REQUIRED", program)
        self.assertIn("build_module_with_rewards", program)

    def test_composite_action_keeps_frontmatter_and_executable_body(self) -> None:
        template = (
            ROOT
            / "packs"
            / "github-actions-pack"
            / "templates"
            / "composite_action.yml.tmpl"
        ).read_text(encoding="utf-8")
        self.assertTrue(template.startswith("---\n"))
        self.assertIn("for_each: actions", template)
        self.assertIn("runs:\n  using: composite\n  steps:", template)
        self.assertIn('steps | filter(attribute="actionDirName", value=actionDirName)', template)
        self.assertNotIn("sparql(query=", template)


if __name__ == "__main__":
    unittest.main()
