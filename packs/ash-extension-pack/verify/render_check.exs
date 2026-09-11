# Chicago-style, no-mocks real-render smoke check for the ash-extension-pack
# marketplace pack. Run with:
#
#   cd /Users/sac/ggen_igniter && mix run <abs_path_to_this_file>
#
# so it executes inside ggen_igniter's own compiled Mix project (this file
# calls GgenIgniter.Ontology/Query/Frontmatter/Render.TeraWasm directly --
# those modules are not available outside that project context).
#
# This script is written defensively: any referenced ontology/gate/query/
# template file that does not yet exist on disk prints a "MISSING: <path>"
# line and is skipped rather than crashing the whole report.
#
# Context binding: each template's OWN frontmatter `sparql:` block names its
# real query sources, and `for_each:` (when present) names which one drives
# multi-row fan-out. This script runs those real queries per-template (via
# the real GgenIgniter.Query.Oxigraph.run/2 engine) and builds the render
# context via Mix.Tasks.GgenIgniter.Sync.build_bindings/2 -- the exact same
# production binding function `mix ggen_igniter.sync` itself uses -- rather
# than guessing a generic superset context unrelated to each template's own
# declared query names. This is a real integration fix: an earlier version of
# this script ran only the pack-level gates/queries and fed every template a
# context that never matched what its frontmatter actually asked for, so
# every template failed to render for a binding-mismatch reason unrelated to
# TeraWasm/tera itself.

pack_root = Path.expand(Path.join(__DIR__, ".."))

IO.puts("== ash-extension-pack render_check ==")
IO.puts("pack_root: #{pack_root}")
IO.puts("")

defmodule RenderCheck do
  @moduledoc """
  Helper functions for the render_check.exs script. Kept as a real module
  (not anonymous functions in the script body) purely for readability --
  every call here still hits real GgenIgniter.* code, no test doubles.
  """

  def read_file(path) do
    if File.exists?(path) do
      {:ok, File.read!(path)}
    else
      {:missing, path}
    end
  end

  @doc """
  Runs one gate/query file (by real path) against the already-loaded real
  RDF.Graph via the real oxigraph engine (GgenIgniter.Query.Oxigraph.run/2 --
  chosen over the default sparql engine because these gate queries are
  expected to be ORDER BY-sensitive multi-row contract checks, and the
  sparql hex engine has a confirmed ORDER BY bug per
  lib/ggen_igniter/query.ex's own moduledoc). Returns
  {:ok, rows} | {:missing, path} | {:parse_error, reason}.
  """
  def run_query_file(graph, path) do
    case read_file(path) do
      {:missing, ^path} ->
        {:missing, path}

      {:ok, query_string} ->
        run_query_text(graph, query_string)
    end
  end

  def run_query_text(graph, query_string) do
    try do
      rows = GgenIgniter.Query.Oxigraph.run(graph, query_string)
      {:ok, rows}
    rescue
      e -> {:parse_error, Exception.format(:error, e, __STACKTRACE__)}
    end
  end

  def print_query_result(label, path, result) do
    case result do
      {:missing, ^path} ->
        IO.puts("  #{label} (#{path}): MISSING")

      {:parse_error, reason} ->
        first_line = reason |> String.split("\n") |> List.first()
        IO.puts("  #{label} (#{path}): PARSE ERROR: #{first_line}")

      {:ok, rows} ->
        count = length(rows)
        sample =
          case rows do
            [first | _] -> inspect(first, limit: 5, printable_limit: 200)
            [] -> "(no rows)"
          end

        IO.puts("  #{label} (#{path}): #{count} row(s); sample: #{sample}")
    end
  end
end

# ---------------------------------------------------------------------------
# 1 & 2. Load the real ontology.
# ---------------------------------------------------------------------------

ontology_path = Path.join(pack_root, "ontology.ttl")

graph =
  case RenderCheck.read_file(ontology_path) do
    {:missing, ^ontology_path} ->
      IO.puts("MISSING: #{ontology_path}")
      IO.puts("(cannot load ontology -- all gate/query/template checks below will be skipped)")
      nil

    {:ok, _raw} ->
      try do
        g = GgenIgniter.Ontology.load!(ontology_path)
        IO.puts("ontology loaded ok: #{ontology_path}")
        g
      rescue
        e ->
          IO.puts("PARSE ERROR loading ontology #{ontology_path}: #{Exception.format(:error, e, __STACKTRACE__) |> String.split("\n") |> List.first()}")
          nil
      end
  end

