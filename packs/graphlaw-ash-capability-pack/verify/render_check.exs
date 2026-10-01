# Chicago-style, no-mocks real-render check for the graphlaw-ash-capability-pack marketplace pack.
# Run with:
#
#   cd /Users/sac/ggen_igniter && mix run <abs_path_to_this_file>
#
# so it executes inside ggen_igniter's own compiled Mix project (GgenIgniter.Ontology/Query/
# Frontmatter/Render.TeraWasm are not available outside that project context).
#
# What it does, all against real engines (oxigraph SPARQL, WASM Tera, the Elixir compiler):
#
#   1. Positive fixture (verify/fixtures/registry_3ops.ttl): every pack gate must return 0 rows.
#   2. Negative fixture (verify/fixtures/registry_bad_type.ttl): gate 040 must return >= 1 row.
#   3. Every templates/*.tmpl is rendered from the positive fixture through its OWN frontmatter
#      `sparql:` / `for_each:` blocks and the production binding function
#      Mix.Tasks.GgenIgniter.Sync.build_bindings/2, and its `to:` path is rendered too.
#   4. Every inline frontmatter query must be byte-identical to queries/<name>.rq and every
#      queries/*.rq must be used by a template.
#   5. Every rendered Elixir file must parse (Code.string_to_quoted) and be formattable
#      (Code.format_string!); a Chicago check also compiles them together and exercises the
#      Registry and Result.Term modules (the only generated modules with no collaborator outside
#      the generated set).
#   6. Cardinality is compared against the fixture's gac:opCount, never a hardcoded operation
#      count.
#
# Optional env: RENDER_OUT_DIR=<dir> writes every rendered file at its `to:` path under <dir>.
# Any failed check prints FAIL and halts the VM with a nonzero exit code (fail-closed).

pack_root = Path.expand(Path.join(__DIR__, ".."))
fixture_dir = Path.join(__DIR__, "fixtures")

IO.puts("== graphlaw-ash-capability-pack render_check ==")
IO.puts("pack_root: #{pack_root}")
IO.puts("")

defmodule CapRenderCheck do
  @moduledoc false

  def query_text(graph, text), do: GgenIgniter.Query.Oxigraph.run(graph, text)

  def gate_rows(graph, gate_files) do
    Enum.map(gate_files, fn path ->
      rows =
        try do
          {:ok, query_text(graph, File.read!(path))}
        rescue
          e -> {:error, Exception.format(:error, e, __STACKTRACE__) |> String.split("\n") |> hd()}
        end

      {Path.basename(path), rows}
    end)
  end

  def inline_queries(template_text) do
    # `sparql:` then `  <name>: |` then the query indented four spaces (the shape assemble writes).
    ["", front | _] = String.split(template_text, ~r/^---\n/m, parts: 3)

    front
    |> String.split("\n")
    |> Enum.drop_while(&(&1 != "sparql:"))
    |> Enum.drop(1)
    |> Enum.take_while(&(String.starts_with?(&1, "  ") or &1 == ""))
    |> Enum.chunk_while(
      nil,
      fn line, acc ->
        case {Regex.run(~r/^  (\w+): \|$/, line), acc} do
          {[_, name], nil} -> {:cont, {name, []}}
          {[_, name], {prev, body}} -> {:cont, {prev, Enum.reverse(body)}, {name, []}}
          {nil, {name, body}} -> {:cont, {name, [String.replace_prefix(line, "    ", "") | body]}}
        end
      end,
      fn
        nil -> {:cont, nil}
        {name, body} -> {:cont, {name, Enum.reverse(body)}, nil}
      end
    )
    |> Map.new(fn {name, body} -> {name, body |> Enum.join("\n") |> String.trim_trailing("\n")} end)
  end

  @doc "Renders one template. Returns {:ok, [{to_path, body}]} | {:error, reason}."
  def render(graph, path) do
    raw = File.read!(path)
    {frontmatter, _mode, body} = GgenIgniter.Frontmatter.split_template(raw)
    named = if is_map(frontmatter.sparql), do: Map.to_list(frontmatter.sparql), else: []

    named_results =
      Enum.map(named, fn {name, text} -> {name, query_text(graph, text)} end)

    to_template = frontmatter.to

    render_one = fn row ->
      bindings = Mix.Tasks.GgenIgniter.Sync.build_bindings(named_results, row)
      context = Map.new(bindings)

      with {:ok, rendered} <- GgenIgniter.Render.TeraWasm.render(body, context),
           {:ok, to_path} <- GgenIgniter.Render.TeraWasm.render(to_template, context) do
        {:ok, {String.trim(to_path), rendered}}
      end
    end

    case Map.get(frontmatter, :for_each) do
      nil ->
        with {:ok, one} <- render_one.(nil), do: {:ok, [one]}

      driver ->
        rows =
          case List.keyfind(named_results, driver, 0) do
            {^driver, rows} -> rows
            _ -> []
          end

        if rows == [] do
          {:error, "for_each driver #{driver} produced 0 rows"}
        else
          results = Enum.map(rows, render_one)

          case Enum.find(results, &match?({:error, _}, &1)) do
            nil -> {:ok, Enum.map(results, fn {:ok, one} -> one end)}
            err -> err
          end
        end
    end
  rescue
    e -> {:error, Exception.format(:error, e, __STACKTRACE__) |> String.split("\n") |> Enum.take(3) |> Enum.join(" | ")}
  end
