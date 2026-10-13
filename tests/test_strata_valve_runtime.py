"""Strata valve refusal runtime court: the generated refusals.ex compiles warning-free under a
real elixirc and every refusal class emits a fixed 32-byte opaque receipt at runtime.

Chicago style, no mocks: a real `elixirc` compiles the real generated module and a real
`elixir` subprocess executes a harness that prints KEY=VALUE observations. The sabotage twin
mutates @receipt_len in a temp copy and re-runs the same court to prove the court can fail.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "packs" / "strata-valve-pack" / "generated" / "refusals.ex"
CLASSES = ["ArenaFailure", "FuelExhausted", "MalformedFrame", "ParentDiscontinuity"]
MODULE = "Strata.Valve.Refusals"

HARNESS = r"""
receipt_len = Strata.Valve.Refusals.receipt_len()
IO.puts("RECEIPT_LEN=" <> to_string(receipt_len))
for mod <- Strata.Valve.Refusals.classes() do
  {:refuse, bin} = apply(mod, :refuse, [:x])
  {:refuse, bin2} = apply(mod, :refuse, [:x])
  name = mod |> Module.split() |> List.last() |> String.upcase()
  IO.puts("REFUSE_#{name}_SIZE=" <> to_string(byte_size(bin)))
  IO.puts("REFUSE_#{name}_HEX=0x" <> Base.encode16(bin, case: :lower))
  IO.puts("REFUSE_#{name}_NONZERO=" <> to_string(bin != :binary.copy(<<0>>, 32)))
  IO.puts("REFUSE_#{name}_DET=" <> to_string(bin == bin2))
end
seed = {:frame, <<1, 2, 3>>}
digests = for mod <- Strata.Valve.Refusals.classes(), {:refuse, b} = apply(mod, :refuse, [seed]), do: b
IO.puts("REFUSE_DISTINCT=" <> to_string(length(Enum.uniq(digests)) == length(digests)))
doc =
  case Code.fetch_docs(Strata.Valve.Refusals.MalformedFrame) do
    {:docs_v1, _, _, _, %{"en" => d}, _, _} -> d
    _ -> ""
  end
IO.puts("MODULEDOC_HAS_32BYTE=" <> to_string(String.contains?(doc, "32-byte receipt")))
IO.puts("MODULEDOC_HAS_SHA256=" <> to_string(String.contains?(doc, "SHA-256")))
"""

# Cross-language parity fixture: the SAME 32-byte hexes pinned by the Rust
# in-test port in affidavit-core/tests/strata_refusal_seam.rs (seed
# "seam-29-l26"). Both implementations derive
# sha256(class_label <> 0x00 <> term_to_binary(seed)); this court proves the
# real Elixir modules produce byte-identical receipts.
PARITY_SEED = "seam-29-l26"
PARITY_SEED_LABEL = "PARITYSEED"  # printed via String.upcase in the harness
PARITY_HEXES = {
    "ARENAFAILURE": "68384c704cf1b757df5ef4a59c831460bd275b2b78b772089a49f5cad0d60b01",
    "FUELEXHAUSTED": "cbc0de1a5255cc1000333422ef2ac613fec4a601627c07b1afa4aa22e548e23a",
    "MALFORMEDFRAME": "91d5817e6a7e8753e62b815b4caa54939bfa876bc48c251974665969438faf18",
    "PARENTDISCONTINUITY": "48368e7b176a54cd8213caada897754e2d1b2ee536eed1b36c7355230477984a",
}

HARNESS += r"""
# Cross-language parity leg: same seed as affidavit-core/tests/strata_refusal_seam.rs.
for mod <- Strata.Valve.Refusals.classes() do
  {:refuse, bin} = apply(mod, :refuse, ["seam-29-l26"])
  name = mod |> Module.split() |> List.last() |> String.upcase()
  IO.puts("#{name}_SEAM29_L26=" <> Base.encode16(bin, case: :upper))
