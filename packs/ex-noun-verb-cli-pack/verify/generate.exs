## verify/generate.exs -- the GENERIC form of this pack's generation layer.
##
## render_check.exs (this pack's own regression proof against
## playground/greet-cli.ttl) is now a thin wrapper around this script.
## This is the reusable capability itself (see the "Generation instances"
## section of this pack's README.md): point it at ANY ontology.ttl declaring
## an nvc:GeneratedCliProject + nvc:GeneratedVerb/nvc:GeneratedArgument
## individuals, and it renders real, ggen_igniter-verified Elixir source --
## not hardcoded to the greet/math playground content.
##
## Usage (from ~/ggen_igniter, this pack's own generator dependency root):
##
##   mix run <pack>/verify/generate.exs -- <ontology.ttl> <output_dir> [template1,template2,...]
##
## `templates` (comma-separated, optional) defaults to all 5 templates under
## templates/. Pass a subset (e.g. "registry.ex.tmpl") when the target
## project already owns its real mix.exs/config.exs/handlers and only the
## generated-shape registry should be produced -- see
## instances/marketplace-cli.ttl and its own generation note for the worked
## example this was built for.
##
## Real steps performed (identical machinery to render_check.exs, factored
## out): GgenIgniter.Ontology.load!/1 -> GgenIgniter.Frontmatter.split_template/1
## per selected template -> GgenIgniter.Query.Oxigraph.run/2 per named sparql
## query -> Elixir-side row pre-join (schema_str/required_str/params_str,
## documented Tera nested-loop.last workaround) -> GgenIgniter.Render.TeraWasm.render/2
## for both the `to:` path and the body -> write -> Code.string_to_quoted!/1
## on every .ex/.exs output.

pack_root = __ENV__.file |> Path.dirname() |> Path.dirname() |> Path.expand()
templates_dir = Path.join(pack_root, "templates")

[ontology_path, output_dir | rest] = System.argv()
requested_templates =
  case rest do
    [csv | _] when csv != "" -> String.split(csv, ",")
    _ -> ["mix.exs.tmpl", "config.exs.tmpl", "registry.ex.tmpl", "handler_stub.ex.tmpl", "README.md.tmpl"]
  end

IO.puts("== ex-noun-verb-cli-pack generate ==")
IO.puts("pack_root:   #{pack_root}")
IO.puts("ontology:    #{ontology_path}")
IO.puts("output_dir:  #{output_dir}")
IO.puts("templates:   #{inspect(requested_templates)}")
IO.puts("")

unless File.exists?(ontology_path) do
  raise "ontology not found at #{ontology_path}"
end

graph = GgenIgniter.Ontology.load!(ontology_path)
IO.puts("loaded graph: #{RDF.Graph.triple_count(graph)} triples")
IO.puts("")

run_named_query = fn query_string ->
  GgenIgniter.Query.Oxigraph.run(graph, query_string)
end

# ---------------------------------------------------------------------------
# Row-shaping helpers (Elixir-side pre-join, working around Tera's nested
# loop.last limitation instead of hiding it -- see templates/registry.ex.tmpl).
# ---------------------------------------------------------------------------

sort_by_order = fn rows -> Enum.sort_by(rows, fn r -> String.to_integer(r["arg_order"]) end) end

args_for = fn args_rows, verb_row ->
  args_rows
  |> Enum.filter(fn a -> a["noun"] == verb_row["noun"] and a["verb"] == verb_row["verb"] end)
  |> sort_by_order.()
end

schema_str = fn args -> Enum.map_join(args, ", ", fn a -> "#{a["arg_name"]}: :#{a["arg_type"]}" end) end

required_str = fn args ->
  args
  |> Enum.filter(fn a -> a["arg_required"] == "true" end)
  |> Enum.map_join(", ", fn a -> ":#{a["arg_name"]}" end)
end

params_str = fn args -> Enum.map_join(args, ", ", fn a -> a["arg_name"] end) end

enrich_for_registry = fn verb_row, args_rows ->
  args = args_for.(args_rows, verb_row)

  Map.merge(verb_row, %{
    "schema_str" => schema_str.(args),
    "required_str" => required_str.(args)
  })
end

enrich_for_handler = fn verb_row, args_rows ->
  args = args_for.(args_rows, verb_row)

  Map.merge(verb_row, %{
    "params_str" => params_str.(args),
    "body_str" => verb_row["body_expr"]
  })
end

render_to_path! = fn frontmatter, context ->
  case GgenIgniter.Render.TeraWasm.render(frontmatter.to, context) do
    {:ok, rendered} -> String.trim(rendered)
    {:error, reason} -> raise "failed to render `to:` path #{inspect(frontmatter.to)}: #{inspect(reason)}"
  end
end

render_body! = fn body, context ->
  case GgenIgniter.Render.TeraWasm.render(body, context) do
    {:ok, rendered} -> rendered
    {:error, reason} -> raise "failed to render template body: #{inspect(reason)}"
  end
end

write_rendered! = fn rel_path, contents ->
  full_path = Path.join(output_dir, rel_path)
  File.mkdir_p!(Path.dirname(full_path))
  File.write!(full_path, contents)
  full_path
end

template_files =
  requested_templates
  |> Enum.map(fn name ->
    path = Path.join(templates_dir, name)
    raw = File.read!(path)
    {frontmatter, :file, body} = GgenIgniter.Frontmatter.split_template(raw)
    {name, frontmatter, body}
  end)
  |> Map.new(fn {name, fm, body} -> {name, {fm, body}} end)

