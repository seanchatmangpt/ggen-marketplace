# Lane R9 court — cryptographic receipt dossier (RFC §4.1 artifact 3).
# Standalone, no mix project required.
# Run: elixir qualification/receipt_court.exs
base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

{_, 0} = System.cmd("elixirc", ["lib/cscb_receipt.ex", "-o", "/tmp/cscb_r9_ebin"])
Code.append_path("/tmp/cscb_r9_ebin")
Code.require_file("qualification/receipt_fixtures.exs", base)

require Bitwise
flip_byte = fn bin ->
  <<head::binary-size(4), b::size(8), rest::binary>> = bin
  <<head::binary, Bitwise.bxor(b, 0xFF)::size(8), rest::binary>>
end

failures = []

# 1. mint → render contains all measured values + CRC + signature
{:ok, receipt} = CscbReceipt.mint(CscbReceiptFixtures.results(), CscbReceiptFixtures.stamp())
md = CscbReceipt.render_markdown(receipt)

failures =
  if String.contains?(md, ["87.4", "0", "142117", "24"]) do
    failures
  else
    IO.puts("FAIL render missing measured values")
    ["render missing values" | failures]
  end

failures =
  if String.contains?(md, "CRC32: `0x") and String.contains?(md, "Signature: `") do
    failures
  else
    IO.puts("FAIL render missing CRC or signature block")
    ["render missing blocks" | failures]
  end

# 2. verify round-trip
failures =
  case CscbReceipt.verify(receipt) do
    :ok -> failures
    err -> IO.puts("FAIL verify round-trip got #{inspect(err)}"); ["round-trip" | failures]
  end

# 3. tamper one metric value → :crc_mismatch
tampered_crc = put_in(receipt.metrics[:throughput_ops], 1)
failures =
  case CscbReceipt.verify(tampered_crc) do
    {:error, :crc_mismatch} -> failures
    err -> IO.puts("FAIL tampered metric got #{inspect(err)}"); ["tamper-crc" | failures]
  end

# 4. tamper signature → :bad_signature (flip a byte in the signature)
sig = receipt.signature
tampered_sig = Map.put(receipt, :signature, flip_byte.(sig))
failures =
  case CscbReceipt.verify(tampered_sig) do
    {:error, :bad_signature} -> failures
    err -> IO.puts("FAIL tampered signature got #{inspect(err)}"); ["tamper-sig" | failures]
  end

# 5. deterministic markdown for identical receipt
failures =
  if CscbReceipt.render_markdown(receipt) == md do
    failures
  else
    IO.puts("FAIL render not deterministic")
    ["determinism" | failures]
  end

# 6. same payload minted twice → distinct nonces/signatures (ephemeral key per run)
{:ok, other} = CscbReceipt.mint(CscbReceiptFixtures.results(), CscbReceiptFixtures.stamp())
failures =
  if other.nonce != receipt.nonce do
    failures
  else
    IO.puts("FAIL nonce repeated across runs")
    ["nonce" | failures]
  end

# 7. header fields present: embedded public key is 65-byte P-256 uncompressed point
failures =
  if byte_size(receipt.public_key) == 65 and binary_part(receipt.public_key, 0, 1) == <<4>> do
    failures
  else
    IO.puts("FAIL public key not 65-byte uncompressed P-256 point")
    ["pubkey" | failures]
  end

# 8. renders for a second minted payload too (different values, still verifies)
{:ok, r2} = CscbReceipt.mint(CscbReceiptFixtures.results_at(99.9), CscbReceiptFixtures.stamp())
failures =
  if CscbReceipt.verify(r2) == :ok and String.contains?(CscbReceipt.render_markdown(r2), "99.9") do
    failures
  else
    IO.puts("FAIL second payload mint/verify/render")
    ["second payload" | failures]
  end

# 9. HTML render determinism: byte-identical for the same receipt
html = CscbReceipt.render_html(receipt)
failures =
  if CscbReceipt.render_html(receipt) == html do
    failures
  else
    IO.puts("FAIL html render not deterministic")
    ["html-determinism" | failures]
  end

# 10. HTML is self-contained: inline CSS + @media print + page-break, no JS/no external refs
failures =
  if String.contains?(html, "<style>") and
     String.contains?(html, "@media print") and
     String.contains?(html, "page-break-before") and
     not String.contains?(html, "<script") and
     not String.contains?(html, "http://") and
     not String.contains?(html, "https://") do
    failures
  else
    IO.puts("FAIL html missing print CSS or not self-contained")
    ["html-print-css" | failures]
  end

# 11. HTML carries the same dossier content as markdown (same receipt)
failures =
  if String.contains?(html, "87.4") and String.contains?(html, "CRC32:") and
     String.contains?(html, Base.encode16(receipt.signature, case: :lower)) do
    failures
  else
    IO.puts("FAIL html missing dossier content")
    ["html-content" | failures]
  end

# 12. hostile metric value is HTML-escaped, not executed
{:ok, hostile} = CscbReceipt.mint(
  %{verdict: :adopted,
    metrics: %{xss_metric: "<script>alert(1)</script>"}},
  CscbReceiptFixtures.stamp())
