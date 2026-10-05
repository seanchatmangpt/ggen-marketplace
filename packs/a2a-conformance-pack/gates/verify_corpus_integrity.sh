#!/usr/bin/env bash
# corpus-integrity gate -- EXECUTABLE half (the SPARQL half is
# 010_corpus_integrity.rq over the pack graph).
#
# The vendored proto is pristine -- sha256 pinned here AND in the gate
# header above:
#   945df6e34001b2bfd0fd62d9484b63094dfad9d78705e41e2873441c419ae2d1
#
# Usage: bash gates/verify_corpus_integrity.sh [ASH_A2A_CHECKOUT]
#   default checkout: /Users/sac/ash_a2a (the truth source this pack mints against)
set -euo pipefail

REPO="${1:-/Users/sac/ash_a2a}"
CORPUS="$REPO/priv/a2a_v1_spec_corpus/v1_spec_examples.json"
PROTO="$REPO/priv/a2a_v1_spec_corpus/a2a.proto"
PINNED_SHA="945df6e34001b2bfd0fd62d9484b63094dfad9d78705e41e2873441c419ae2d1"
PINNED_EXAMPLES=36
# The corpus's closed family vocabulary (pinned by the corpus court's
# integrity test and ontology.ttl's CorpusFamily individuals).
FAMILIES='agent_card message task status artifact part event jsonrpc_request jsonrpc_error'

fail() { echo "CORPUS-INTEGRITY FAIL: $*" >&2; exit 1; }

[ -f "$PROTO" ]  || fail "vendored proto not found at $PROTO"
[ -f "$CORPUS" ] || fail "spec corpus not found at $CORPUS"

ACTUAL_SHA="$(shasum -a 256 "$PROTO" | awk '{print $1}')"
[ "$ACTUAL_SHA" = "$PINNED_SHA" ] \
  || fail "vendored a2a.proto is NOT pristine: sha256 $ACTUAL_SHA != pinned $PINNED_SHA (any byte change moves the sha and kills the pristine claim)"

python3 - "$CORPUS" "$PINNED_EXAMPLES" $FAMILIES <<'PY'
import json, sys
corpus, expected_n, *families = sys.argv[1:]
d = json.load(open(corpus))
examples = d["examples"]
if len(examples) != int(expected_n):
    sys.exit(f"FAIL: corpus has {len(examples)} examples, pinned {expected_n}")
if d.get("corpus") != "a2a_v1_spec_corpus":
    sys.exit("FAIL: corpus header contract broken (corpus != a2a_v1_spec_corpus)")
if d.get("spec_source", {}).get("url") != "https://a2a-protocol.org/latest/specification/":
    sys.exit("FAIL: spec provenance header missing or drifted")
if not d.get("findings_summary"):
    sys.exit("FAIL: findings_summary empty -- codec_gap findings were dropped")
ids = [e["id"] for e in examples]
if len(ids) != len(set(ids)):
    sys.exit("FAIL: duplicate example ids in corpus")
actual_families = {e["family"] for e in examples}
missing = actual_families - set(families)
if missing:
    sys.exit(f"FAIL: families outside the closed vocabulary: {sorted(missing)}")
gaps = [e for e in examples if e.get("expect") == "codec_gap"]
if len(gaps) != 6:
    sys.exit(f"FAIL: pinned codec_gap count is 6, corpus has {len(gaps)} -- pinned findings were silently 'fixed'")
print(f"corpus ok: {len(examples)} examples, {len(gaps)} pinned codec_gap findings, families closed")
PY

echo "CORPUS-INTEGRITY PASS: proto pristine (sha pinned), corpus frozen and complete"