run_queries = fn frontmatter ->
  Map.new(frontmatter.sparql, fn {query_name, query_string} ->
    {query_name, run_named_query.(query_string)}
  end)
end

written = []

# NOTE: each block below is `written = if ... do ... else written end`, not a
# bare `if` -- Elixir does not leak a rebind from inside an `if do...end`
# back to the enclosing scope unless the `if` expression's own value is
# reassigned to the outer name. A bare `if Map.has_key?(...) do written = [...|written] end`
# looks correct but silently no-ops on every branch (a real bug this pack's
# own render_check.exs regression run caught: "files written (0)" against a
# graph that genuinely had 4 verb rows).

written =
  if Map.has_key?(template_files, "mix.exs.tmpl") do
    {fm, body} = Map.fetch!(template_files, "mix.exs.tmpl")
    rows = run_queries.(fm)
    project = Map.fetch!(rows, "project")
    IO.puts("mix.exs.tmpl -- project rows: #{inspect(project)}")
    context = %{"project" => project}
    rel = render_to_path!.(fm, context)
    rendered = render_body!.(body, context)
    path = write_rendered!.(rel, rendered)
    [{path, rendered} | written]
  else
    written
  end

written =
  if Map.has_key?(template_files, "config.exs.tmpl") do
    {fm, body} = Map.fetch!(template_files, "config.exs.tmpl")
    rows = run_queries.(fm)
    project = Map.fetch!(rows, "project")
    context = %{"project" => project}
    rel = render_to_path!.(fm, context)
    rendered = render_body!.(body, context)
    path = write_rendered!.(rel, rendered)
    [{path, rendered} | written]
  else
    written
  end

written =
  if Map.has_key?(template_files, "registry.ex.tmpl") do
    {fm, body} = Map.fetch!(template_files, "registry.ex.tmpl")
    rows = run_queries.(fm)
    project = Map.fetch!(rows, "project")
    verb_rows = Map.fetch!(rows, "verbs")
    args_rows = Map.fetch!(rows, "args")
    IO.puts("registry.ex.tmpl -- #{length(verb_rows)} verb rows, #{length(args_rows)} arg rows")
    enriched_verbs = Enum.map(verb_rows, fn v -> enrich_for_registry.(v, args_rows) end)
    context = %{"project" => project, "verbs" => enriched_verbs}
    rel = render_to_path!.(fm, context)
    rendered = render_body!.(body, context)
    path = write_rendered!.(rel, rendered)
    [{path, rendered} | written]
  else
    written
  end

written =
  if Map.has_key?(template_files, "README.md.tmpl") do
    {fm, body} = Map.fetch!(template_files, "README.md.tmpl")
    rows = run_queries.(fm)
    project = Map.fetch!(rows, "project")
    verb_rows_readme = Map.fetch!(rows, "verbs")
    context = %{"project" => project, "verbs" => verb_rows_readme}
    rel = render_to_path!.(fm, context)
    rendered = render_body!.(body, context)
    path = write_rendered!.(rel, rendered)
    [{path, rendered} | written]
  else
    written
  end

written =
  if Map.has_key?(template_files, "handler_stub.ex.tmpl") do
    {fm, body} = Map.fetch!(template_files, "handler_stub.ex.tmpl")
    rows = run_queries.(fm)
    project = Map.fetch!(rows, "project")
    all_verb_rows = Map.fetch!(rows, "verbs")
    all_args_rows = Map.fetch!(rows, "args")

    nouns = all_verb_rows |> Enum.map(& &1["noun"]) |> Enum.uniq()
    IO.puts("handler_stub.ex.tmpl -- nouns: #{inspect(nouns)}")

    Enum.reduce(nouns, written, fn noun, acc ->
      noun_verbs =
        all_verb_rows
        |> Enum.filter(&(&1["noun"] == noun))
        |> Enum.map(fn v -> enrich_for_handler.(v, all_args_rows) end)

      noun_mod = %{
        "noun" => noun,
        "noun_pascal" => Macro.camelize(noun),
        "noun_snake" => Macro.underscore(noun)
      }

      context = %{"project" => project, "noun_mod" => noun_mod, "verbs" => noun_verbs}
      rel = render_to_path!.(fm, context)
      rendered = render_body!.(body, context)
      path = write_rendered!.(rel, rendered)
      [{path, rendered} | acc]
    end)
  else
    written
  end

IO.puts("")
IO.puts("== files written (#{length(written)}) ==")

quoted_ok =
  Enum.reduce(written, 0, fn {path, contents}, ok_count ->
    byte_count = byte_size(contents)
    ext = Path.extname(path)

    quoted_status =
      if ext in [".ex", ".exs"] do
        Code.string_to_quoted!(contents)
        "QUOTED_OK"
      else
        "N/A (not Elixir source)"
      end

    IO.puts("  #{path} (#{byte_count} bytes) -- #{quoted_status}")

    if ext in [".ex", ".exs"], do: ok_count + 1, else: ok_count
  end)

IO.puts("")
IO.puts("== summary receipt ==")
IO.puts("templates rendered: #{map_size(template_files)}")
IO.puts("files written:      #{length(written)}")
IO.puts("elixir files:       #{Enum.count(written, fn {p, _} -> Path.extname(p) in [".ex", ".exs"] end)}")
IO.puts("quoted-ok count:    #{quoted_ok}")
IO.puts("generate: PASS")
