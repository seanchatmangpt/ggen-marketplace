# SPDX-License-Identifier: MIT
# Replays op-examples.json through the real Elixir host (AshAffidavit) and prints one JSON object
# {op_index: response} on stdout. Run from the ash_affidavit checkout: mix run --no-start <this> <examples>.
[examples_path] = System.argv()
{:ok, _} = Application.ensure_all_started(:jason)
{:ok, _} = AshAffidavit.Pool.start_link(size: 1)

examples = examples_path |> File.read!() |> Jason.decode!() |> Map.fetch!("examples")

out =
  examples
  |> Enum.with_index()
  |> Map.new(fn {example, index} ->
    {:ok, response} = AshAffidavit.call(example["request"])
    {"#{index}:#{example["op"]}", response}
  end)

IO.puts(Jason.encode!(out))
