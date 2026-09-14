import Config

# ExNounVerbCli.Escript / the generic `mix ex_noun_verb_cli` Igniter adapter
# both resolve their registry module from this key (the one shared
# configuration point both adapters use, per ex_noun_verb_cli's own docs).
config :ex_noun_verb_cli, :registry, MarketplaceCli.Registry

# Default marketplace root this consumer app inspects: this same
# ggen-marketplace checkout, computed relative to this config file so it
# resolves correctly regardless of which worktree the app lives in.
# config.exs -> config/ -> marketplace-cli/ -> packages/ -> marketplace root.
#
# Deliberately placed under packages/ (a sibling of packs/), NOT nested
# inside packs/noun-verb-cli-pack/ itself: a real, compiled Mix project's
# _build/deps trees contain real symlinks (priv/src/include dirs from
# hex packages like rdf/sparql/rustler/yamerl/telemetry), and
# scripts/marketplace.py's own PACKS.rglob("*") walk -- ported faithfully
# in MarketplaceCli.Inspector -- refuses ANY symlink found anywhere under
# packs/ (REFUSED:PACK_SYMLINK). A first attempt at nesting this consumer
# app under packs/noun-verb-cli-pack/consumer/ confirmed this the hard way:
# `mix deps.get`/`compile` there made `Inspector.validate/1` (and the real
# `python3 scripts/marketplace.py validate`) both refuse the ENTIRE
# marketplace once real deps were fetched, which is real, correct
# behavior on both ports' part -- not a bug to route around inside
# packs/, but a real reason this consumer belongs outside it.
config :marketplace_cli, :marketplace_root, Path.expand("../../..", __DIR__)