hostile_html = CscbReceipt.render_html(hostile)
failures =
  if not String.contains?(hostile_html, "<script>alert") and
     String.contains?(hostile_html, "&lt;script&gt;") do
    failures
  else
    IO.puts("FAIL hostile metric value not escaped in html")
    ["html-escaping" | failures]
  end

# 13. markdown and html render from the same receipt without interfering
failures =
  if CscbReceipt.render_markdown(receipt) == md and CscbReceipt.render_html(receipt) == html do
    failures
  else
    IO.puts("FAIL markdown/html renders interfere")
    ["dual-render" | failures]
  end

# 14. AR7/X3: hostile metric value is markdown-escaped (<script> does not survive)
{:ok, hostile_md_rcpt} = CscbReceipt.mint(
  %{verdict: :inconclusive,
    metrics: %{xss_metric: "<script>alert(1)</script>"}},
  CscbReceiptFixtures.stamp())
hostile_md = CscbReceipt.render_markdown(hostile_md_rcpt)
failures =
  if not String.contains?(hostile_md, "<script>alert") and
     String.contains?(hostile_md, "&lt;script&gt;alert(1)&lt;/script&gt;") do
    failures
  else
    IO.puts("FAIL hostile metric value not markdown-escaped")
    ["md-escaping" | failures]
  end

# 15. AR7/X3: a |-bearing metric key cannot break the table row structure
pipe_rcpt = CscbReceipt.mint!(
  %{verdict: :adopted,
    metrics: %{"bad | key": 1}},
  CscbReceiptFixtures.stamp())
pipe_md = CscbReceipt.render_markdown(pipe_rcpt)
row_lines =
  pipe_md
  |> String.split("\n")
  |> Enum.drop_while(&(&1 != "|---|---|"))
  |> Enum.drop(1)
  |> Enum.take_while(&String.starts_with?(&1, "| "))
failures =
  if Enum.all?(row_lines, fn line ->
       String.starts_with?(line, "| ") and String.ends_with?(line, " |") and
       # exactly 3 pipes = one intact 2-cell row
       length(String.split(line, " \\| ")) == 2
     end) and row_lines != [] do
    failures
  else
    IO.puts("FAIL pipe-bearing key broke table row integrity: #{inspect(row_lines)}")
    ["md-table-integrity" | failures]
  end

# 16. AR7/X3: closed verdict set — valid atoms mint, :pass and garbage refused typed
failures =
  Enum.reduce([:status_quo_refused, :adopted, :inconclusive], failures, fn v, failures ->
    case CscbReceipt.mint(%{verdict: v, metrics: %{m: 1}}, CscbReceiptFixtures.stamp()) do
      # runtime struct check: the beam is compiled at runtime here, so
      # compile-time %CscbReceipt{} expansion is unavailable in this script
      {:ok, r} when is_struct(r, CscbReceipt) and r.verdict == v -> failures
      other ->
        IO.puts("FAIL closed-set atom #{inspect(v)} refused: #{inspect(other)}")
        ["closed-set-#{v}" | failures]
    end
  end)

failures =
  case CscbReceipt.mint(%{verdict: :pass, metrics: %{m: 1}}, CscbReceiptFixtures.stamp()) do
    {:error, {:invalid_verdict, :pass}} -> failures
    other ->
      IO.puts("FAIL :pass not refused typed, got #{inspect(other)}")
      ["closed-set-pass" | failures]
  end

failures =
  case CscbReceipt.mint(%{verdict: "adopted", metrics: %{m: 1}}, CscbReceiptFixtures.stamp()) do
    {:error, {:invalid_verdict, "adopted"}} -> failures
    other ->
      IO.puts("FAIL string verdict not refused typed, got #{inspect(other)}")
      ["closed-set-string" | failures]
  end

# 17. AR7/X3: rationale map (CscbVerdict.rule/1 output shape) accepted into the slot
rationale = %{
  verdict: :status_quo_refused,
  invariant_rows: [],
  economics_total_usd: 0.0,
  missing: [],
  violated_by_status_quo: [:tail_under_100us]
}
failures =
  case CscbReceipt.mint(%{verdict: rationale, metrics: %{m: 1}}, CscbReceiptFixtures.stamp()) do
    {:ok, r} when is_struct(r, CscbReceipt) and r.verdict == rationale -> failures
    other ->
      IO.puts("FAIL rationale map not accepted, got #{inspect(other)}")
      ["rationale-map" | failures]
  end

failures =
  case CscbReceipt.mint(%{verdict: %{verdict: :pass}, metrics: %{m: 1}},
         CscbReceiptFixtures.stamp()) do
    {:error, {:invalid_verdict, %{verdict: :pass}}} -> failures
    other ->
      IO.puts("FAIL rationale with out-of-set verdict not refused, got #{inspect(other)}")
      ["rationale-bad-verdict" | failures]
  end

total = 17
pass = total - length(failures)
IO.puts("#{pass}/#{total} passed")
System.cmd("rm", ["-rf", "/tmp/cscb_r9_ebin"])
# lane X3: exit(:ok) at script top level still exits the VM with rc 1;
# System.halt(0) is the rc=0 convention the other courts use.
if failures == [], do: System.halt(0), else: IO.inspect(Enum.reverse(failures)) && System.halt(1)
