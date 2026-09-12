## verify/render_check.exs -- REAL render regression proof for this pack's
## own greet-cli playground. Thin wrapper around the generic generate.exs
## (see that file for the real, reusable mechanics and for how to point the
## generator at a DIFFERENT ontology instance, e.g. instances/marketplace-cli.ttl).
##
## Run from ~/ggen_igniter (this pack's own generator dependency root):
##
##   cd ~/ggen_igniter && mix run <this pack>/verify/render_check.exs

pack_root = __ENV__.file |> Path.dirname() |> Path.dirname() |> Path.expand()
playground_path = Path.join(pack_root, "playground/greet-cli.ttl")
examples_dir = Path.join(pack_root, "examples/greet-cli")
generate_script = Path.join(pack_root, "verify/generate.exs")

System.argv([playground_path, examples_dir])
Code.eval_file(generate_script)
