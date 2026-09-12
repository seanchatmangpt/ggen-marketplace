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
  # digest) per admitted pack. `build_pack_archive_digest/1` still does a
  # real disk write+read+delete round trip per pack -- confirmed against
  # OTP 28.3.1's `erl_tar` source (stdlib-7.2/src/erl_tar.erl): `erl_tar`'s
  # in-memory `{binary, Bin}` open target is wired only for `read` access,
  # never `write`, so there is no genuine in-memory tar-write target to swap
  # in without hand-reimplementing `erl_tar`'s own writer. The real fix
  # (`catalog/1` now runs per-pack digesting via `Task.async_stream/3`
  # instead of serially) measured a real single call to `Inspector.catalog/1`
  # at this marketplace's real current scale (301 packs) at ~28.5s wall clock
  # (`mix test test/marketplace_cli/inspector_test.exs:<line> --timeout
  # 300000`, 2026-09-11) -- comfortably under ExUnit's default 60s timeout.
  # No explicit tag needed anymore; kept generous rather than exactly 60s
  # since real wall-clock varies with machine load.
  @tag timeout: 60_000
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

  # Runs a real `python3 scripts/marketplace.py catalog` subprocess in
  # addition to a real `Inspector.catalog/1` call -- generous timeout kept
  # for the subprocess's own real startup+301-pack cost, but well below the
  # old 300s: see the timeout note on the sibling test above for the real
  # measured `Inspector.catalog/1` cost alone (~28.5s).
  @tag timeout: 90_000
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

  # Permanent regression falsifier for the tar-digest fix
  # (3f3e641e1, "parallelize catalog/1 pack digesting"). That fix moved
  # per-pack digesting from `Enum.map/2` to `Task.async_stream/3` --
  # concurrent scheduling of the same real `:erl_tar.create/3` write +
  # `File.read!` + `File.rm` round trip per pack. The real risk a
  # parallelization refactor like that introduces is non-determinism: two
  # concurrent tasks racing on the same `System.tmp_dir!()`-scoped tmp
  # filename, or the archive's own byte layout depending on run order. This
  # test builds the real catalog for the SAME pack tree from two independent
  # `Inspector.catalog/1` calls (same process, real disk I/O both times) and
  # asserts every pack's digest is byte-identical across both real
  # calls -- a real clean-checkout-reproduction falsifier: if the
  # parallelized path ever reintroduces order-dependence or tmp-file
  # collision, this test fails on a real digest mismatch, not a
  # hand-maintained fixture.
  @tag timeout: 90_000
  test "catalog/1 digest is byte-identical across two independent real calls (tar-digest regression falsifier)" do
    first = Inspector.catalog(@root)
    second = Inspector.catalog(@root)

    first_digests =
      first["packs"] |> Enum.map(&{&1["name"], &1["digest"]}) |> Enum.sort()

    second_digests =
      second["packs"] |> Enum.map(&{&1["name"], &1["digest"]}) |> Enum.sort()

    assert first_digests == second_digests

    for {name, digest} <- first_digests do
      assert String.starts_with?(digest, "sha256:"),
             "pack #{name} produced non-sha256 digest #{inspect(digest)}"
    end
  end
end