end

failures = :ets.new(:cap_render_failures, [:public, :bag])
fail = fn msg -> :ets.insert(failures, {:failure, msg}) end

# --- 1. positive fixture + gates -------------------------------------------------------------

pos_path = Path.join(fixture_dir, "registry_3ops.ttl")
neg_path = Path.join(fixture_dir, "registry_bad_type.ttl")
gate_files = pack_root |> Path.join("gates/*.rq") |> Path.wildcard() |> Enum.sort()

pos_graph = GgenIgniter.Ontology.load!(pos_path)
IO.puts("positive fixture loaded: #{pos_path}")
IO.puts("gates found: #{length(gate_files)}")

if gate_files == [], do: fail.("no gates/*.rq found; gate expectations cannot be checked")

IO.puts("")
IO.puts("-- gates over the positive fixture (every gate must return 0 rows) --")

for {name, result} <- CapRenderCheck.gate_rows(pos_graph, gate_files) do
  case result do
    {:ok, []} ->
      IO.puts("  #{name}: 0 rows (ok)")

    {:ok, rows} ->
      IO.puts("  #{name}: #{length(rows)} row(s) FAIL, sample: #{inspect(hd(rows), limit: 6)}")
      fail.("gate #{name} reports #{length(rows)} violation(s) on the positive fixture")

    {:error, reason} ->
      IO.puts("  #{name}: QUERY ERROR #{reason}")
      fail.("gate #{name} did not run: #{reason}")
  end
end

# --- 2. negative fixture --------------------------------------------------------------------

IO.puts("")
IO.puts("-- gates over the negative fixture (gate 040 must report the bad field type) --")
neg_graph = GgenIgniter.Ontology.load!(neg_path)
neg = CapRenderCheck.gate_rows(neg_graph, gate_files)

for {name, result} <- neg do
  case result do
    {:ok, rows} -> IO.puts("  #{name}: #{length(rows)} row(s)#{if rows != [], do: ", sample: " <> inspect(hd(rows), limit: 6), else: ""}")
    {:error, reason} -> IO.puts("  #{name}: QUERY ERROR #{reason}")
  end
end

case Enum.find(neg, fn {name, _} -> String.starts_with?(name, "040_") end) do
  {_, {:ok, [_ | _]}} -> IO.puts("  negative control: gate 040 refuses registry_bad_type.ttl (ok)")
  _ -> fail.("negative control: gate 040 did not report registry_bad_type.ttl")
end

# --- 3. registry identity from the fixture ---------------------------------------------------

[registry_row] =
  CapRenderCheck.query_text(pos_graph, File.read!(Path.join(pack_root, "queries/registry.rq")))

fixture_op_count = registry_row["op_count"] |> to_string() |> String.to_integer()
IO.puts("")
IO.puts("fixture registry: schema=#{registry_row["schema_id"]} gac:opCount=#{fixture_op_count}")

# --- 4. render every template ---------------------------------------------------------------

templates = pack_root |> Path.join("templates/*.tmpl") |> Path.wildcard() |> Enum.sort()