IO.puts("")

# ---------------------------------------------------------------------------
# 3. Gates 010..060 and the two named queries -- real filenames on disk,
#    confirmed via `find packs/ash-extension-pack -type f`.
# ---------------------------------------------------------------------------

gate_files = [
  {"gate 010 (required_extension_contract)", Path.join([pack_root, "gates", "010_required_extension_contract.rq"])},
  {"gate 020 (schema_field_contract)", Path.join([pack_root, "gates", "020_schema_field_contract.rq"])},
  {"gate 030 (entity_identifier_contract)", Path.join([pack_root, "gates", "030_entity_identifier_contract.rq"])},
  {"gate 040 (reactor_step_graph_contract)", Path.join([pack_root, "gates", "040_reactor_step_graph_contract.rq"])},
  {"gate 050 (info_getter_quadruple_contract)", Path.join([pack_root, "gates", "050_info_getter_quadruple_contract.rq"])},
  {"gate 060 (installer_target_mode_contract)", Path.join([pack_root, "gates", "060_installer_target_mode_contract.rq"])}
]

query_files = [
  {"query reactor_steps", Path.join([pack_root, "queries", "reactor_steps.rq"])},
  {"query receipted_action", Path.join([pack_root, "queries", "receipted_action.rq"])}
]

IO.puts("-- gates --")

gate_results =
  Enum.map(gate_files, fn {label, path} ->
    result = if graph, do: RenderCheck.run_query_file(graph, path), else: {:missing, path}
    RenderCheck.print_query_result(label, path, result)
    {label, path, result}
  end)

IO.puts("")
IO.puts("-- queries --")

query_results =
  Enum.map(query_files, fn {label, path} ->
    result = if graph, do: RenderCheck.run_query_file(graph, path), else: {:missing, path}
    RenderCheck.print_query_result(label, path, result)
    {label, path, result}
  end)

IO.puts("")

gates_run = Enum.count(gate_results, fn {_l, _p, r} -> match?({:ok, _}, r) end)
queries_run = Enum.count(query_results, fn {_l, _p, r} -> match?({:ok, _}, r) end)

# ---------------------------------------------------------------------------
# 4. Render each of the 8 templates, using EACH TEMPLATE'S OWN frontmatter
#    `sparql:`/`for_each:` block -- the real production binding path
#    (Mix.Tasks.GgenIgniter.Sync.build_bindings/2), not a guessed context.
# ---------------------------------------------------------------------------

template_files = [
  {"extension.ex.tmpl", Path.join([pack_root, "templates", "extension.ex.tmpl"])},
  {"persist.ex.tmpl", Path.join([pack_root, "templates", "persist.ex.tmpl"])},
  {"verify.ex.tmpl", Path.join([pack_root, "templates", "verify.ex.tmpl"])},
  {"info.ex.tmpl", Path.join([pack_root, "templates", "info.ex.tmpl"])},
  {"install.ex.tmpl", Path.join([pack_root, "templates", "install.ex.tmpl"])},
  {"reactor_pipeline.ex.tmpl", Path.join([pack_root, "templates", "reactor_pipeline.ex.tmpl"])},
  {"receipted_action.ex.tmpl", Path.join([pack_root, "templates", "receipted_action.ex.tmpl"])},
  {"composition_test.exs.tmpl", Path.join([pack_root, "templates", "composition_test.exs.tmpl"])}
]

IO.puts("-- templates: render --")

