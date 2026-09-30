# Drives the GENERATED Qri.Gl.Host. argv: wasm_path expected_sha256. stdin: one hex request per line
# (or "@raw:<text>" for a non-hex literal). stdout: one JSON object per request, then a summary line.
[wasm, sha] = System.argv()

encode = fn term -> term |> Jason.encode!() |> IO.puts() end

case Qri.Gl.Host.admit(wasm, sha) do
  {:ok, engine} ->
    for line <- IO.stream(:stdio, :line) do
      line = String.trim(line)
      req = if String.starts_with?(line, "@raw:"), do: String.replace_prefix(line, "@raw:", ""), else: Base.decode16!(line, case: :mixed)

      case Qri.Gl.Host.call(engine, req) do
        {:ok, body} -> encode.(%{"kind" => "ok", "body" => body})
        {:refused, code, detail} -> encode.(%{"kind" => "refused", "code" => to_string(code), "detail" => inspect(detail)})
        {:trap, reason} -> encode.(%{"kind" => "trap", "reason" => inspect(reason)})
      end
    end

    encode.(%{"kind" => "summary", "sha256" => engine.sha256, "memory_bytes" => Wasmex.Memory.size(engine.store, engine.memory)})

  {:refused, code, detail} ->
    encode.(%{"kind" => "admission_refused", "code" => to_string(code), "detail" => inspect(detail)})
    System.halt(3)

  {:unsupported, reason} ->
    encode.(%{"kind" => "admission_unsupported", "reason" => inspect(reason)})
    System.halt(4)
end
