defmodule MarketplaceCli.Registry do
  @moduledoc """
  The real, generated-shape verb registry backing both
  `mix marketplace_cli.validate`/`.catalog` (this pack's own thin tasks) and
  the generic `mix ex_noun_verb_cli marketplace validate|catalog --root
  <path>` adapter (`ex_noun_verb_cli`'s own `Mix.Tasks.ExNounVerbCli`, which
  resolves its registry module from `Application.fetch_env!(:ex_noun_verb_cli,
  :registry)` -- set to this module in `config/config.exs`).

  Uses `ExNounVerbCli.Registry.Generated` -- the v1-primary mechanism a ggen
  template would emit -- even though this particular registry is
  hand-written rather than ggen-generated (this milestone's job is proving
  the library against a real consumer, not generating this specific
  registry via Tera/EEx).
  """

  use ExNounVerbCli.Registry.Generated,
    verbs: [
      [
        noun: "marketplace",
        verb: "validate",
        module: MarketplaceCli.Inspector,
        function: :validate,
        info: %{schema: [root: :string], required: [:root]},
        doc: "Validates every pack under <root>/packs, mirroring scripts/marketplace.py validate."
      ],
      [
        noun: "marketplace",
        verb: "catalog",
        module: MarketplaceCli.Inspector,
        function: :catalog,
        info: %{schema: [root: :string], required: [:root]},
        doc: "Emits the marketplace catalog JSON, mirroring scripts/marketplace.py catalog."
      ]
    ]
end
