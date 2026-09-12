## verify/render_check.exs -- REAL render proof for ex-noun-verb-cli-pack's
## generation layer (ontology.ttl "EXTENSION 2" + templates/*.tmpl).
##
## Run from ~/ggen_igniter (this pack's own generator dependency root), NOT
## from this pack's own directory -- this pack has no mix.exs of its own; it
## is data + templates consumed by ggen_igniter's real modules:
##
##   cd ~/ggen_igniter && mix run <this pack>/verify/render_check.exs
##
## What this script actually does, in order (mirrors this pack's own design
## doc section 4):
##   1. GgenIgniter.Ontology.load!/1 the real playground/greet-cli.ttl.
##   2. For each templates/*.tmpl file: GgenIgniter.Frontmatter.split_template/1
##      (the real frontmatter parser, not a hand-rolled YAML splitter) to get
##      its `to:` path template, its named `sparql:` queries, and its body.
##   3. Run each named query for real via GgenIgniter.Query.Oxigraph.run/2 (the
##      real oxigraph NIF engine -- required here, not the default
##      GgenIgniter.Query.run/2, because this pack's queries use ORDER BY,
##      which the sparql-hex engine is documented to get backwards; see
##      lib/ggen_igniter/query.ex's own moduledoc).
##   4. Pre-join each verb row's schema/required/params/body strings in
##      Elixir (not Tera) -- documented workaround for Tera's loop.last
##      conflation inside a nested filtered loop; see this pack's own
##      templates/registry.ex.tmpl comment and README.md.
##   5. GgenIgniter.Render.TeraWasm.render/2 each template body (real Tera,
##      via the real compiled native/tera_wasm_renderer wasm module) against
##      that context, and also render the `to:` path template itself the same
##      way (it is Tera syntax too: `lib/{{ project[0].app_name }}/...`).
##   6. Write every rendered file under examples/greet-cli/.
##   7. Code.string_to_quoted!/1 every generated .ex/.exs file -- a raised
##      exception fails this script; a clean run is the real assertion.
##   8. Print a summary receipt.

pack_root = __ENV__.file |> Path.dirname() |> Path.dirname() |> Path.expand()
playground_path = Path.join(pack_root, "playground/greet-cli.ttl")
templates_dir = Path.join(pack_root, "templates")
examples_dir = Path.join(pack_root, "examples/greet-cli")

IO.puts("== ex-noun-verb-cli-pack render_check ==")
IO.puts("pack_root:       #{pack_root}")
IO.puts("playground:      #{playground_path}")
IO.puts("templates_dir:   #{templates_dir}")
IO.puts("examples_dir:    #{examples_dir}")
IO.puts("")

unless File.exists?(playground_path) do
  raise "playground ontology not found at #{playground_path}"
end

graph = GgenIgniter.Ontology.load!(playground_path)
IO.puts("loaded graph: #{RDF.Graph.triple_count(graph)} triples")
IO.puts("")

run_named_query = fn query_string ->
  GgenIgniter.Query.Oxigraph.run(graph, query_string)
end

# ---------------------------------------------------------------------------
# Row-shaping helpers (the Elixir-side pre-join documented in this pack's own
# templates/registry.ex.tmpl and README.md, working around Tera's nested-loop
# loop.last limitation instead of hiding it).
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
  full_path = Path.join(examples_dir, rel_path)
  File.mkdir_p!(Path.dirname(full_path))
  File.write!(full_path, contents)
  full_path
end

# ---------------------------------------------------------------------------
# Load and split every template's real frontmatter once, up front.
# ---------------------------------------------------------------------------

template_files =
  ["mix.exs.tmpl", "config.exs.tmpl", "registry.ex.tmpl", "handler_stub.ex.tmpl", "README.md.tmpl"]
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

# ---- mix.exs.tmpl ----
{fm, body} = Map.fetch!(template_files, "mix.exs.tmpl")
rows = run_queries.(fm)
project = Map.fetch!(rows, "project")
IO.puts("mix.exs.tmpl -- project rows: #{inspect(project)}")
context = %{"project" => project}
rel = render_to_path!.(fm, context)
rendered = render_body!.(body, context)
path = write_rendered!.(rel, rendered)
written = [{path, rendered} | written]

# ---- config.exs.tmpl ----
{fm, body} = Map.fetch!(template_files, "config.exs.tmpl")
rows = run_queries.(fm)
project = Map.fetch!(rows, "project")
context = %{"project" => project}
rel = render_to_path!.(fm, context)
rendered = render_body!.(body, context)
path = write_rendered!.(rel, rendered)
written = [{path, rendered} | written]

# ---- registry.ex.tmpl ----
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
written = [{path, rendered} | written]

# ---- README.md.tmpl ----
{fm, body} = Map.fetch!(template_files, "README.md.tmpl")
rows = run_queries.(fm)
project = Map.fetch!(rows, "project")
verb_rows_readme = Map.fetch!(rows, "verbs")
context = %{"project" => project, "verbs" => verb_rows_readme}
rel = render_to_path!.(fm, context)
rendered = render_body!.(body, context)
path = write_rendered!.(rel, rendered)
written = [{path, rendered} | written]

# ---- handler_stub.ex.tmpl -- once per distinct noun ----
{fm, body} = Map.fetch!(template_files, "handler_stub.ex.tmpl")
rows = run_queries.(fm)
project = Map.fetch!(rows, "project")
all_verb_rows = Map.fetch!(rows, "verbs")
all_args_rows = Map.fetch!(rows, "args")

nouns = all_verb_rows |> Enum.map(& &1["noun"]) |> Enum.uniq()
IO.puts("handler_stub.ex.tmpl -- nouns: #{inspect(nouns)}")

written =
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
IO.puts("render_check: PASS")
