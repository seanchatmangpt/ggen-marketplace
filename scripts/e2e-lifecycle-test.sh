#!/usr/bin/env bash
# End-to-end proof for the active 80/20 marketplace registry.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
pack_name="ggen-platform-pack"
registry_index="https://seanchatmangpt.github.io/ggen-marketplace/index.json"
scratch="$(mktemp -d)"
trap 'rm -rf "$scratch"' EXIT

step() { printf '\n== %s ==\n' "$1"; }

step "1/6 validate the complete source corpus"
python3 "$root/scripts/marketplace.py" validate

step "2/6 project the active registry"
python3 "$root/scripts/marketplace.py" catalog > "$scratch/local-catalog.json"
python3 - "$scratch/local-catalog.json" "$pack_name" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
names = [pack["name"] for pack in payload["packs"]]
assert payload["scope"] == "active", payload
assert len(names) == 12, names
assert sys.argv[2] in names, names
assert "clap-noun-verb-zeroconfig-pack" not in names, names
PY

step "3/6 fetch the live active registry and compare identities"
curl --fail --silent --show-error --location "$registry_index" --output "$scratch/live-catalog.json"
python3 - "$scratch/local-catalog.json" "$scratch/live-catalog.json" <<'PY'
import json, sys
local = json.load(open(sys.argv[1]))
live = json.load(open(sys.argv[2]))
local_names = [p["name"] for p in local["packs"]]
live_names = [p["name"] for p in live["packs"]]
assert live.get("scope") == "active", live.get("scope")
assert live_names == local_names, (live_names, local_names)
PY

readarray -t registry_fields < <(python3 - "$scratch/live-catalog.json" "$pack_name" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
pack = next(pack for pack in payload["packs"] if pack["name"] == sys.argv[2])
print(pack["download_url"])
print(pack["digest"])
PY
)
download_url="${registry_fields[0]}"
expected_digest="${registry_fields[1]}"
echo "download_url=$download_url"
echo "expected_digest=$expected_digest"

step "4/6 fetch and verify the canonical front-door archive"
curl --fail --silent --show-error --location "$download_url" --output "$scratch/pack.tar.gz"
actual_digest="sha256:$(shasum -a 256 "$scratch/pack.tar.gz" | awk '{print $1}')"
if [[ "$actual_digest" != "$expected_digest" ]]; then
  echo "REFUSED:DIGEST_MISMATCH actual=$actual_digest expected=$expected_digest" >&2
  exit 2
fi
mkdir -p "$scratch/fetched"
tar -xzf "$scratch/pack.tar.gz" -C "$scratch/fetched"
test -f "$scratch/fetched/$pack_name/pack.toml"
test -f "$scratch/fetched/$pack_name/source.ttl"

step "5/6 consume the fetched front door through real ggen"
consumer="$scratch/consumer"
mkdir -p "$consumer"
cat > "$consumer/ontology.ttl" <<'TTL'
@prefix smoke: <https://ggen.dev/marketplace/e2e#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
smoke:RegistryConsumer a rdfs:Class .
TTL
cat > "$consumer/ggen.toml" <<TOML
[project]
name = "active-marketplace-e2e"

[ontology]
source = "ontology.ttl"

[packs]
ggen-platform-pack = { path = "$scratch/fetched/$pack_name" }

[templates]
dir = "."
aggregate_modules = false
TOML
( cd "$consumer" && ggen sync run )

step "6/6 prove the active registry remains exactly the admitted front door plus specialists"
python3 "$root/scripts/marketplace_scope.py" > "$scratch/scope.json"
python3 - "$scratch/scope.json" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1]))
assert payload["active_count"] == 12, payload
assert payload["total_count"] == payload["active_count"] + payload["legacy_count"], payload
PY

echo
echo "ALL GREEN: active marketplace lifecycle verified (catalog -> live fetch -> digest -> consume)"
