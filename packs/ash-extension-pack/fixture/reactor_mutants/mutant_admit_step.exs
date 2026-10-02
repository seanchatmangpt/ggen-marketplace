# Hand-written MUTANT step module -- packs/ash-extension-pack/fixture/reactor_mutants/mutant_admit_step.exs
#
# NOT generated, NOT compiled into the consumer fixture (fixture/mix.exs's
# elixirc_paths never include this directory). It is the divergence falsifier for
# templates/reactor_parity_court.exs.tmpl: a hand-mutated copy of the mechanical
# step-module shape templates/reactor_step.ex.tmpl projects, carrying exactly ONE
# behavior no aex:ReactorStep fact implies -- compensate/4, although the step it
# mutates declares aex:stepHasCompensate false (every `admit` row in ontology.ttl
# and qualification/consumer.ttl).
#
# The rendered court locates this file at court runtime (AEX_PACK_ROOT env or
# upward walk, the same pack-root resolution dead_surface_court.exs.tmpl uses),
# renames its module into the specimen's own namespace, compiles it with
# Code.compile_string/1, and runs over it the SAME parity prober that proves the
# faithful generated step modules. The court must report
# {:divergence, :compensate, ...} -- if it ever reports :parity on this file, the
# court is vacuous and must be repaired, not the mutant excused.

defmodule ReactorParityCourt.MutantAdmitStep do
  @moduledoc """
  Mutant of the generated `:admit` step-module shape
  (templates/reactor_step.ex.tmpl): run/3 stays the mechanical projection of the
  step's own identity and arguments, but the module adds compensate/4 although
  aex:stepHasCompensate is false on the `admit` aex:ReactorStep row. No Spark fact
  implies this behavior -- it is implementation/Spark divergence, and the parity
  court must name :compensate as the diverging field.
  """
  use Reactor.Step

  @impl true
  def run(arguments, _context, _options) do
    {:ok, %{step: :admit, arguments: arguments}}
  end

  # DIVERGENCE: undeclared compensation capability. aex:stepHasCompensate is false
  # on the mutated step, so no Spark declaration licenses this callback.
  @impl true
  def compensate(_reason, _arguments, _context, _options), do: :ok
end
