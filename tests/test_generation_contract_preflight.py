from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / "scripts" / "check-generation-contracts.py"
spec = spec_from_file_location("generation_contract_preflight", SCRIPT)
module = module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


class GenerationContractPreflightTest(unittest.TestCase):
    def _pack(self, query: str, template: str) -> Path:
        temp = Path(tempfile.mkdtemp())
        pack = temp / "pack"
        (pack / "queries").mkdir(parents=True)
        (pack / "templates").mkdir()
        (pack / "ggen.toml").write_text("""[generation]\noutput_dir = \".\"\n\n[[generation.rules]]\nname = \"projection\"\nquery = { file = \"queries/q.rq\" }\ntemplate = { file = \"templates/t.tera\" }\noutput_file = \"out.json\"\n""")
        (pack / "queries" / "q.rq").write_text(query)
        (pack / "templates" / "t.tera").write_text(template)
        return pack

    def test_accepts_ordered_results_contract(self):
        pack = self._pack("SELECT ?x WHERE { ?s ?p ?x } ORDER BY ?x\n", "{% for row in results %}{{ row.x }}{% endfor %}\n")
        self.assertEqual(module.inspect_pack(pack), [])

    def test_refuses_unordered_select_and_legacy_rows(self):
        pack = self._pack("SELECT ?x WHERE { ?s ?p ?x }\n", "{% for row in rows %}{{ row.x }}{% endfor %}\n")
        failures = module.inspect_pack(pack)
        self.assertTrue(any("lacks ORDER BY" in failure for failure in failures))
        self.assertTrue(any("legacy rows context" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main()
