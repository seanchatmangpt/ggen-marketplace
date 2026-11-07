#!/bin/sh
# Gate 030 -- the falsifier court, real execution over real files (Chicago:
# no mocks, assert on final state). (a) valid fixture -> digest equals an
# independently computed sha256 AND a second run is byte-identical;
# (b) dangling-ref fixture -> typed REFUSED, nonzero exit. A court that
# passes on (b) is itself FAIL.
set -eu
cd "$(dirname "$0")/.."
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
cp qualification/fixtures/dangling.json "$TMP/events_dangling.json"
cp qualification/fixtures/objects.json "$TMP/objects.json"
cp qualification/fixtures/valid.json "$TMP/events.json"

python3 generated/dossier_exporter.py --events "$TMP/events.json" \
  --objects "$TMP/objects.json" --subject-id "subject-001" --out "$TMP/out1.json"
python3 generated/dossier_exporter.py --events "$TMP/events.json" \
  --objects "$TMP/objects.json" --subject-id "subject-001" --out "$TMP/out2.json"

if ! cmp -s "$TMP/out1.json" "$TMP/out2.json"; then
  echo "gates/030 FAIL: exporter not deterministic (run 1 != run 2)" >&2
  exit 1
fi

# Independent digest recomputation over the digest-free payload.
python3 - "$TMP/out1.json" <<'PY'
import hashlib, json, sys
d = json.load(open(sys.argv[1]))
claimed = d.pop("digest")
payload = {"subject_id": d["subject_id"], "events": d["events"], "objects": d["objects"]}
actual = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()
if claimed != actual:
    sys.stderr.write("gates/030 FAIL: digest mismatch claimed=%s actual=%s\n" % (claimed, actual))
    sys.exit(1)
PY

# Falsifier: dangling object reference must REFUSE (exit 2), never pass.
if python3 generated/dossier_exporter.py --events "$TMP/events_dangling.json" \
     --objects "$TMP/objects.json" --subject-id "subject-001" --out "$TMP/out_dangling.json" 2>"$TMP/err.txt"; then
  echo "gates/030 FAIL: dangling object reference was accepted (court cannot flip)" >&2
  exit 1
fi
grep -q "REFUSED DANGLING_OBJECT_REF" "$TMP/err.txt" || {
  echo "gates/030 FAIL: refusal not typed: $(cat "$TMP/err.txt")" >&2
  exit 1
}
echo "gates/030 ok: deterministic double-run byte-identical, digest verified, dangling-ref refused"
