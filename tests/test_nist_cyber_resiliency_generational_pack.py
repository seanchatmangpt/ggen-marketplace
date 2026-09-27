from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "nist-cyber-resiliency-generational-pack"

TECHNIQUES = (
    "AdaptiveResponse", "AnalyticMonitoring", "ContextualAwareness",
    "CoordinatedProtection", "Deception", "Diversity", "DynamicPositioning",
    "NonPersistence", "PrivilegeRestriction", "Realignment", "Redundancy",
    "Segmentation", "SubstantiatedIntegrity", "Unpredictability",
)


class NistCyberResiliencyGenerationalPackCourt(unittest.TestCase):
    def test_pack_has_canonical_semantic_surface(self):
        self.assertTrue((PACK / "pack.toml").is_file())
        self.assertTrue((PACK / "README.md").is_file())
        self.assertTrue((PACK / "ontology.ttl").is_file())
        self.assertEqual(len(list((PACK / "gates").glob("*.rq"))), 15)
        self.assertEqual(len(list((PACK / "queries").glob("*.rq"))), 3)

    def test_all_fourteen_nist_techniques_are_source_bound(self):
        text = (PACK / "ontology.ttl").read_text()
        for technique in TECHNIQUES:
            pattern = rf"cr:{technique}\s+a\s+cr:NISTDerivedTechnique\s*;.*?prov:wasDerivedFrom\s+cr:NIST_SP_800_160_V2R1"
            self.assertRegex(text, re.compile(pattern, re.S), technique)

    def test_generational_extensions_are_not_claimed_as_nist(self):
        text = (PACK / "ontology.ttl").read_text()
        for extension in ("GenerationalRemanufacture", "ImplementationNonInheritance", "ZeroCompatibilityObligation"):
            block = re.search(rf"cr:{extension}\s+a\s+cr:ArchitectureExtensionPattern\s*;(.*?\.)", text, re.S)
            self.assertIsNotNone(block, extension)
            self.assertIn("cr:sourceKind cr:MarketplaceExtension", block.group(1))
            self.assertIn("prov:wasDerivedFrom cr:MarketplaceGenerationalProfileSource", block.group(1))
            self.assertNotIn("cr:NISTDerived", block.group(1))

    def test_private_generative_law_is_not_published(self):
        corpus = "\n".join(p.read_text() for p in PACK.rglob("*") if p.is_file())
        for token in ("Chatman Equation", "Chatman Equilibrium", "A = μ", "A=μ"):
            self.assertNotIn(token, corpus)

    def test_non_inheritance_and_zero_compatibility_are_explicit_refusals(self):
        gate = (PACK / "gates" / "02_zero_implementation_inheritance.rq").read_text()
        self.assertIn("cr:inheritsImplementation false", gate)
        self.assertIn("cr:compatibilityObligation false", gate)

    def test_redundancy_keeps_intrinsic_resource_cost_visible(self):
        text = (PACK / "ontology.ttl").read_text()
        self.assertRegex(text, re.compile(r"cr:CostRedundancy.*?cr:costClass\s+cr:IntrinsicResourceCost", re.S))


if __name__ == "__main__":
    unittest.main()
