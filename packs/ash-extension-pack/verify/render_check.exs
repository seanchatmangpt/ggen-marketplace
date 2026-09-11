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
# line and is skipped rather than crashing the whole report. It is meant to
# be runnable mid-construction (while sibling agents are still writing
# ontology.ttl / templates/*.tmpl in the same shared worktree) and to produce
# a partial-but-useful report in that case -- a partial run is not a final
# verdict; that comes later in this workflow's integration phase.

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
        try do
          rows = GgenIgniter.Query.Oxigraph.run(graph, query_string)
          {:ok, rows}
        rescue
          e -> {:parse_error, Exception.format(:error, e, __STACKTRACE__)}
        end
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

  @doc """
  Reads a raw template file, splits real frontmatter via
  GgenIgniter.Frontmatter.split_template/1, and renders the real body via
  GgenIgniter.Render.TeraWasm.render/2 against `context`. Returns
  {:missing, path} | {:frontmatter_error, reason} | {:ok, {frontmatter, rendered}}
  | {:error, reason}.
  """
  def render_template_file(path, context, context_label) do
    case read_file(path) do
      {:missing, ^path} ->
        {:missing, path}

      {:ok, raw} ->
        try do
          {frontmatter, _mode, body} = GgenIgniter.Frontmatter.split_template(raw)

          case GgenIgniter.Render.TeraWasm.render(body, context) do
            {:ok, rendered} ->
              IO.puts(
                "  context used for #{Path.basename(path)}: #{context_label} (keys: #{inspect(Map.keys(context))})"
              )

              {:ok, {frontmatter, rendered}}

            {:error, reason} ->
              IO.puts(
                "  context used for #{Path.basename(path)}: #{context_label} (keys: #{inspect(Map.keys(context))})"
              )

              {:error, reason}
          end
        rescue
          e -> {:frontmatter_error, Exception.format(:error, e, __STACKTRACE__)}
        end
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
# 3. Gates 010..060 and the two named queries.
# ---------------------------------------------------------------------------

gate_files = [
  {"gate 010 (required_extension_contract)", Path.join([pack_root, "gates", "010_required_extension_contract.rq"])},
  {"gate 020", Path.join([pack_root, "gates", "020_reactor_step_contract.rq"])},
  {"gate 030", Path.join([pack_root, "gates", "030_receipted_action_contract.rq"])},
  {"gate 040", Path.join([pack_root, "gates", "040_info_dsl_contract.rq"])},
  {"gate 050", Path.join([pack_root, "gates", "050_persist_verify_contract.rq"])},
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
# 4. Render each of the 8 templates via GgenIgniter.Render.TeraWasm.render/2.
#
# Best-effort context binding: each template's frontmatter names a query it
# expects rows from (its `sparql:`/`for_each:` keys once frontmatter parses
# for real), but since we may not yet know the pack's real frontmatter query
# names with certainty this pass, we build a superset context map containing
# every gate/query row-list under multiple plausible keys, plus first-row
# convenience keys, so a template can bind via either `{{ row["key"] }}`-style
# indexed access over a list or plain top-level variables. This is explicitly
# a best-effort, disclosed guess -- see the final summary for an honest
# statement of what this proves and does not prove.
# ---------------------------------------------------------------------------

all_named_results = gate_results ++ query_results

# rows_by_name: %{"required_extension_contract" => [row, ...], "reactor_steps" => [...], ...}
rows_by_name =
  Enum.reduce(all_named_results, %{}, fn {_label, path, result}, acc ->
    case result do
      {:ok, rows} ->
        name = path |> Path.basename() |> String.replace_suffix(".rq", "")
        # Also strip a leading "NNN_" gate-number prefix so both
        # "010_required_extension_contract" and "required_extension_contract"
        # resolve to the same context key.
        bare_name = Regex.replace(~r/^\d+_/, name, "")
        acc |> Map.put(name, rows) |> Map.put(bare_name, rows)

      _ ->
        acc
    end
  end)

first_rows =
  Enum.reduce(rows_by_name, %{}, fn {name, rows}, acc ->
    case rows do
      [first | _] -> Map.put(acc, name, first)
      _ -> acc
    end
  end)

base_context =
  rows_by_name
  |> Map.merge(first_rows, fn _k, list, _first -> list end)
  |> Map.new(fn {k, v} -> {k, v} end)

context_label =
  "superset of all real gate/query rows (keys: #{inspect(Map.keys(rows_by_name))}), " <>
    "first-row convenience keys merged in"

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

render_results =
  Enum.map(template_files, fn {name, path} ->
    result = RenderCheck.render_template_file(path, base_context, context_label)

    case result do
      {:missing, ^path} ->
        IO.puts("  #{name}: MISSING (#{path})")

      {:frontmatter_error, reason} ->
        first_line = reason |> String.split("\n") |> List.first()
        IO.puts("  #{name}: FRONTMATTER/SPLIT ERROR: #{first_line}")

      {:ok, {_frontmatter, rendered}} ->
        IO.puts("  #{name}: {:ok, #{byte_size(rendered)}} (rendered length)")

      {:error, reason} ->
        IO.puts("  #{name}: {:error, #{inspect(reason)}}")
    end

    {name, path, result}
  end)

IO.puts("")

templates_rendered_ok =
  Enum.count(render_results, fn {_n, _p, r} -> match?({:ok, {_fm, _rendered}}, r) end)

# ---------------------------------------------------------------------------
# 5. Syntax check every successfully-rendered template; extra compile check
#    for the four core Spark/Ash extension modules.
# ---------------------------------------------------------------------------

IO.puts("-- templates: syntax check --")

syntax_results =
  Enum.map(render_results, fn {name, _path, result} ->
    case result do
      {:ok, {_fm, rendered}} ->
        case Code.string_to_quoted(rendered) do
          {:ok, _quoted} ->
            IO.puts("  #{name}: :valid_syntax")
            {name, :valid_syntax}

          {:error, reason} ->
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
          {:ok, {_fm, rendered}} -> rendered
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
        "lines above for which template and why) for the specific best-effort context " <>
        "shape this script guessed. This does not yet prove or disprove the construct " <>
        "itself works -- it may be this script's context-binding guess, not the renderer, " <>
        "that is wrong for the failing templates."

    templates_rendered_ok == 0 and length(template_files) > 0 ->
      "No template rendered successfully this run (see MISSING/error lines above), so " <>
        "this run provides NO real evidence either confirming or refuting whether " <>
        "TeraWasm handles this pack's `{% if %}`/row-indexed/multi-row constructs -- " <>
        "that remains genuinely untested pending the missing files."

    true ->
      "No templates were checked this run."
  end

IO.puts("DISCLOSURE: #{disclosure}")
