# Evaluate a pack's gates/*.rq against every fixture directory in the pack
# (a ggen.toml beside facts.ttl or baseline.ttl) through ggen_igniter's
# Rustler NIF over the Rust oxigraph engine -- an independent witness for
# gate verdicts when the pinned ggen release binary is unavailable. Any gate
# row = REFUSED; zero rows from every gate = ADMITTED. Gate semantics only:
# this does not render templates or prove generated-file behavior.
#
# Usage, from a compiled ggen_igniter checkout
# (https://github.com/seanchatmangpt/ggen_igniter; MIX_ENV=test mix compile):
#   PACK=/path/to/ggen-marketplace/packs/<pack> \
#     MIX_ENV=test mix run --no-start /path/to/ggen-marketplace/scripts/igniter_gate_matrix.exs
pack = Path.expand(System.fetch_env!("PACK"))
onto = File.read!(Path.join(pack, "ontology.ttl"))
gates = Path.wildcard(Path.join(pack, "gates/*.rq")) |> Enum.sort()
Path.wildcard(Path.join(pack, "**/ggen.toml"))
|> Enum.map(&Path.dirname/1)
|> Enum.filter(fn d -> File.exists?(Path.join(d, "facts.ttl")) or File.exists?(Path.join(d, "baseline.ttl")) end)
|> Enum.sort()
|> Enum.each(fn d ->
  f = if File.exists?(Path.join(d, "facts.ttl")), do: "facts.ttl", else: "baseline.ttl"
  ttl = onto <> "\n" <> File.read!(Path.join(d, f))
  rows = for g <- gates, {:ok, rs} = GgenIgniter.Native.GraphNif.query_turtle(ttl, File.read!(g)), r <- rs,
    do: {Path.basename(g, ".rq"), Map.get(r, "violation")}
  verdict = if rows == [], do: "ADMITTED", else: "REFUSED "
  IO.puts("#{verdict} #{Path.relative_to(d, pack)} #{inspect(Enum.frequencies(rows))}")
end)
