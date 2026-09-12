defmodule GreetCli.Math do
  @moduledoc """
  Real handler functions for the `math` noun, generated once by
  ggen (ex-noun-verb-cli-pack) from `nvc:handlerBodyExpr` playground facts.
  `unless_exists: true` in this template's frontmatter -- like
  clap-noun-verb-crate-pack's `custom_handlers.rs.tmpl` -- means this file is
  scaffolding: a later `ggen sync` re-run never overwrites hand-edits made
  here.
  """

  @doc "Adds --x and --y."
  def add(x, y), do: x + y

  @doc "Multiplies --x and --y."
  def multiply(x, y), do: x * y

end
