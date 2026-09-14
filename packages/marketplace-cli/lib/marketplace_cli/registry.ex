defmodule MarketplaceCli.Registry do
  @moduledoc """
  The real, generated verb registry backing both
  `mix marketplace_cli.validate`/`.catalog` (this pack's own thin tasks) and
  the generic `mix ex_noun_verb_cli marketplace validate|catalog --root
  <path>` adapter (`ex_noun_verb_cli`'s own `Mix.Tasks.ExNounVerbCli`, which
  resolves its registry module from `Application.fetch_env!(:ex_noun_verb_cli,
  :registry)` -- set to this module in `config/config.exs`).

  GENERATED, not hand-written: this closes the one disclosed
  hand-authored-vs-generated gap named in this module's own prior moduledoc
  ("hand-written rather than ggen-generated"). The real source of truth is
  now `~/ggen-marketplace/packs/ex-noun-verb-cli-pack/instances/marketplace-cli.ttl`
  (an `nvc:GeneratedCliProject` Turtle instance) rendered through that
  pack's real `templates/registry.ex.tmpl` via `ggen_igniter`'s real
  oxigraph+TeraWasm pipeline -- the same generation layer proven against the
  pack's own `greet-cli` playground.

  To regenerate after editing the instance ttl (do not hand-edit the verb
  list below; edit the ttl and regenerate instead):

      cd ~/ggen_igniter && mix run \\
        ~/ggen-marketplace/packs/ex-noun-verb-cli-pack/verify/generate.exs \\
        ~/ggen-marketplace/packs/ex-noun-verb-cli-pack/instances/marketplace-cli.ttl \\
        <scratch_dir> \\
        registry.ex.tmpl

  then copy `<scratch_dir>/lib/marketplace_cli/registry.ex` over this file
  and re-run `mix format` (the generator does not itself run the formatter).
  """

  use ExNounVerbCli.Registry.Generated,
    verbs: [
      [
        noun: "marketplace",
        verb: "catalog",
        module: MarketplaceCli.Inspector,
        function: :catalog,
        info: %{schema: [root: :string], required: [:root]},
        doc: "Emits the marketplace catalog JSON, mirroring scripts/marketplace.py catalog."
      ],
      [
        noun: "marketplace",
        verb: "validate",
        module: MarketplaceCli.Inspector,
        function: :validate,
        info: %{schema: [root: :string], required: [:root]},
        doc: "Validates every pack under <root>/packs, mirroring scripts/marketplace.py validate."
      ]
    ]
end
