from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

PACK = Path(__file__).parents[1] / "packs" / "challenger-value-framing-pack"
SPEC = spec_from_file_location("challenger_value_court", PACK / "reference" / "python" / "court.py")
assert SPEC and SPEC.loader
MOD = module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


def test_conformance_vectors():
    assert MOD.run_vectors(PACK / "vectors" / "conformance.json") == 0
