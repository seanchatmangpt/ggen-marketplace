# The generated tree is required: scripts/cs2_pack_live_fixture.sh sets
# CS2_PACK_GENERATED to the capsule copy of a real `ggen sync run`. No hand copy of
# any generated JSON or module exists in this fixture.
root = System.get_env("CS2_PACK_GENERATED") || raise "CS2_PACK_GENERATED unset"

unless File.dir?(Path.join(root, "elixir")) and File.regular?(Path.join(root, "work-projection-batch.json")) do
  raise "CS2_PACK_GENERATED=#{root} is not a ggen-projected cs2-semantic-work tree"
end

ExUnit.start()
