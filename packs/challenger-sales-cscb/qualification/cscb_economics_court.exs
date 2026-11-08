# Lane R2 court — standalone, no mix project required.
# Run: elixir qualification/cscb_economics_court.exs
base = String.replace(__DIR__, "/qualification", "")
File.cd!(base)

{_, 0} =
  System.cmd("elixirc",
    ["lib/cscb_economics.ex", "-o", "/tmp/cscb_r2_ebin",
     "-pa", "/Users/sac/ash_pplan/_build/dev/lib/decimal/ebin"]
  )
true = Code.append_path("/tmp/cscb_r2_ebin")
true = Code.append_path("/Users/sac/ash_pplan/_build/dev/lib/decimal/ebin")
Code.require_file("qualification/cscb_economics_spot.exs", base)
alias CscbEconomicsSpotFixtures, as: F
alias CscbEconomics, as: E
alias Decimal, as: D

eq = fn a, b -> D.compare(a, D.new(b)) == :eq end

cases = [
  {"RFC sample reproduces exactly",
   fn ->
     {:ok, r} = E.loss(F.rfc_metrics(), F.rfc_pricing())
     jitter = Enum.find(r.lines, &(&1.name == :jitter)).annual_amount
     sla = Enum.find(r.lines, &(&1.name == :sla)).annual_amount
     hosting = Enum.find(r.lines, &(&1.name == :hosting)).annual_amount
     eq.(jitter, 300_000) and eq.(sla, 16_920) and eq.(hosting, 6_000) and
       eq.(r.total_annual_hemorrhage, 322_920)
   end.()},
  {"zero deltas -> zero hemorrhage",
   fn ->
     {:ok, r} = E.loss(F.zero_metrics(), F.rfc_pricing())
     eq.(r.total_annual_hemorrhage, 0)
   end.()},
  {"negative delta refused typed",
   E.loss(F.negative_metrics(), F.rfc_pricing()) == {:refused, :negative_metric}},
  {"nil metric refused typed",
   E.loss(F.nil_metrics(), F.rfc_pricing()) == {:refused, :nil_metric}},
  {"missing pricing key refused typed",
   E.loss(F.rfc_metrics(), F.missing_pricing()) == {:refused, :invalid_pricing}},
  {"non-map input refused",
   E.loss("nope", F.rfc_pricing()) == {:refused, :nil_metric}},
  {"ms->us->$ conversion 50ms x 6e-7 $/us = 0.03",
   match?({:ok, d}, E.dollars_per_microsecond(50, "0.0000006")) and
   elem(E.dollars_per_microsecond(50, "0.0000006"), 1) |> D.compare(D.new("0.03")) == :eq},
  {"bytes conversion 4096 x 0.25 = 1024",
   match?({:ok, d}, E.dollars_per_allocation_byte(4096, "0.25")) and
   elem(E.dollars_per_allocation_byte(4096, "0.25"), 1) |> D.compare(D.new("1024")) == :eq},
  {"negative jitter in conversion refused",
   E.dollars_per_microsecond(-1, "0.0000006") == {:refused, :negative_metric}},
  {"zero rate in conversion refused",
   E.dollars_per_microsecond(50, F.zero_rate_pricing().dollars_per_microsecond)
   == {:refused, :invalid_pricing}},
  {"provenance: every line carries formula + inputs",
   fn ->
     {:ok, r} = E.loss(F.rfc_metrics(), F.rfc_pricing())
     Enum.all?(r.lines, fn l -> is_binary(l.formula) and is_map(l.inputs) and map_size(l.inputs) > 0 end)
   end.()},
  {"Decimal exactness: total is exact sum of line amounts",
   fn ->
     {:ok, r} = E.loss(F.rfc_metrics(), F.rfc_pricing())
     sum = Enum.reduce(r.lines, D.new(0), fn l, acc -> D.add(acc, l.annual_amount) end)
     D.compare(sum, r.total_annual_hemorrhage) == :eq
   end.()}
]

{passed, failed} =
  Enum.reduce(cases, {0, 0}, fn {name, outcome}, {p, f} ->
    if outcome do
      IO.puts("[PASS] #{name}")
      {p + 1, f}
    else
      IO.puts("[FAIL] #{name}")
      {p, f + 1}
    end
  end)

IO.puts("court: #{passed} pass / #{failed} fail")
System.at_exit(fn _ -> if failed > 0, do: System.stop(1) end)
