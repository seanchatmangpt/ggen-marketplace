defmodule Mix.Tasks.MarketplaceCliTest do
  use ExUnit.Case, async: false

  # Real subprocess Chicago-style test: runs the real Mix task in this real
  # consumer project, not a mocked Igniter pipeline.
  test "mix marketplace_cli.validate runs for real and prints the validated line" do
    {output, 0} = System.cmd("mix", ["marketplace_cli.validate", "--yes"], stderr_to_stdout: true)
    assert output =~ "validated packs="
  end

  test "mix marketplace_cli.catalog runs for real and prints JSON" do
    {output, 0} = System.cmd("mix", ["marketplace_cli.catalog", "--yes"], stderr_to_stdout: true)
    assert output =~ "\"schema\""
    assert output =~ "marketplace_version"
  end
end
