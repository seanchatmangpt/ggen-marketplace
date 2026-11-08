defmodule CscbReceipt do
  @moduledoc """
  Cryptographic audit dossier for a CSCB qualification run (RFC §4.1
  artifact 3).

  `mint/2` takes harness output (`results`) plus an attestation `stamp`
  and produces a self-verifying receipt struct:

    * `:crc32`          — CRC32 of the canonical receipt term
                          (`:erlang.crc32` over `:erlang.term_to_binary/1`)
    * `:profile_digest` — hardware signature from `CscbAttest` when the
                          optional dependency is loadable, else `nil`
    * `:nonce`          — per-run unique nonce (Phase 3 ephemeral run id)
    * `:metrics`        — per-metric measured values, verbatim
    * `:verdict`        — verdict slot: one of the closed atoms
                          `:status_quo_refused | :adopted | :inconclusive`,
                          or a rationale map/struct carrying a closed-set
                          verdict (CscbVerdict.rule/1 output shape). Mint
                          refuses anything else typed:
                          `{:error, {:invalid_verdict, value}}`.
    * `:public_key`     — embedded ECDSA P-256 public key (raw, 65-byte
                          uncompressed point), so anyone holding the
                          receipt can verify the signature
    * `:signature`      — ECDSA P-256 / SHA-256 signature over the
                          canonical receipt term (DER-encoded)

  Non-repudiation: each run generates an ephemeral P-256 keypair; the
  canonical term is signed with the private key and the public key is
  embedded in the receipt. `verify/1` recomputes the CRC and verifies the
  signature against the embedded key.

  Verification failure vocabulary (typed, closed):

    * `{:error, :crc_mismatch}` — receipt payload altered
    * `{:error, :bad_signature}` — signature altered or wrong key

  `render_markdown/1` produces the RFC §5-style dossier (metric table,
  CRC block, signature block). Deterministic: the same receipt renders to
  byte-identical markdown. PDF rendering is deferred (RFC Phase 3);
  markdown is emitted now.

  `render_html/1` renders the same dossier as a deterministic,
  self-contained HTML document (inline CSS, print stylesheet, page-break
  rules; no external dependencies, no JavaScript). All interpolated
  values are HTML-escaped — metric values are measured data and must not
  inject markup. PDF generation itself remains deferred; the HTML is
  print-ready via browser print as the Phase-3 intermediate.
  """

  @enforce_keys [:results, :stamp, :crc32, :profile_digest, :nonce, :metrics,
                 :verdict, :public_key, :signature]
  defstruct [:results, :stamp, :crc32, :profile_digest, :nonce, :metrics,
             :verdict, :public_key, :signature]

  @type t :: %__MODULE__{
          results: map(),
          stamp: term(),
          crc32: non_neg_integer(),
          profile_digest: String.t() | nil,
          metrics: map(),
          verdict: term(),
          public_key: binary(),
          signature: binary()
        }

  @type verify_error :: {:error, :crc_mismatch | :bad_signature}

  # ── mint ──────────────────────────────────────────────────────────────

  @doc """
  Mints a receipt from harness `results` and an attestation `stamp`.

  The metrics map is the measured values themselves (defaulting to
  `results.metrics` when present). An ephemeral P-256 keypair is
  generated per run; the public key is embedded so `verify/1` needs no
  external material.
  """
  @valid_verdicts [:status_quo_refused, :adopted, :inconclusive]

  @spec mint(map(), term()) :: {:ok, t()} | {:error, {:invalid_verdict, term()}}
  def mint(results, stamp) when is_map(results) do
    metrics = Map.get(results, :metrics, results)

    case validate_verdict(Map.get(results, :verdict)) do
      :ok -> {:ok, do_mint(results, stamp, metrics)}
      {:error, reason} -> {:error, reason}
    end
  end

  @doc """
  Like `mint/2` but raises on an out-of-vocabulary verdict slot (lane X3,
  AR7 closed-set law). Returns the receipt directly.
  """
  @spec mint!(map(), term()) :: t()
  def mint!(results, stamp) do
    case mint(results, stamp) do
      {:ok, receipt} -> receipt
      {:error, reason} -> raise ArgumentError, "CscbReceipt.mint refused: #{inspect(reason)}"
    end
  end

  # Verdict slot vocabulary (lane X3, AR7): closed set only. Accepts the
  # three verdict atoms, or a rationale map/struct carrying a closed-set
  # verdict (the shape CscbVerdict.rule/1 returns; a %CscbVerdict.Rationale{}
  # struct, if introduced later, satisfies the same clause). `:pass` — the
  # historical default — is outside the set and is now refused typed.
  defp validate_verdict(v) when v in @valid_verdicts, do: :ok
  defp validate_verdict(%{verdict: v}) when v in @valid_verdicts, do: :ok
  defp validate_verdict(v), do: {:error, {:invalid_verdict, v}}

  defp do_mint(results, stamp, metrics) do
    verdict = Map.fetch!(results, :verdict)
    nonce = nonce()
    profile_digest = hardware_profile_digest()

    base = %__MODULE__{
      results: results,
      stamp: stamp,
      crc32: 0,
      profile_digest: profile_digest,
      nonce: nonce,
      metrics: metrics,
      verdict: verdict,
      public_key: nil,
      signature: nil
    }

    {public_key, private_key} = keypair()
    canonical = canonical_term(base)
    crc = :erlang.crc32(:erlang.term_to_binary(canonical))
    # SLA minimal-unblock (lane R13, disclosed in R9 receipt too): keypair/0
    # uses :crypto.generate_key(:ecdh, :prime256v1); the ECDH private-key
    # format doesn't carry the curve, so :crypto.sign(:ecdsa, ...) raises
    # {:badarg, "pkey.c", "Couldn't get ECDSA private key"} without it.
    signature = :crypto.sign(:ecdsa, :sha256, :erlang.term_to_binary(canonical),
                             [private_key, :prime256v1])

    %{base | crc32: crc, public_key: public_key, signature: signature}
  end

  # ── verify ────────────────────────────────────────────────────────────

  @doc """
  Recomputes the CRC32 over the receipt's canonical term and verifies the
  ECDSA signature against the embedded public key.

  Returns `:ok` or `{:error, :crc_mismatch | :bad_signature}`.
  """
  @spec verify(t()) :: :ok | verify_error()
  def verify(%__MODULE__{} = receipt) do
    canonical = canonical_term(receipt)
    digest_bin = :erlang.term_to_binary(canonical)

    cond do
      :erlang.crc32(digest_bin) != receipt.crc32 ->
        {:error, :crc_mismatch}

      not :crypto.verify(:ecdsa, :sha256, digest_bin, receipt.signature,
                         [receipt.public_key, :prime256v1]) ->
        {:error, :bad_signature}

      true ->
        :ok
      end
  end

  @doc """
  Pinned verification (lane AR7): like `verify/1`, but additionally requires
  the receipt's embedded public key to equal `expected_pubkey` (raw 65-byte
  uncompressed point). This is the closure for the key-substitution attack:
  `verify/1` is self-consistent by design — any attacker can mint a receipt
  over fabricated metrics with their own ephemeral key and it verifies — so
  trust requires pinning the expected signer key (or a profile digest that
  binds one). Returns `{:error, :key_mismatch}` when the embedded key is not
  the pinned one, before any signature work.
  """
  @spec verify(t(), binary()) :: :ok | verify_error() | {:error, :key_mismatch}
  def verify(%__MODULE__{} = receipt, expected_pubkey)
      when is_binary(expected_pubkey) do
    if receipt.public_key == expected_pubkey do
      verify(receipt)
    else
      {:error, :key_mismatch}
    end
  end

  # ── render ────────────────────────────────────────────────────────────

  @doc """
  Renders the RFC §5-style dossier: metric table, CRC block, signature
  block. Deterministic — the same receipt renders byte-identically.

  PDF output is deferred (RFC Phase 3); markdown is the emitted form.
  """
  @spec render_markdown(t()) :: String.t()
  def render_markdown(%__MODULE__{} = r) do
    header = [
      "# CSCB Audit Dossier",
      "",
      "Verdict: #{esc_md(inspect(r.verdict))}",
      "Nonce: #{esc_md(to_string(r.nonce))}",
      "Hardware profile: #{esc_md(r.profile_digest || "unavailable (optional dep not loaded)")}",
      "Attestation stamp: #{esc_md(inspect(r.stamp))}",
      "",
      "## Measured metrics",
      "",
      "| metric | value |",
      "|---|---|",
    ]

    rows =
      r.metrics
      |> Enum.sort_by(fn {k, _} -> to_string(k) end)
      |> Enum.map(fn {k, v} ->
        "| #{esc_md(to_string(k))} | #{esc_md(format_value(v))} |"
      end)

    footer = [
      "",
      "## Integrity",
      "",
      "CRC32: `0x#{Integer.to_string(r.crc32, 16)}`",
      "",
      "## Signature",
      "",
      "Algorithm: ECDSA P-256 / SHA-256 (ephemeral key per run)",
      "Public key: `#{Base.encode16(r.public_key, case: :lower)}`",
      "Signature: `#{Base.encode16(r.signature, case: :lower)}`",
      "",
      "PDF rendering: deferred (RFC Phase 3).",
      ""
    ]

    # Lane X3: lines were previously concatenated without separators — the
    # dossier rendered as one unbroken line and the metric table was not a
    # markdown table at all. Each line is now newline-terminated, so row
    # structure (and table-integrity guarantees) are real.
    (header ++ rows ++ footer)
    |> Enum.intersperse("\n")
    |> IO.iodata_to_binary()
  end

  @doc """
  Renders the same RFC §5-style dossier as a self-contained HTML document:
  inline CSS, `@media print` stylesheet, page-break rules — no external
  dependencies, no JavaScript. Deterministic — the same receipt renders
  byte-identically. All interpolated values are HTML-escaped.

  PDF generation remains deferred (RFC Phase 3); this document is the
  print-ready intermediate, printable via a browser's print dialog.
  """
  @spec render_html(t()) :: String.t()
  def render_html(%__MODULE__{} = r) do
    metric_rows =
      r.metrics
      |> Enum.sort_by(fn {k, _} -> to_string(k) end)
      |> Enum.map(fn {k, v} ->
        ["<tr><td>", esc(to_string(k)), "</td><td>", esc(format_value(v)),
         "</td></tr>\n"]
      end)

    doc = [
      "<!DOCTYPE html>\n",
      "<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n",
      "<title>", esc("CSCB Audit Dossier"), "</title>\n",
      "<style>\n",
      "body{font-family:monospace;margin:2em;color:#111;}\n",
      "h1{font-size:1.4em;}h2{font-size:1.1em;margin-top:1.5em;}\n",
      "table{border-collapse:collapse;}\n",
      "td,th{border:1px solid #999;padding:0.3em 0.8em;text-align:left;}\n",
      ".block{white-space:pre-wrap;word-break:break-all;}\n",
      ".pagebreak{page-break-before:always;}\n",
      "@media print{body{margin:0;}h2{page-break-after:avoid;}\n",
      "table{page-break-inside:auto;}tr{page-break-inside:avoid;}\n",
      ".pagebreak{break-before:page;}}\n",
      "</style>\n</head>\n<body>\n",
      "<h1>", esc("CSCB Audit Dossier"), "</h1>\n",
      "<p>Verdict: ", esc(inspect(r.verdict)), "</p>\n",
      "<p>Nonce: ", esc(to_string(r.nonce)), "</p>\n",
      "<p>Hardware profile: ",
      esc(r.profile_digest || "unavailable (optional dep not loaded)"),
      "</p>\n",
      "<p>Attestation stamp: ", esc(inspect(r.stamp)), "</p>\n",
      "<h2>", esc("Measured metrics"), "</h2>\n",
      "<table>\n<tr><th>metric</th><th>value</th></tr>\n",
      metric_rows,
      "</table>\n",
      "<div class=\"pagebreak\"></div>\n",
      "<h2>", esc("Integrity"), "</h2>\n",
      "<p>CRC32: <code>0x", esc(Integer.to_string(r.crc32, 16)), "</code></p>\n",
      "<h2>", esc("Signature"), "</h2>\n",
      "<p>Algorithm: ", esc("ECDSA P-256 / SHA-256 (ephemeral key per run)"),
      "</p>\n",
      "<p>Public key: <span class=\"block\"><code>",
      esc(Base.encode16(r.public_key, case: :lower)), "</code></span></p>\n",
      "<p>Signature: <span class=\"block\"><code>",
      esc(Base.encode16(r.signature, case: :lower)), "</code></span></p>\n",
      "<p>", esc("PDF rendering: deferred (RFC Phase 3). "
                 <> "Print-ready via browser print."), "</p>\n",
      "</body>\n</html>\n"
    ]

    IO.iodata_to_binary(doc)
  end

  # ── internals ─────────────────────────────────────────────────────────

  # Canonical term over integrity-bearing payload fields only. The CRC,
  # signature, and public key are excluded: the CRC is computed over this
  # term (self-inclusion would be unsatisfiable), and the signature is
  # verified against the embedded key, which binds the key by use.
  defp canonical_term(%__MODULE__{} = r) do
    {:cscb_receipt_v1, r.results, r.stamp, r.profile_digest,
     r.nonce, r.metrics, r.verdict}
  end

  defp nonce do
    :crypto.strong_rand_bytes(16) |> Base.encode16(case: :lower)
  end

  # Ephemeral P-256 keypair per run (raw 65-byte uncompressed public
  # point + 32-byte private scalar). The curve must be supplied at
  # sign/verify time ([key, curve] list form) because the raw private
  # scalar carries no curve parameters.
  defp keypair do
    :crypto.generate_key(:ecdh, :prime256v1)
  end

  defp hardware_profile_digest do
    if Code.ensure_loaded?(CscbAttest) and function_exported?(CscbAttest, :profile_digest, 0) do
      CscbAttest.profile_digest()
    else
      nil
    end
  end

  defp format_value(v) when is_float(v), do: :erlang.float_to_binary(v, [:compact, decimals: 6])
  defp format_value(v), do: inspect(v)

  # HTML-escape measured/derived text. Metric values are measured data and
  # may carry hostile bytes; everything interpolated into the document goes
  # through this.
  defp esc(bin) when is_binary(bin) do
    for <<ch <- bin>>, do: escape_char(ch)
    |> IO.iodata_to_binary()
  end

  defp esc(other), do: esc(inspect(other))

  defp escape_char(?<), do: "&lt;"
  defp escape_char(?>), do: "&gt;"
  defp escape_char(?&), do: "&amp;"
  defp escape_char(?"), do: "&quot;"
  defp escape_char(?'), do: "&#39;"
  defp escape_char(ch), do: <<ch>>

  # Markdown-escape measured/derived text (lane X3, AR7): a `|` breaks the
  # metric table row structure, `<`/`>` survive into HTML-in-markdown
  # renderers, backticks open code spans, `&` seeds entity injection.
  # Everything interpolated into the markdown dossier goes through this.
  defp esc_md(bin) when is_binary(bin) do
    bin
    |> String.replace("&", "&amp;")
    |> String.replace("<", "&lt;")
    |> String.replace(">", "&gt;")
    |> String.replace("|", "\\|")
    |> String.replace("`", "\\`")
  end

  defp esc_md(other), do: esc_md(inspect(other))
end