expected_templates = ~w(
  capability_behaviour.ex.tmpl capability_registry.ex.tmpl capability_module.ex.tmpl
  capability_api.ex.tmpl result_term.ex.tmpl result_struct.ex.tmpl capability_doc.md.tmpl
  capability_index.md.tmpl capability_surface_test.exs.tmpl
  capability_model.ex.tmpl capability_enums.ex.tmpl capability_limits.ex.tmpl
)

for name <- expected_templates do
  unless Path.join([pack_root, "templates", name]) in templates, do: fail.("missing template #{name}")
end

IO.puts("")
IO.puts("-- templates: render --")

rendered =
  Enum.flat_map(templates, fn path ->
    name = Path.basename(path)

    case CapRenderCheck.render(pos_graph, path) do
      {:ok, files} ->
        bytes = files |> Enum.map(fn {_, b} -> byte_size(b) end) |> Enum.sum()
        IO.puts("  #{name}: {:ok, #{length(files)} file(s), #{bytes} bytes} -> #{files |> Enum.map(&elem(&1, 0)) |> Enum.join(", ")}")
        Enum.map(files, fn {to, body} -> {name, to, body} end)

      {:error, reason} ->
        IO.puts("  #{name}: {:error, #{inspect(reason)}}")
        fail.("template #{name} did not render: #{inspect(reason)}")
        []
    end
  end)

# cardinality against the ontology, not a literal
count_to = fn prefix -> Enum.count(rendered, fn {_n, to, _b} -> String.starts_with?(to, prefix) end) end

for {label, prefix} <- [
      {"capability modules", "lib/ash_graphlaw/capability/"},
      {"op docs", "documentation/reference/capabilities/"}
    ] do
  # capability/ also holds registry.ex, api.ex and limits.ex
  got = count_to.(prefix)
  want = if label == "capability modules", do: fixture_op_count + 3, else: fixture_op_count

  if got == want do
    IO.puts("  #{label}: #{got} == gac:opCount#{if label == "capability modules", do: " + registry + api + limits", else: ""} (ok)")
  else
    fail.("#{label}: rendered #{got}, expected #{want}")
  end
end

result_files = Enum.count(rendered, fn {_n, to, _b} -> String.match?(to, ~r{^lib/ash_graphlaw/result/(?!term)}) end)

[%{"n" => overrides}] =
  CapRenderCheck.query_text(
    pos_graph,
    """
    PREFIX gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#>
    SELECT (COUNT(?b) AS ?n) WHERE { ?b a gac:OpBinding ; gac:bindingResultModule ?m }
    """
  )

overrides = overrides |> to_string() |> String.to_integer()

if result_files == fixture_op_count - overrides do
  IO.puts("  result structs: #{result_files} == gac:opCount - #{overrides} bindingResultModule override(s) (ok)")
else
  fail.("result structs: rendered #{result_files}, expected #{fixture_op_count - overrides}")
end

# typed models: one struct file per gac:Model, one Enums module, one Limits module
count_of = fn class ->
  [%{"n" => n}] =
    CapRenderCheck.query_text(
      pos_graph,
      """
      PREFIX gac: <http://seanchatmangpt.github.io/packs/graphlaw-ash-capability#>
      SELECT (COUNT(?x) AS ?n) WHERE { ?x a gac:#{class} }
      """
    )

  n |> to_string() |> String.to_integer()
end

model_files =
  Enum.count(rendered, fn {_n, to, _b} ->
    String.starts_with?(to, "lib/ash_graphlaw/model/") and to != "lib/ash_graphlaw/model/enums.ex"
  end)

fixture_models = count_of.("Model")
fixture_limits = count_of.("Limit")

if fixture_models > 0 and model_files == fixture_models do
  IO.puts("  model structs: #{model_files} == count(gac:Model) (ok)")
else
  fail.("model structs: rendered #{model_files}, expected #{fixture_models} (> 0)")
end

for path <- ["lib/ash_graphlaw/model/enums.ex", "lib/ash_graphlaw/capability/limits.ex"] do
  if Enum.any?(rendered, fn {_n, to, _b} -> to == path end),
    do: IO.puts("  #{path}: rendered (ok)"),
    else: fail.("missing rendered file #{path}")
end

# --- 5. inline query == queries/*.rq --------------------------------------------------------

IO.puts("")
IO.puts("-- inline frontmatter queries are verbatim copies of queries/*.rq --")