render_template_file = fn path ->
  case RenderCheck.read_file(path) do
    {:missing, ^path} ->
      {:missing, path}

    {:ok, raw} ->
      try do
        {frontmatter, _mode, body} = GgenIgniter.Frontmatter.split_template(raw)

        named_queries =
          case frontmatter do
            %GgenIgniter.Frontmatter{sparql: map} when is_map(map) and map_size(map) > 0 ->
              Map.to_list(map)

            _ ->
              []
          end

        if named_queries == [] do
          {:frontmatter_error, "no sparql: block found in frontmatter -- cannot bind real context"}
        else
          named_results =
            Enum.map(named_queries, fn {name, query_text} ->
              result = if graph, do: RenderCheck.run_query_text(graph, query_text), else: {:missing, "no ontology loaded"}

              rows =
                case result do
                  {:ok, rows} -> rows
                  {:parse_error, reason} -> {:query_error, name, reason}
                  {:missing, reason} -> {:query_error, name, reason}
                end

              {name, rows}
            end)

          query_errors =
            Enum.filter(named_results, fn {_name, rows} -> match?({:query_error, _, _}, rows) end)

          if query_errors != [] do
            {name, {:query_error, _n, reason}} = List.first(query_errors)
            first_line = reason |> to_string() |> String.split("\n") |> List.first()
            {:frontmatter_error, "named query \"#{name}\" failed: #{first_line}"}
          else
            for_each_name = Map.get(frontmatter, :for_each)

            case for_each_name do
              nil ->
                bindings = Mix.Tasks.GgenIgniter.Sync.build_bindings(named_results)
                context = Map.new(bindings)

                case GgenIgniter.Render.TeraWasm.render(body, context) do
                  {:ok, rendered} -> {:ok, {frontmatter, [rendered]}}
                  {:error, reason} -> {:error, reason}
                end

              driver_name ->
                driver_rows =
                  case List.keyfind(named_results, driver_name, 0) do
                    {^driver_name, rows} when is_list(rows) -> rows
                    _ -> []
                  end

                if driver_rows == [] do
                  {:error, "for_each driver query \"#{driver_name}\" produced 0 rows -- nothing to render"}
                else
                  results =
                    Enum.map(driver_rows, fn row ->
                      bindings = Mix.Tasks.GgenIgniter.Sync.build_bindings(named_results, row)
                      context = Map.new(bindings)
                      GgenIgniter.Render.TeraWasm.render(body, context)
                    end)

                  errors = Enum.filter(results, &match?({:error, _}, &1))

                  if errors != [] do
                    {:error, "for_each row render failed: #{inspect(List.first(errors))}"}
                  else
                    rendered_bodies = Enum.map(results, fn {:ok, r} -> r end)
                    {:ok, {frontmatter, rendered_bodies}}
                  end
                end
            end
          end
        end
      rescue
        e -> {:frontmatter_error, Exception.format(:error, e, __STACKTRACE__)}
      end
  end
end

render_results =
  Enum.map(template_files, fn {name, path} ->
    result = render_template_file.(path)

    case result do
      {:missing, ^path} ->
        IO.puts("  #{name}: MISSING (#{path})")

      {:frontmatter_error, reason} ->
        first_line = reason |> to_string() |> String.split("\n") |> List.first()
        IO.puts("  #{name}: FRONTMATTER/QUERY ERROR: #{first_line}")

      {:ok, {_frontmatter, rendered_bodies}} ->
        total_bytes = Enum.reduce(rendered_bodies, 0, fn r, acc -> acc + byte_size(r) end)
        IO.puts("  #{name}: {:ok, #{length(rendered_bodies)} row(s), #{total_bytes} total bytes}")

      {:error, reason} ->
        IO.puts("  #{name}: {:error, #{inspect(reason)}}")
    end

    {name, path, result}
  end)

IO.puts("")

templates_rendered_ok =
  Enum.count(render_results, fn {_n, _p, r} -> match?({:ok, {_fm, _bodies}}, r) end)

# ---------------------------------------------------------------------------
# 5. Syntax check every successfully-rendered template body; extra compile
#    check for the four core Spark/Ash extension modules.
# ---------------------------------------------------------------------------

IO.puts("-- templates: syntax check --")

