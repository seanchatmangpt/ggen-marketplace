#!/usr/bin/env bash
# Native pack-gate enforcement: consume the pack through a [packs] entry, once as committed and once
# with a gate-05 violation. Usage (from an empty scratch dir): bash native.sh <pack dir> <this dir>
P=$1; E=$2
for v in good bad; do
  mkdir -p $v/templates
  rsync -a --exclude .ggen --exclude .ggen-v2 $P/ $v/pk/
  cp $E/native-consumer.ttl $v/consumer.ttl
  sed "s/rpv-native-good/rpv-native-$v/" $E/native-consumer.ggen.toml > $v/ggen.toml
done
python3 -c "
p='bad/pk/ontology.ttl'; s=open(p).read(); s2=s.replace('rp:gitArgv \"cat-file -e \$sha:\$path\"','rp:gitArgv \"update-ref refs/heads/x \$sha\"'); assert s2!=s; open(p,'w').write(s2)"
for v in good bad; do
  (cd $v && ggen sync run > sync.log 2>&1; echo "native-$v ggen sync exit=$?")
  grep -v INFO $v/sync.log | grep -o 'FM-PACK-013.\{0,150\}' | head -1
done
for f in unified_receipt_validator.py qualification_runner.py receipt_contract_matrix.json gate_report.json; do
  cmp good/generated/$f $P/generated/$f && echo "IDENTICAL $f"
done
