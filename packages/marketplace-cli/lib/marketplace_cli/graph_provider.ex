defmodule MarketplaceCli.GraphProvider.GgenIgniterProvider do
  @moduledoc """
  Real `ExNounVerbCli.GraphProvider` implementation wrapping ggen_igniter's
  real ontology-loading + SPARQL-query stack -- the concrete
  `GgenIgniter.Ontology.load!/1` + `GgenIgniter.Query.run/2` pairing named in
  the design spec's milestone 2 (section 5), and the decoupling point the
  spec's "Graph coupling" decision requires: `ex_noun_verb_cli` itself never
  references `ggen_igniter`; this module lives in the consumer instead.

  `load!/1` takes a real Turtle/N-Triples/N-Quads file path and returns a
  real `RDF.Graph.t()`/`RDF.Dataset.t()` (dispatched on extension by
  `GgenIgniter.Ontology.load!/1`). `query/2` runs a real SPARQL SELECT
  string against that graph via `GgenIgniter.Query.run/2` (the pure-Elixir
  `sparql` hex engine -- ggen_igniter's non-NIF default query path) and
  returns the same `[%{"var" => value}]` row shape ggen_igniter's own
  templates consume.
  """

  @behaviour ExNounVerbCli.GraphProvider

  @impl ExNounVerbCli.GraphProvider
  def load!(path) when is_binary(path) do
    GgenIgniter.Ontology.load!(path)
  end

  @impl ExNounVerbCli.GraphProvider
  def query(graph, sparql) when is_binary(sparql) do
    GgenIgniter.Query.run(graph, sparql)
  end
end
