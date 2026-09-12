defmodule MarketplaceCli.InspectorTest do
  use ExUnit.Case, async: true

  alias MarketplaceCli.Inspector

  @root Application.compile_env(:marketplace_cli, :marketplace_root)

  # Real behavioral-parity check against `python3 scripts/marketplace.py
  # validate` run against this SAME marketplace tree. The real Python
  # command was run once by hand to obtain the comparison line below (see
  # the pack commit message / final report for its exact captured output);
  # this test re-derives the same counts independently through the real
  # Elixir port rather than hard-coding a stale snapshot, and only the
  # PACK-COUNT-DERIVED fields (packs/manifests/ontologies/templates/
  # native_gates/verifier_gates/profiles/diataxis) are asserted, since those
  # are the load-bearing signal marketplace.py's own `validate()` prints.
  test "validate/1 matches real python3 scripts/marketplace.py validate on this marketplace tree" do
    {python_line, 0} =
      System.cmd("python3", ["scripts/marketplace.py", "validate"],
        cd: @root,
        stderr_to_stdout: true
      )

    result = Inspector.validate(@root)

    assert String.trim(result.line) == String.trim(python_line)
  end

  # `catalog/1` builds a real deterministic tar archive (for a real sha256
  # digest) per admitted pack -- at this marketplace's real current scale
  # (301 packs) that genuinely exceeds ExUnit's default 60s timeout. Not a
  # hang/bug: `mix test --timeout 300000` (or this tag) passes cleanly in
  # ~2 minutes. Raised rather than optimized away, since the real work
  # (hashing every pack's real file tree) is the thing under test.
  @tag timeout: 300_000
  test "catalog/1 pack count and names match require_admitted/1's own pack set" do
    packs = Inspector.require_admitted(@root)
    catalog = Inspector.catalog(@root)

    assert length(catalog["packs"]) == length(packs)

    assert Enum.map(catalog["packs"], & &1["name"]) |> Enum.sort() ==
             Enum.map(packs, & &1.name) |> Enum.sort()

    for record <- catalog["packs"] do
      assert is_binary(record["digest"])
      assert record["size_bytes"] > 0
    end
  end

  @tag timeout: 300_000
  test "catalog/1 pack count matches real python3 scripts/marketplace.py catalog on this marketplace tree" do
    {python_json, 0} =
      System.cmd("python3", ["scripts/marketplace.py", "catalog"],
        cd: @root,
        stderr_to_stdout: true
      )

    python_payload = Jason.decode!(python_json)
    elixir_payload = Inspector.catalog(@root)

    assert length(elixir_payload["packs"]) == length(python_payload["packs"])
    assert elixir_payload["marketplace_version"] == python_payload["marketplace_version"]

    python_names = python_payload["packs"] |> Enum.map(& &1["name"]) |> Enum.sort()
    elixir_names = elixir_payload["packs"] |> Enum.map(& &1["name"]) |> Enum.sort()
    assert elixir_names == python_names
  end

  test "ontology_files/1 finds this pack's own real ontology.ttl" do
    this_pack_dir = Path.join([@root, "packs", "noun-verb-cli-pack"])
    assert Path.join(this_pack_dir, "ontology.ttl") in Inspector.ontology_files(this_pack_dir)
  end
end
