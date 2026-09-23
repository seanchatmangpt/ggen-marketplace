#!/usr/bin/env python3
"""Anti-vacuity of the pack gates: one-edit ontology mutants through bin/run-gates.py.
Usage (from a scratch dir): gatemut.py <pack dir>  -> one line per mutant; each must exit 1."""
import sys, subprocess
P = sys.argv[1]
src = open(P + '/ontology.ttl').read()
muts = {
 'm04_drop_line.ttl': src.replace('rp:gitArgv "notes --ref=$ref list $sha" ;\n    rp:sourceFile "/Users/sac/.claude/dfcm/receipt.schema.json" ; rp:sourceLine 55 .', 'rp:gitArgv "notes --ref=$ref list $sha" ;\n    rp:sourceFile "/Users/sac/.claude/dfcm/receipt.schema.json" .'),
 'm05_write_probe.ttl': src.replace('rp:gitArgv "cat-file -e $sha:$path"', 'rp:gitArgv "update-ref refs/heads/x $sha"'),
 'm05_option_token.ttl': src.replace('rp:gitArgv "cat-file -e $sha:$path"', 'rp:gitArgv "cat-file -e --output=x $sha:$path"'),
 'm02_uncited_validator.ttl': src.replace('rp:sourceFile "/Users/sac/.claude/dfcm/validate_receipt.py" ;\n    rp:sourceLine 12 ;', 'rp:sourceLine 12 ;'),
 'm01_actuation.ttl': src + '\nrp:res_blob_at_commit rp:actuates rp:c_dfcm_fleet .\n',
}
for name, text in muts.items():
    assert text != src, name
    open(name, 'w').write(text)
    r = subprocess.run(['python3', P + '/bin/run-gates.py', name, P + '/gates'], capture_output=True, text=True)
    print(name, 'exit', r.returncode, [l for l in r.stdout.splitlines() if 'VIOLATION' in l])
