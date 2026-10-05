# Lane C9 court runner: runs the three courts (regeneration, drift, mutation
# league) from courts/ against this specimen directory. Exits non-zero on
# the first court failure.
specimen_root = __DIR__
System.put_env("SPECIMEN_ROOT", specimen_root)

pack_courts = Path.expand("../../courts", __DIR__)

for court <- ~w(regeneration_court drift_court mutation_league) do
  path = Path.join(pack_courts, court <> ".exs")
  IO.puts("")
  IO.puts("### running #{path}")
  {result, _binding} = Code.eval_file(path)
  result == :ok || exit({:court_failed, court, result})
end

IO.puts("")
IO.puts("all three courts PASS")
:ok
