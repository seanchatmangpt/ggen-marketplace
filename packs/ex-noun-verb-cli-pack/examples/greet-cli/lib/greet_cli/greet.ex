defmodule GreetCli.Greet do
  @moduledoc """
  Real handler functions for the `greet` noun, generated once by
  ggen (ex-noun-verb-cli-pack) from `nvc:handlerBodyExpr` playground facts.
  `unless_exists: true` in this template's frontmatter -- like
  clap-noun-verb-crate-pack's `custom_handlers.rs.tmpl` -- means this file is
  scaffolding: a later `ggen sync` re-run never overwrites hand-edits made
  here.
  """

  @doc "Prints a friendly greeting for --name."
  def hello(name), do: "Hello, #{name}!"

  @doc "Prints an uppercase, shouted greeting for --name."
  def shout(name), do: String.upcase("HELLO, #{name}!")

end
