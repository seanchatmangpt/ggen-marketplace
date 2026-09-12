defmodule MarketplaceCli.CliVerbsQueryTest do
  use ExUnit.Case, async: true

  alias MarketplaceCli.GraphProvider.GgenIgniterProvider

  @root Application.compile_env(:marketplace_cli, :marketplace_root)
  @pack_dir Path.join([@root, "packs", "noun-verb-cli-pack"])
  @consumer_dir Path.join([@root, "packages", "marketplace-cli"])

  # Chicago-style: real ggen_igniter Turtle parser + real `sparql` hex query
  # engine, real .rq files on disk, real ontology.ttl on disk -- no
  # mock/fixture stub. These two queries are noun-verb-cli-pack's real
  # consumers for its nvc:CliVerb / nvc:noun / nvc:verb / nvc:belongsTo /
  # nvc:displaces / nvc:usesLibrary / nvc:usesGraphEngine facts (the pack has
  # no Tera templates, so a SPARQL query is the generation-adjacent consumer
  # role a .tmpl file plays elsewhere).
  test "cli_verbs.rq returns the app's real noun/verb dispatch pairs" do
    graph = GgenIgniterProvider.load!(Path.join(@pack_dir, "ontology.ttl"))
    sparql = File.read!(Path.join([@pack_dir, "queries", "cli_verbs.rq"]))

    rows = GgenIgniterProvider.query(graph, sparql)

    verbs =
      rows
      |> Enum.map(fn row -> {row["noun"], row["verb"]} end)
      |> Enum.sort()

    assert verbs == [{"marketplace", "catalog"}, {"marketplace", "validate"}]

    # Each returned verb names a real Igniter.Mix.Tasks module this consumer
    # actually ships -- ties the ontology's declarative record back to the
    # real dispatch table it describes.
    for {_noun, verb} <- verbs do
      task_path = Path.join([@consumer_dir, "lib", "mix", "tasks", "marketplace_cli.#{verb}.ex"])
      assert File.exists?(task_path), "expected real mix task at #{task_path}"
    end
  end

  test "capability_shape.rq returns real displacement/library/graph-engine facts" do
    graph = GgenIgniterProvider.load!(Path.join(@pack_dir, "ontology.ttl"))
    sparql = File.read!(Path.join([@pack_dir, "queries", "capability_shape.rq"]))

    [row] = GgenIgniterProvider.query(graph, sparql)

    assert row["displaces"] =~ "MarketplacePyScript"
    assert row["library"] =~ "ExNounVerbCli"
    assert row["graphEngine"] =~ "GgenIgniter"

    # These claims are checkable against this consumer's own real deps().
    mix_exs = File.read!(Path.join(@consumer_dir, "mix.exs"))
    assert mix_exs =~ "ex_noun_verb_cli"
    assert mix_exs =~ "ggen_igniter"
  end
end
