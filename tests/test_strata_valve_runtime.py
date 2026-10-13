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
  name = mod |> Module.split() |> List.last() |> String.upcase()
  IO.puts("REFUSE_#{name}_SIZE=" <> to_string(byte_size(bin)))
end
doc =
  case Code.fetch_docs(Strata.Valve.Refusals.MalformedFrame) do
    {:docs_v1, _, _, _, %{"en" => d}, _, _} -> d
    _ -> ""
  end
IO.puts("MODULEDOC_HAS_32BYTE=" <> to_string(String.contains?(doc, "32-byte receipt")))
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
    if obs.get("MODULEDOC_HAS_32BYTE") != "true":
        bad.append(f"MODULEDOC_HAS_32BYTE={obs.get('MODULEDOC_HAS_32BYTE')!r} != 'true'")
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