syntax_results =
  Enum.map(render_results, fn {name, _path, result} ->
    case result do
      {:ok, {_fm, bodies}} ->
        body_results =
          Enum.map(bodies, fn body ->
            case Code.string_to_quoted(body) do
              {:ok, _quoted} -> :valid_syntax
              {:error, reason} -> {:syntax_error, reason}
            end
          end)

        bad = Enum.find(body_results, &match?({:syntax_error, _}, &1))

        case bad do
          nil ->
            IO.puts("  #{name}: :valid_syntax (#{length(bodies)} row(s))")
            {name, :valid_syntax}

          {:syntax_error, reason} ->
            IO.puts("  #{name}: SYNTAX ERROR: #{inspect(reason)}")
            {name, {:syntax_error, reason}}
        end

      _ ->
        {name, :skipped}
    end
  end)

valid_syntax_count =
  Enum.count(syntax_results, fn {_n, r} -> r == :valid_syntax end)

IO.puts("")
IO.puts("-- four-module compile check (extension + persist + verify + info) --")

core_module_names = ["extension.ex.tmpl", "persist.ex.tmpl", "verify.ex.tmpl", "info.ex.tmpl"]

core_rendered_bodies =
  Enum.map(core_module_names, fn name ->
    Enum.find_value(render_results, fn {n, _p, result} ->
      if n == name do
        case result do
          {:ok, {_fm, [body | _]}} -> body
          _ -> nil
        end
      end
    end)
  end)

compile_check_result =
  cond do
    Enum.any?(core_rendered_bodies, &is_nil/1) ->
      missing_names =
        Enum.zip(core_module_names, core_rendered_bodies)
        |> Enum.filter(fn {_n, body} -> is_nil(body) end)
        |> Enum.map(fn {n, _} -> n end)

      IO.puts("  skipped: not all four core templates rendered successfully (missing/failed: #{inspect(missing_names)})")
      :skipped

    true ->
      concatenated = Enum.join(core_rendered_bodies, "\n\n")

      try do
        Code.compile_string(concatenated)
        IO.puts("  :compiles")
        :compiles
      rescue
        e ->
          reason = Exception.format(:error, e, __STACKTRACE__)
          first_line = reason |> String.split("\n") |> List.first()
          IO.puts("  :error #{first_line}")
          {:error, reason}
      end
  end

IO.puts("")

# ---------------------------------------------------------------------------
# 6. Final summary + honest disclosure re: TeraWasm/`{% if %}`/row-indexed
#    access, grounded in THIS run's actual results (not assumed either way).
# ---------------------------------------------------------------------------

IO.puts("== SUMMARY ==")
IO.puts("gates run ok: #{gates_run}/#{length(gate_files)}")
IO.puts("queries run ok: #{queries_run}/#{length(query_files)}")
IO.puts("templates rendered ok: #{templates_rendered_ok}/#{length(template_files)}")
IO.puts("templates with valid syntax: #{valid_syntax_count}/#{length(template_files)}")
IO.puts("four-module compile check: #{inspect(compile_check_result)}")
IO.puts("")

any_render_error =
  Enum.any?(render_results, fn {_n, _p, r} -> match?({:error, _}, r) end)

any_render_ok = templates_rendered_ok > 0

disclosure =
  cond do
    any_render_ok and not any_render_error ->
      "This run's real {:ok, _} results above are the first real evidence in this " <>
        "session that GgenIgniter.Render.TeraWasm.render/2 (the real WASM tera crate) " <>
        "successfully renders this pack's `{% if %}`/`{{ row[\"key\"] }}`-style " <>
        "row-indexed and multi-row context bindings for real ash-extension-pack " <>
        "templates -- CONFIRMED for the templates that rendered, based on real output " <>
        "above, not assumed."

    any_render_ok and any_render_error ->
      "This run produced a MIX of real {:ok, _} and real {:error, _} results above -- " <>
        "some templates' `{% if %}`/row-indexed-access constructs are CONFIRMED working " <>
        "against the real WASM tera renderer, others are REFUTED (see the real {:error, ...} " <>
        "lines above for which template and why)."

    templates_rendered_ok == 0 and length(template_files) > 0 ->
      "No template rendered successfully this run (see MISSING/error lines above), so " <>
        "this run provides NO real evidence either confirming or refuting whether " <>
        "TeraWasm handles this pack's `{% if %}`/row-indexed/multi-row constructs -- " <>
        "that remains genuinely untested pending the missing files."

    true ->
      "No templates were checked this run."
  end

IO.puts("DISCLOSURE: #{disclosure}")
