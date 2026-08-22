import json
import sys
import unittest
from pathlib import Path

PACK_DIR = Path(__file__).resolve().parents[1]
SCRIPT_DIR = PACK_DIR / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from public_projection_adapter import (  # noqa: E402
    AdmissionError,
    assert_public_semantic_graph,
    build_manifest,
    parse_legacy_render_hints,
)

GOOD = '''@prefix xar: <https://ggen.io/ontology/xaas-ash-render#> .
@prefix pcc: <https://seanchatmangpt.github.io/chatman-ecosystem/ontology/platform-console-capabilities#> .
xar:B a xar:RenderTarget ; xar:renderOf pcc:B ; xar:moduleName "B" ; xar:domainModule "Xaas.Billing" ; xar:actionName "bill" ; skos:closeMatch togaf:Capability .
xar:A a xar:RenderTarget ; xar:renderOf pcc:A ; xar:moduleName "A" ; xar:domainModule "Xaas.Platform" ; xar:actionName "read" ; skos:closeMatch togaf:Capability .
'''


class AdapterTest(unittest.TestCase):
    def test_manifest_is_deterministic_and_sorted(self):
        first = build_manifest(GOOD)
        second = build_manifest(GOOD)
        self.assertEqual(first, second)
        self.assertEqual(
            [target["capability"].split("#")[-1] for target in first["targets"]],
            ["A", "B"],
        )
        self.assertEqual(len(first["receipt_sha256"]), 64)
        self.assertEqual(first["authority"], "CONSTRUCT_ONLY")

    def test_exact_pack_ontology_projects_all_44_targets(self):
        manifest = build_manifest((PACK_DIR / "ontology.ttl").read_text())
        self.assertEqual(len(manifest["targets"]), 44)
        self.assertEqual(len({target["capability"] for target in manifest["targets"]}), 44)
        self.assertTrue(all(target["capability"].startswith("https://seanchatmangpt.github.io/chatman-ecosystem/ontology/platform-console-capabilities#") for target in manifest["targets"]))

    def test_missing_fact_refused(self):
        broken = GOOD.replace(' ; xar:actionName "bill"', '')
        with self.assertRaisesRegex(AdmissionError, "REFUSED_RENDER_HINT_CARDINALITY"):
            parse_legacy_render_hints(broken)

    def test_duplicate_capability_refused(self):
        duplicate = GOOD.replace("pcc:B", "pcc:A")
        with self.assertRaisesRegex(AdmissionError, "REFUSED_DUPLICATE_CAPABILITY"):
            parse_legacy_render_hints(duplicate)

    def test_public_graph_rejects_private_render_vocab(self):
        with self.assertRaisesRegex(AdmissionError, "REFUSED_PRIVATE_RENDER_VOCAB"):
            assert_public_semantic_graph(GOOD)

        assert_public_semantic_graph(
            '@prefix skos: <http://www.w3.org/2004/02/skos/core#> . '
            '<urn:a> skos:prefLabel "A" .'
        )

    def test_manifest_is_data_only(self):
        encoded = json.dumps(build_manifest(GOOD))
        for forbidden in ("subprocess", "os.system", "requests", "actuate", "broker.do"):
            self.assertNotIn(forbidden, encoded)


if __name__ == "__main__":
    unittest.main()
