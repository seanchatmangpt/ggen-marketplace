# Lane R9 qualification fixtures — cryptographic receipt dossier corpus.
defmodule CscbReceiptFixtures do
  @stamp "attest:v1:sha256:cscb-r9-fixture"

  def stamp, do: @stamp

  def results do
    %{
      verdict: :adopted,
      metrics: %{
        p99_max_micros: 87.4,
        max_allocation_bytes: 0,
        throughput_ops: 142_117,
        adversarial_cases: 24
      }
    }
  end

  def results_at(p99) do
    put_in(results(), [:metrics, :p99_max_micros], p99)
  end
end
