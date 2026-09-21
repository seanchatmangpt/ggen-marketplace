# Golden-vector driver (elixir). Usage: elixir -r src/es/chain.ex driver.exs <golden.vec>
defmodule Driver do
  def run(path) do
    path |> File.read!() |> String.split("\n") |> Enum.reduce([], &step/2)
  end

  defp step("", chain), do: chain
  defp step("#" <> _, chain), do: chain
  defp step("case " <> name, _chain) do
    IO.puts("case " <> name)
    []
  end
  defp step(line, chain) do
    case String.split(line, "|") do
      ["append", id, ph, st, su, ac] -> res(Es.Chain.append(chain, id, ph, st, su, ac), chain)
      ["seal", id, st, su] -> res(Es.Chain.seal(chain, id, st, su), chain)
      ["verify"] ->
        IO.puts("verify " <> to_string(Es.Chain.verify(chain)))
        chain
      ["tamper"] ->
        IO.puts("tampered")
        [%{hd(chain) | subject: "tampered"} | tl(chain)]
    end
  end

  defp res({:ok, c}, _old) do
    IO.puts("ok " <> List.last(c).hash)
    c
  end
  defp res({:error, _}, old) do
    IO.puts("err")
    old
  end
end

Driver.run(hd(System.argv()))