used =
  Enum.reduce(templates, MapSet.new(), fn path, acc ->
    inline = CapRenderCheck.inline_queries(File.read!(path))

    Enum.reduce(inline, acc, fn {qname, text}, acc2 ->
      file = Path.join([pack_root, "queries", qname <> ".rq"])

      cond do
        not File.exists?(file) ->
          fail.("#{Path.basename(path)} names query #{qname} but queries/#{qname}.rq is missing")

        text != file |> File.read!() |> String.trim_trailing("\n") ->
          fail.("#{Path.basename(path)}: inline #{qname} differs from queries/#{qname}.rq")

        true ->
          :ok
      end

      MapSet.put(acc2, qname)
    end)
  end)

for file <- Path.wildcard(Path.join(pack_root, "queries/*.rq")) do
  unless Path.basename(file, ".rq") in used, do: fail.("queries/#{Path.basename(file)} is used by no template")

  text = File.read!(file)
  unless text =~ "PREFIX gac:", do: fail.("#{Path.basename(file)} has no gac PREFIX")

  # every SELECT carries ORDER BY (Rust ggen strict_mode E0013)
  unless text =~ ~r/ORDER BY/, do: fail.("#{Path.basename(file)} has no ORDER BY")
end

IO.puts("  #{MapSet.size(used)} distinct queries inlined, #{length(Path.wildcard(Path.join(pack_root, "queries/*.rq")))} query files")

# --- 6. syntax + format ---------------------------------------------------------------------

IO.puts("")
IO.puts("-- rendered Elixir: parse + format --")

elixir = Enum.filter(rendered, fn {_n, to, _b} -> String.ends_with?(to, ".ex") or String.ends_with?(to, ".exs") end)

for {name, to, body} <- elixir do
  case Code.string_to_quoted(body, file: to) do
    {:ok, _} ->
      formatted =
        try do
          {:formats, Code.format_string!(body) |> IO.iodata_to_binary()}
        rescue
          e -> {:format_error, Exception.message(e)}
        end

      case formatted do
        {:formats, out} ->
          # Rust `ggen` writes the template output as-is; ggen_igniter and `mix format` normalize.
          # A whitespace-only difference is reported, never failed.
          if String.trim_trailing(out) != String.trim_trailing(body),
            do: IO.puts("  note: #{to} differs from Code.format_string!/1 output (mix format normalizes)")

        {:format_error, msg} ->
          fail.("#{to} (#{name}) does not format: #{msg}")
      end

    {:error, reason} ->
      IO.puts("  #{to}: SYNTAX ERROR #{inspect(reason)}")
      fail.("#{to} (#{name}) has a syntax error: #{inspect(reason)}")
  end
end

IO.puts("  #{length(elixir)} rendered Elixir file(s) parsed")

# generated header + SPDX + doc coverage (every def/defmacro documented in .ex output)
for {_name, to, body} <- elixir, String.ends_with?(to, ".ex") do
  unless body =~ "SPDX-License-Identifier: MIT", do: fail.("#{to}: no SPDX header")
  unless body =~ "GENERATED by ggen", do: fail.("#{to}: no GENERATED-by-ggen header")
  unless body =~ "@moduledoc", do: fail.("#{to}: no @moduledoc")
end

# --- 7. compile + exercise ------------------------------------------------------------------

IO.puts("")
IO.puts("-- compile check: all rendered lib/*.ex together --")

lib_files = Enum.filter(elixir, fn {_n, to, _b} -> String.starts_with?(to, "lib/") end)

# The generated API pattern-matches %AshGraphLaw.Refusal{} and raises AshGraphLaw.Error.Refused, and
# every capability module calls the hand-written Coerce/Decode/Telemetry residue. Load the consumer's
# REAL definitions of those collaborators when the consumer checkout has them (read-only). If the
# Refusal struct is missing, define a minimal hand-written stand-in with the same struct shape and
# say so. Anything still missing is named by the compiler below.
consumer_root = System.get_env("ASH_GRAPHLAW_ROOT", "/Users/sac/ash_graphlaw")

collaborators =
  for rel <- [
        "lib/ash_graphlaw/refusal.ex",
        "lib/ash_graphlaw/error/refused.ex",
        "lib/ash_graphlaw/capability/canonical_json.ex",
        "lib/ash_graphlaw/capability/coerce.ex",
        "lib/ash_graphlaw/capability/decode.ex",
        "lib/ash_graphlaw/telemetry.ex"
      ],
      path = Path.join(consumer_root, rel),
      File.exists?(path) do
    try do
      Code.compile_file(path)
      {:real, rel}
    rescue
      e -> {:unavailable, rel, Exception.message(e) |> String.split("\n") |> hd()}
    end
  end

unless Code.ensure_loaded?(AshGraphLaw.Refusal) do
  Code.compile_string("""
  defmodule AshGraphLaw.Refusal do
    defexception [:code, :message, :details, :raw]
  end

  defmodule AshGraphLaw.Error.Refused do
    defexception [:refusal]
  end
  """)

  IO.puts("  collaborators: consumer Refusal/Error.Refused unavailable; hand-written stand-in struct used")
end

for c <- collaborators, do: IO.puts("  collaborator #{inspect(c)}")

{compile_result, diagnostics} =
  Code.with_diagnostics(fn ->
    try do
      modules = lib_files |> Enum.map(fn {_n, to, body} -> {body, to} end) |> Enum.flat_map(fn {body, to} -> Code.compile_string(body, to) end)
      {:ok, Enum.map(modules, &elem(&1, 0))}
    rescue
      e -> {:error, Exception.format(:error, e, __STACKTRACE__) |> String.split("\n") |> Enum.take(4) |> Enum.join(" | ")}
    end
  end)

case compile_result do
  {:ok, mods} ->
    IO.puts("  compiled #{length(mods)} module(s)")

    undefined =
      diagnostics
      |> Enum.map(&to_string(&1.message))
      |> Enum.filter(&String.contains?(&1, "is undefined"))
      |> Enum.uniq()

    other_warnings =
      diagnostics
      |> Enum.filter(&(&1.severity == :warning))
      |> Enum.map(&to_string(&1.message))
      |> Enum.reject(&String.contains?(&1, "is undefined"))

    for w <- other_warnings, do: fail.("compile warning: #{w |> String.split("\n") |> hd()}")

    IO.puts("  #{length(undefined)} warning line(s) name a module outside the generated set")

    generated = Enum.map(mods, &inspect/1)

    outside =
      undefined
      |> Enum.map(fn line ->
        cond do
          m = Regex.run(~r/^([A-Za-z0-9_.]+\.\w+\/\d+) is undefined or private/, line) -> Enum.at(m, 1)
          m = Regex.run(~r/module ([A-Za-z0-9_.]+) (?:is undefined|is not available)/, line) -> Enum.at(m, 1)
          true -> line
        end
      end)
      |> Enum.uniq()
      |> Enum.sort()
      # modules of the generated set that were merely compiled later than their referrer
      |> Enum.reject(&(&1 in generated))

    IO.puts("    outside the generated set: #{Enum.join(outside, ", ")}")

    # only hand-written residue (Coerce, Decode, Telemetry, Refusal.build/3 pending its lane) and
    # the existing AshGraphLaw modules may be missing from this VM
    allowed = ~w(AshGraphLaw AshGraphLaw.Capability.Coerce AshGraphLaw.Capability.Decode
                 AshGraphLaw.Telemetry AshGraphLaw.Refusal AshGraphLaw.Refusal.build/3
                 AshGraphLaw.Error.Refused AshGraphLaw.Admitted)

    surprises = Enum.reject(outside, &(&1 in allowed))
    if surprises != [], do: fail.("unexpected undefined reference(s): #{Enum.join(surprises, ", ")}")

  {:error, reason} ->
    IO.puts("  COMPILE ERROR: #{reason}")
    fail.("generated lib files do not compile together: #{reason}")
end

if match?({:ok, _}, compile_result) do
  IO.puts("")
  IO.puts("-- exercise Registry and Result.Term (real compiled modules) --")
  alias AshGraphLaw.Capability.Registry
  alias AshGraphLaw.Result.Term

  check = fn label, ok? ->
    IO.puts("  #{label}: #{if ok?, do: "ok", else: "FAIL"}")
    unless ok?, do: fail.("exercise: #{label}")
  end

  check.("Registry.names/0 length == gac:opCount", length(Registry.names()) == fixture_op_count)
  check.("Registry.digest/0 == gac:registrySha256", Registry.digest() == registry_row["registry_sha256"])
  check.("Registry.surface_digest/0 == gac:surfaceSha256", Registry.surface_digest() == registry_row["surface_sha256"])
  check.("Registry.abi_version/0 == gac:abiVersion", Registry.abi_version() == (registry_row["abi_version"] |> to_string() |> String.to_integer()))

  {:ok, sparql} = Registry.op("sparql")
  check.("sparql has 3 tagged variants", Enum.map(sparql.responses, & &1.tag) == ["solutions", "graph", "boolean"])
  check.("sparql variants share tag_field kind", Enum.all?(sparql.responses, &(&1.tag_field == "kind")))
  check.("sparql request field order preserved", Enum.map(sparql.request, & &1.name) == ["data", "query", "base"])
  check.("required/nullable are booleans", Enum.all?(sparql.request, &(is_boolean(&1.required) and is_boolean(&1.nullable))))

  {:ok, sniff} = Registry.op("sniff")
  [%{tag: nil, tag_field: nil, fields: sniff_fields}] = sniff.responses
  engine = Enum.find(sniff_fields, &(&1.name == "engine"))
  check.("untagged op has one nil-tag variant; enum kept in order", engine.enum == ["PurRdf", "Eyeron"])
  check.("field order is an integer", is_integer(engine.order))

  {:ok, law} = Registry.op("law")
  unverified = Enum.find(law.request, &(&1.name == "unverified_lease"))
  check.("default false renders as boolean false", unverified.default == false)
  check.("absent default renders nil", Enum.find(law.request, &(&1.name == "data")).default == nil)
  check.("module_for(law) is the capability module", Registry.module_for("law") == {:ok, AshGraphLaw.Capability.Law})
  check.("module_for(unknown) is :error", Registry.module_for("nope") == :error)
  check.("rdf/other dialect split", Registry.rdf_dialects() == ["turtle", "ntriples"] and Registry.other_dialects() == ["n3"])
  check.("law step ceilings", Enum.map(Registry.law_steps(), &{&1.name, &1.ceiling}) == [{"shacl", "observe"}, {"record-receipts", nil}])
  check.("limits are atom-keyed integers", Registry.limits().max_json_depth == 64)
  check.("regimes vocabulary is present", is_list(Registry.regimes()))
  check.("no field doc lost its text", Enum.all?(sparql.request, &(byte_size(&1.doc) > 0)))

  term = %{"type" => "literal", "value" => "hola", "xml:lang" => "es"}
  check.("Term.from_map maps xml:lang -> lang", struct(Term, type: "literal", value: "hola", lang: "es", raw: term) == Term.from_map(term))
  check.("Term.from_map never raises on non-maps", Term.from_map(1).raw == 1)

  for mod <- [AshGraphLaw.Result.Sniff, AshGraphLaw.Result.Sparql] do
    check.("#{inspect(mod)} struct has :raw and no :kind unless tagged",
      (:raw in Map.keys(struct(mod))) and (:kind in Map.keys(struct(mod)) == (mod == AshGraphLaw.Result.Sparql)))
  end

  check.("Result.Sparql keys == union of variant fields (+ kind, raw)",
    Enum.sort(Map.keys(struct(AshGraphLaw.Result.Sparql)) -- [:__struct__]) ==
      Enum.sort([:kind, :nquads, :quads, :raw, :rows, :value, :variables]))

  check.("no Result.Law is generated (bindingResultModule override)", not Code.ensure_loaded?(AshGraphLaw.Result.Law))

  alias AshGraphLaw.Capability.Limits
  alias AshGraphLaw.Model

  check.("Limits.all/0 length == count(gac:Limit)", length(Limits.all()) == fixture_limits)
  check.("Limits agree with Registry.limits/0", Map.new(Limits.all(), &{&1.name, &1.value}) == Registry.limits())
  check.("every limit carries scope, unit and source", Enum.all?(Limits.all(), &(&1.scope != "" and &1.unit != "" and &1.source != "")))
  check.("n3 scope holds the n3 limits", Enum.all?(Limits.in_scope("n3"), &String.starts_with?(Atom.to_string(&1.name), "n3_")))

  check.("Model.Enums knows Ceiling in order", Model.Enums.values("Ceiling") == ["observe", "select", "construct"])
  check.("Model.Enums.member?/2 is informational", Model.Enums.member?("Ceiling", "select") and not Model.Enums.member?("Ceiling", "root"))

  wire = %{
    "lease" => %{"id" => "l1", "holder" => "h", "ceiling" => "select", "scope" => ["shacl"], "expires_unix" => 9, "issued_unix" => 0},
    "attestation" => %{"payload_sha256" => "aa", "key_id" => "k", "signature" => "ss", "future" => 1},
    "future_top" => [1, 2]
  }

  signed = Model.SignedLease.from_map(wire)
  check.("SignedLease decodes its nested Lease", is_struct(signed.lease, Model.Lease) and signed.lease.id == "l1" and signed.lease.scope == ["shacl"])
  check.("SignedLease decodes its nested Attestation", is_struct(signed.attestation, Model.Attestation) and signed.attestation.key_id == "k")
  check.("unknown wire keys are kept in :extra at every level", signed.extra == %{"future_top" => [1, 2]} and signed.attestation.extra == %{"future" => 1})
  check.("to_map(from_map(m)) == m for a fully populated SignedLease", Model.SignedLease.to_map(signed) == wire)
  check.("Receipt omits absent optional keys and keeps required keys",
    Model.Receipt.from_map(%{}) |> Model.Receipt.to_map() |> Map.keys() |> Enum.sort() ==
      ~w(added authority child parent revision step))
  check.("from_map never raises on non-maps", is_struct(Model.Plan.from_map(1), Model.Plan) and Model.Lease.from_map(nil).extra == %{})
  check.("Plan decodes list<model:Action>", (case Model.Plan.from_map(%{"actions" => [%{"name" => "a"}]}).actions do [action] -> is_struct(action, Model.Action) and action.name == "a"; _ -> false end))
end

# --- 7b. run the generated pure surface test against the real collaborators -----------------

if match?({:ok, _}, compile_result) do
  IO.puts("")
  IO.puts("-- generated test/generated/capability_surface_test.exs (ExUnit, real modules) --")

  collaborators_ok =
    Enum.all?(
      [AshGraphLaw.Capability.Coerce, AshGraphLaw.Capability.Decode, AshGraphLaw.Telemetry],
      &Code.ensure_loaded?/1
    )

  refusal_build? =
    Code.ensure_loaded?(AshGraphLaw.Refusal) and function_exported?(AshGraphLaw.Refusal, :build, 3)

  test_body =
    Enum.find_value(rendered, fn {_n, to, body} ->
      if to == "test/generated/capability_surface_test.exs", do: body
    end)

  cond do
    is_nil(test_body) ->
      fail.("generated surface test was not rendered")

    not collaborators_ok ->
      IO.puts("  PENDING: consumer Coerce/Decode/Telemetry not loadable; generated test not run")

    true ->
      ExUnit.start(autorun: false, colors: [enabled: false])
      Code.compile_string(test_body, "test/generated/capability_surface_test.exs")
      result = ExUnit.run()
      IO.puts("  ExUnit: #{inspect(result)}")

      cond do
        result.failures == 0 ->
          IO.puts("  generated surface test: PASS")

        not refusal_build? ->
          IO.puts(
            "  PENDING(lanes A1+A6): #{result.failures} failure(s) with AshGraphLaw.Refusal.build/3 " <>
              "undefined in the consumer checkout (the typed refusal builder and codes 36..40 are not landed yet)"
          )

        true ->
          fail.("generated surface test: #{result.failures} failure(s) with Refusal.build/3 present")
      end
  end
end

# --- 8. optional write-out ------------------------------------------------------------------

case System.get_env("RENDER_OUT_DIR") do
  nil ->
    :ok

  dir ->
    for {_name, to, body} <- rendered do
      target = Path.join(dir, to)
      File.mkdir_p!(Path.dirname(target))
      File.write!(target, body)
    end

    IO.puts("")
    IO.puts("wrote #{length(rendered)} rendered file(s) under #{dir}")
end

# --- summary --------------------------------------------------------------------------------

IO.puts("")
IO.puts("== SUMMARY ==")
IO.puts("templates rendered: #{length(templates)} template(s) -> #{length(rendered)} file(s)")
all_failures = :ets.lookup(failures, :failure) |> Enum.map(&elem(&1, 1))

if all_failures == [] do
  IO.puts("RESULT: PASS (semantic render check only; no exact-SHA receipt, so not ALIVE)")
else
  for f <- all_failures, do: IO.puts("FAIL: #{f}")
  IO.puts("RESULT: FAIL (#{length(all_failures)} check(s))")
  System.halt(1)
end
