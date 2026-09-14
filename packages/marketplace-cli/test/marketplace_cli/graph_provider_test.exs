defmodule MarketplaceCli.GraphProviderTest do
  use ExUnit.Case, async: true

  alias MarketplaceCli.GraphProvider.GgenIgniterProvider
  alias MarketplaceCli.Inspector

  @root Application.compile_env(:marketplace_cli, :marketplace_root)

  # Chicago-style: real ggen_igniter (real RDF.ex Turtle parser + real
  # `sparql` hex query engine), real file on disk -- no mock/fixture stub.
  test "load!/1 + query/2 count this pack's own ontology.ttl's real triples" do
    path = Path.join([@root, "packs", "noun-verb-cli-pack", "ontology.ttl"])

    graph = GgenIgniterProvider.load!(path)
    assert %RDF.Graph{} = graph

    rows = GgenIgniterProvider.query(graph, "SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
    assert length(rows) > 0
  end

  test "Inspector.ontology_triple_count/2 uses the real GraphProvider end to end" do
    pack = %Inspector.Pack{
      name: "noun-verb-cli-pack",
      version: "26.9.11",
      description: "x",
      path: Path.join([@root, "packs", "noun-verb-cli-pack"]),
      ontologies: [Path.join([@root, "packs", "noun-verb-cli-pack", "ontology.ttl"])],
      templates: [],
      native_gates: [],
      verifier_gates: []
    }

    count = Inspector.ontology_triple_count(pack, GgenIgniterProvider)
    assert count > 0
  end
end
