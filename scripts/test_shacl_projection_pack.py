#!/usr/bin/env python3
"""Chicago-style tests for shacl-projection-pack zod / JSON Schema targets.

Real ggen, real pack, real files; assertions on generated state. No doubles.
"""
import importlib.util, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import marketplace as m  # noqa: E402
import qualify_packs as q  # noqa: E402

PACK = ROOT / "packs" / "shacl-projection-pack"
ZOD, JSONS = "src/shacl_zod_schemas.ts", "schemas/shacl_projection.schema.json"


def pack_obj():
    packs, _ = m.inspect_marketplace()
    return next(p for p in packs if p.name == "shacl-projection-pack")


def generate(consumer_ttl: str) -> dict[str, str]:
    root = Path(tempfile.mkdtemp())
    try:
        consumer = root / "consumer"
        q.write_projection_consumer(pack_obj(), consumer)
        (consumer / "ontology.ttl").write_text(consumer_ttl, encoding="utf-8")
        r = subprocess.run(["ggen", "sync", "run"], cwd=consumer, capture_output=True, text=True, timeout=110)
        if r.returncode != 0:
            raise AssertionError(r.stdout + r.stderr)
        return {k: (consumer / k).read_text() for k in (ZOD, JSONS)}
    finally:
        shutil.rmtree(root, ignore_errors=True)


TTL = (PACK / "qualification" / "consumer.ttl").read_text()


class Targets(unittest.TestCase):
    def test_qualification_consumer_regenerates_both_targets(self):
        out = generate(TTL)
        self.assertIn("z.number().int()", out[ZOD])
        self.assertIn("export const WidgetSchema", out[ZOD])
        doc = json.loads(out[JSONS])
        self.assertEqual(doc["$schema"], "https://json-schema.org/draft/2020-12/schema")
        w = doc["$defs"]["Widget"]
        self.assertEqual(w["properties"]["count"], {"type": "integer"})
        self.assertEqual(sorted(w["required"]), ["active", "count", "name"])

    def test_mutation_rename_individual_changes_only_that_name(self):
        base = generate(TTL)
        mut = generate(TTL.replace('"Widget"', '"Gadget"'))
        self.assertEqual(mut[ZOD], base[ZOD].replace("Widget", "Gadget"))
        self.assertEqual(json.loads(mut[JSONS]), json.loads(base[JSONS].replace("Widget", "Gadget")))

    def test_mutation_rename_property_changes_only_that_field(self):
        base = generate(TTL)
        mut = generate(TTL.replace("ex:count", "ex:tally"))
        self.assertEqual(sorted(mut[ZOD].replace("tally", "count").splitlines()), sorted(base[ZOD].splitlines()))
        self.assertIn("tally: z.number().int()", mut[ZOD])

    def test_literal_scan_gate_clean_and_detects(self):
        spec = importlib.util.spec_from_file_location("g", PACK / "gates" / "030_literal_scan.py")
        g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
        self.assertEqual(g.scan(PACK), [])
        tmp = Path(tempfile.mkdtemp())
        try:
            (tmp / "templates").mkdir()
            (tmp / "templates" / "x.tmpl").write_text("import zcode\n")
            self.assertEqual(len(g.scan(tmp)), 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class TargetsTable(unittest.TestCase):
    def test_backfilled_packs_declare_languages(self):
        for name in ("process-intelligence-pack", "state-transition-pack", "evidence-standing-pack", "shacl-projection-pack", "gdmcp-pack"):
            self.assertTrue((ROOT / "packs" / name / "targets.toml").is_file(), name)
        self.assertEqual(pack_obj().target_languages, ("ts", "json-schema"))


if __name__ == "__main__":
    unittest.main()
