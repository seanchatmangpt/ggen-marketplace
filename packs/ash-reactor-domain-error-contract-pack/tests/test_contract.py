import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class ReactorDomainErrorCourt(unittest.TestCase):
    def test_template_preserves_run_step_domain_error(self):
        text = (ROOT / "templates" / "domain_error_normalizer.ex.tmpl").read_text()
        self.assertIn("Reactor.Error.Invalid.RunStepError", text)
        self.assertIn("error: error", text)
        self.assertIn("error -> error", text)
        self.assertIn("Generated.ReactorDomainErrorNormalizer", text)

    def test_template_refuses_unavailable_row_context(self):
        text = (ROOT / "templates" / "domain_error_normalizer.ex.tmpl").read_text()
        self.assertNotIn("row.", text)

    def test_pack_has_no_do_authority(self):
        text = (ROOT / "pack.toml").read_text()
        self.assertIn('authority = "VERIFY|CONSTRUCT"', text)
        self.assertIn("consequential_do = false", text)

    def test_failure_is_grounded_in_consumer_receipt(self):
        text = (ROOT / "ontology.ttl").read_text()
        self.assertIn("seanchatmangpt/xaas/pull/32", text)
        self.assertIn("idempotency_conflict", text)

    def test_generation_rule_uses_admitted_template_surface(self):
        text = (ROOT / "ggen.toml").read_text()
        self.assertIn('template = { file = "templates/domain_error_normalizer.ex.tmpl" }', text)

if __name__ == "__main__":
    unittest.main()
