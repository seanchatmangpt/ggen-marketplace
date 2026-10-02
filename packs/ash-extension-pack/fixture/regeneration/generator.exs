# The specimen generator -- the pack's sync/render law in miniature.
#
# `RegenerationSpecimen.Generator.render/1` is a pure function from the
# facts (facts.exs, the ontology in miniature) to generated extension source,
# byte-deterministic: same facts in, same bytes out, every process, every
# epoch. This is the exact property the regeneration court enforces against
# the real pack (ontology -> template render): generated files are never
# authoritative; anything on disk that differs from a fresh render from the
# current facts is a violation, not a truth.

defmodule RegenerationSpecimen.Generator do
  @extension_path "lib/regeneration_specimen/extension.ex"

  def extension_path, do: @extension_path

  def render(facts) do
    %{@extension_path => render_extension(facts)}
  end

  # ------------------------------------------------------------------
  # Type vocabulary -- mirrors ontology.ttl's closed aex:fieldType set.
  # ------------------------------------------------------------------
  defp render_type(%{type: "one_of", one_of: values}) do
    "{:one_of, [#{values |> Enum.map(&(":#{&1}")) |> Enum.join(", ")}]}"
  end

  defp render_type(%{type: "or_string_list_string"}) do
    "{:or, [:string, {:list, :string}]}"
  end

  defp render_type(%{type: t}) when t in ~w(atom string boolean integer any) do
    ":#{t}"
  end

  defp render_type(%{type: "list_atom"}), do: "{:list, :atom}"

  defp render_type(%{type: "list_string"}), do: "{:list, :string}"

  defp render_type(%{type: "module"}), do: ":module"

  # ------------------------------------------------------------------
  # Entity field: exactly one line, so scratch-copy mutations (a league
  # edit) and diffs against a fresh render are line-addressable.
  # ------------------------------------------------------------------
  defp render_field(%{name: name} = f) do
    default = Map.get(f, :default)

    default_src =
      cond do
        is_nil(default) -> "nil"
        String.starts_with?(default, ":") -> default
        true -> inspect(default)
      end

    ~s(%{name: :#{name}, type: #{render_type(f)}, required: #{Map.get(f, :required, false)}, default: #{default_src}})
  end

  defp render_entity_fields(entity) do
    entity.fields
    |> Enum.map(&render_field/1)
    |> Enum.map_join("\n", &("        #{&1},"))
  end

  defp render_entity(entity) do
    identifier =
      case Map.get(entity, :identifier) do
        nil -> "nil"
        id -> ":#{id}"
      end

    """
        %{
          name: :#{entity.name},
          order: #{entity.order},
          struct: #{inspect(entity.struct)},
          identifier: #{identifier},
          args: #{inspect(Enum.map(entity.args, &String.to_atom/1))},
          fields: [
    #{render_entity_fields(entity)}
          ]
        }\
    """
  end

  defp render_section_entities(section) do
    section.entities
    |> Enum.map(&render_entity/1)
    |> Enum.map_join("\n", &(&1 <> ","))
  end

  defp render_sections(facts) do
    facts.sections
    |> Enum.map(fn section ->
      singleton_keys = Enum.map(section.singleton_entity_keys, &String.to_atom/1)

      """
          %{
            name: :#{section.name},
            order: #{section.order},
            describe: #{inspect(section.describe)},
            singleton_entity_keys: #{inspect(singleton_keys)},
            entities: [
      #{render_section_entities(section)}
            ]
          }\
      """
    end)
    |> Enum.join(",\n")
  end

  defp render_verifiers(facts) do
    facts.verifiers
    |> Enum.map_join("\n", fn v ->
      ~s(      {:#{v.name}, #{inspect(v.doc)}},)
    end)
  end

  defp render_info_getters(facts) do
    facts.info_getters
    |> Enum.map_join("\n", fn g ->
      ~s(      %{name: :#{g.name}, source_section: :#{g.source_section}},)
    end)
  end

  defp render_steps(facts) do
    facts.steps
    |> Enum.map(fn s ->
      wait_for = Enum.map(s.wait_for, &String.to_atom/1)

      """
          %{
            name: :#{s.name},
            order: #{s.order},
            module: #{inspect("RegenerationSpecimen.Reactor.Steps.#{s.module}")},
            wait_for: #{inspect(wait_for)},
            max_retries: #{s.max_retries},
            has_compensate: #{s.has_compensate},
            is_return: #{s.is_return},
            scope: :#{s.scope}
          }\
      """
    end)
    |> Enum.join(",\n")
  end

  defp render_persist_after(facts) do
    facts.persist_after
    |> Enum.map_join("\n", &("      #{inspect(&1)},"))
  end

  # ------------------------------------------------------------------
  # The generated extension itself.
  # ------------------------------------------------------------------
  def render_extension(facts) do
    module = facts.module_name
    target_atom = String.to_atom(facts.extension_target)

    """
    # ------------------------------------------------------------------
    # GENERATED -- regeneration specimen extension.
    # Source of truth: the semantic facts (facts.exs / the pack ontology).
    # This file is NEVER authoritative. A byte on disk that differs from a
    # fresh render from the current facts is a violation, not a truth.
    # ------------------------------------------------------------------
    defmodule #{module} do
      @moduledoc \"\"\"
      Generated regeneration specimen extension.

      One Spark-shaped extension surface, derived entirely from declared
      facts: one section (:audit), two entities (:event, :projection),
      two verifiers, one Info getter quadruple, a declared Reactor step
      graph, and an idempotent installer.
      \"\"\"

      @extension_target :#{target_atom}

      @sections [
    #{render_sections(facts)}
      ]

      @verifiers [
    #{render_verifiers(facts)}
      ]

      @info_getters [
    #{render_info_getters(facts)}
      ]

      @steps [
    #{render_steps(facts)}
      ]

      @persist_after [
    #{render_persist_after(facts)}
      ]

      @single_extension_kinds [:#{facts.single_extension_kind}]

      @installer_target "#{facts.installer_target}"

      def extension_target, do: @extension_target

      def sections, do: @sections

      def entities do
        Enum.flat_map(@sections, & &1.entities)
      end

      def verifiers, do: @verifiers

      def info_getters, do: @info_getters

      def steps, do: @steps

      def persist_after, do: @persist_after

      def single_extension_kinds, do: @single_extension_kinds

      def installer_target, do: @installer_target

      @doc \"\"\"
      Declared Info getter quadruple dispatch: every getter resolves to the
      section its `source_section` fact names -- no runtime drift between
      declared and effective sources.
      \"\"\"
      def do_info_get(_dsl_state, getter) do
        case Enum.find(@info_getters, &(&1.name == getter)) do
          nil ->
            {:error, :unknown_getter}

          getter_decl ->
            {:ok, Enum.find(@sections, &(&1.name == getter_decl.source_section))}
        end
      end

      @doc \"\"\"
      The installer, modeled on the pack's Igniter installer law: idempotent
      -- running it against an already-installed dsl_state is a no-op.
      \"\"\"
      def install(dsl_state) do
        dsl_state
        |> Map.put_new(:#{facts.package_name}_installed, true)
        |> Map.put_new(:installed_targets, [@installer_target])
        |> Map.put_new(:installed_single_extension_kinds, @single_extension_kinds)
      end
    end
    """
  end
end