end
# Tamper negatives: changed seed and changed class must both change the receipt.
{:refuse, base} = Strata.Valve.Refusals.MalformedFrame.refuse("seam-29-l26")
{:refuse, other_seed} = Strata.Valve.Refusals.MalformedFrame.refuse("seam-29-l27")
{:refuse, other_class} = Strata.Valve.Refusals.FuelExhausted.refuse("seam-29-l26")
IO.puts("TAMPER_SEED_CHANGES=" <> to_string(base != other_seed))
IO.puts("TAMPER_CLASS_CHANGES=" <> to_string(base != other_class))
IO.puts("SEED_DET=" <> to_string(base == elem(Strata.Valve.Refusals.MalformedFrame.refuse("seam-29-l26"), 1)))
"""


def have(*tools: str) -> bool:
    return all(shutil.which(t) for t in tools)


def run_court(src: Path) -> dict[str, str]:
    """Compile src with real elixirc and run the real harness; return KEY=VALUE observations.
    Raises AssertionError with the compiler stderr if compilation warns or fails."""
    tmp = tempfile.TemporaryDirectory()
    work = Path(tmp.name)
    ebin = work / "ebin"
    ebin.mkdir()
    c = subprocess.run(["elixirc", "-o", str(ebin), str(src)], capture_output=True, text=True)
    assert c.returncode == 0, (c.stdout + c.stderr)[-1200:]
    assert c.stderr.strip() == "", f"elixirc emitted warnings:\n{c.stderr[-1200:]}"
    harness = work / "harness.exs"
    harness.write_text(HARNESS, encoding="utf-8")
    r = subprocess.run(["elixir", "-pa", str(ebin), str(harness)],
                       capture_output=True, text=True, cwd=work)
    assert r.returncode == 0, (r.stdout + r.stderr)[-1200:]
    obs = {m.group(1): m.group(2)
           for m in map(re.compile(r"^([A-Z_0-9]+)=(.*)$").match, r.stdout.splitlines()) if m}
    assert obs, f"harness produced no observations:\n{(r.stdout + r.stderr)[-1200:]}"
    return obs


def violations(obs: dict[str, str]) -> list[str]:
    """The court: every way the observations deviate from the refusal contract."""
    bad: list[str] = []
    if obs.get("RECEIPT_LEN") != "32":
        bad.append(f"RECEIPT_LEN={obs.get('RECEIPT_LEN')!r} != '32'")
    for cls in CLASSES:
        key = f"REFUSE_{cls.upper()}_SIZE"
        if obs.get(key) != "32":
            bad.append(f"{key}={obs.get(key)!r} != '32'")
        for prop in ("NONZERO", "DET"):
            k = f"REFUSE_{cls.upper()}_{prop}"
            if obs.get(k) != "true":
                bad.append(f"{k}={obs.get(k)!r} != 'true'")
        if obs.get(f"REFUSE_{cls.upper()}_HEX", "").startswith("0x00"):
            bad.append(f"REFUSE_{cls.upper()}_HEX begins with 00 — zero receipt")
    if obs.get("REFUSE_DISTINCT") != "true":
        bad.append(f"REFUSE_DISTINCT={obs.get('REFUSE_DISTINCT')!r} != 'true'")
    if obs.get("MODULEDOC_HAS_32BYTE") != "true":
        bad.append(f"MODULEDOC_HAS_32BYTE={obs.get('MODULEDOC_HAS_32BYTE')!r} != 'true'")
    if obs.get("MODULEDOC_HAS_SHA256") != "true":
        bad.append(f"MODULEDOC_HAS_SHA256={obs.get('MODULEDOC_HAS_SHA256')!r} != 'true'")
    for cls, hex_ in PARITY_HEXES.items():
        k = f"{cls}_SEAM29_L26"
        if (obs.get(k) or "").lower() != hex_.lower():
            bad.append(f"PARITY {k}={obs.get(k, '')!r} != pinned {hex_} (Elixir vs Rust divergence)")
    for k in ("TAMPER_SEED_CHANGES", "TAMPER_CLASS_CHANGES", "SEED_DET"):
        if obs.get(k) != "true":
            bad.append(f"{k}={obs.get(k)!r} != 'true'")
    return bad


@unittest.skipUnless(have("elixir", "elixirc"), "BLOCKED: elixir/elixirc not installed")
class ValveRefusalRuntime(unittest.TestCase):
    def test_generated_refusals_compile_clean_and_refuse_with_32_byte_receipts(self) -> None:
        self.assertEqual(violations(run_court(SOURCE)), [])

    def test_sabotaged_receipt_len_is_caught_by_the_court(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        sabotaged = Path(tmp.name) / "refusals_sabotaged.ex"
        text = SOURCE.read_text(encoding="utf-8")
        self.assertIn("@receipt_len 32", text)
        sabotaged.write_text(text.replace("@receipt_len 32", "@receipt_len 31"), encoding="utf-8")
        obs = run_court(sabotaged)
        bad = violations(obs)
        self.assertNotEqual(bad, [], "court passed a sabotaged 31-byte receipt — court is vacuous")
        self.assertTrue(any("31" in v for v in bad), bad)


if __name__ == "__main__":
    unittest.main()
