# Shared court kit for the regeneration specimen (Lane C9).
#
# Loaded by all three courts (templates/regeneration_court.exs.tmpl,
# drift_court.exs.tmpl, mutation_league.exs.tmpl) via Code.eval_file. Holds
# only real machinery -- facts loading, the generator, compile + real
# introspection snapshots, deterministic digests. No test doubles: the
# specimen is compiled for real with Code.compile_string/1 and probed for
# real (getter dispatch, installer idempotence) on every snapshot.

defmodule RegenerationSpecimen.Kit do
  @extension_path "lib/regeneration_specimen/extension.ex"

  def extension_path, do: @extension_path

  def court_failure(message) do
    raise "COURT FAILURE: " <> message
  end

  def assert!(true, _message), do: :ok
  def assert!(false, message), do: court_failure(message)

  # ---------------------------------------------------------------
  # Facts + generator
  # ---------------------------------------------------------------
  def load_facts(specimen_root) do
    {facts, _} = Code.eval_file(Path.join(specimen_root, "facts.exs"), specimen_root)
    facts
  end

  def ensure_generator(specimen_root) do
    case Code.ensure_loaded(RegenerationSpecimen.Generator) do
      {:module, _} ->
        :ok

      _ ->
        Code.eval_file(Path.join(specimen_root, "generator.exs"), specimen_root)
        :ok
    end
  end

  def render(facts) do
    apply(RegenerationSpecimen.Generator, :render, [facts])
  end

  def render_extension(facts) do
    render(facts)[@extension_path]
  end

  def sha256(source), do: Base.encode16(:crypto.hash(:sha256, source), case: :lower)

  # ---------------------------------------------------------------
  # Compile + introspect for real
  # ---------------------------------------------------------------
  def compile(source) do
    [{mod, _binary}] = Code.compile_string(source)
    mod
  end

  @doc """
  A full semantic snapshot of the compiled specimen: the compiled module's
  real export list, every declared surface, real runtime probes (getter
  dispatch, installer idempotence), and a static side-effect scan of the
  source AST for undeclared hidden configuration (:persistent_term /
  :application mutation). Digest-stable for an unchanged DSL; anything that
  silently alters extension meaning moves this term.
  """
  def snapshot(source) do
    mod = compile(source)
    ast = Code.string_to_quoted!(source)

    first_install = mod.install(%{})
    second_install = mod.install(first_install)

    %{
      exports: mod.module_info(:functions) |> Enum.sort(),
      extension_target: mod.extension_target(),
      sections: mod.sections(),
      verifiers: mod.verifiers(),
      info_getters: mod.info_getters(),
      steps: mod.steps(),
      persist_after: mod.persist_after(),
      single_extension_kinds: mod.single_extension_kinds(),
      installer_target: mod.installer_target(),
      getter_probe: mod.do_info_get(%{}, :audit_index),
      installer_probe: %{
        first: first_install,
        idempotent: first_install == second_install
      },
      side_effects: side_effects(ast)
    }
  end

  def digest(source), do: :erlang.phash2(snapshot(source))

  @side_effect_calls [:persistent_term, :application]

  defp side_effects(ast) do
    {_, found} =
      Macro.prewalk(ast, [], fn
        {{:., _, [mod, fun]}, _, _args} = node, acc
        when is_atom(mod) and is_atom(fun) and mod in @side_effect_calls and
               fun in [:put, :put_env, :put_all_env] ->
          {node, [node | acc]}

        node, acc ->
          {node, acc}
      end)

    found
    |> Enum.reverse()
    |> Enum.map(fn {{:., meta, [mod, fun]}, _, _args} ->
      %{call: "#{mod}.#{fun}", line: meta[:line]}
    end)
  end
end
