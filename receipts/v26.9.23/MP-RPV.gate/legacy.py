#!/usr/bin/env python3
"""Old (420bc91) vs new generated validator on the five earlier contracts.
Usage (from an empty scratch dir): legacy.py <marketplace worktree> -> one line per run + a total."""
import copy, json, os, subprocess, sys
WT = sys.argv[1]
NEW = os.path.join(WT, 'packs/receipt-provenance-unification-pack/generated/unified_receipt_validator.py')
old = subprocess.run(['git', '-C', WT, 'show', '420bc91e7c1e291be73ab749b7e443252bc7bab8:packs/receipt-provenance-unification-pack/generated/unified_receipt_validator.py'], capture_output=True, check=True).stdout
open('old_validator.py', 'wb').write(old)
crown = json.load(open('/Users/sac/gym-ecosystem/artifacts/autonomic-crown.json'))
boot = json.load(open('/Users/sac/gym-ecosystem/vendor/ggen-ecosystem/receipts/bootstrap-ggen-ecosystem-sync.json'))
cases = {'crown': crown, 'boot': boot}
c = copy.deepcopy(crown); c['submodules'][0]['current'] = 'NOTASHA'; cases['crown_notasha'] = c
c = copy.deepcopy(crown); c['submodules'][1]['default_ref'] = 'main'; cases['crown_badref'] = c
c = copy.deepcopy(crown); del c['submodules'][2]['url']; cases['crown_missing_elem_field'] = c
c = copy.deepcopy(crown); c['changed_count'] = 1.0; cases['crown_float_count'] = c
c = copy.deepcopy(boot); c['standing'] = 'ALIVE'; c['artifact'] = 'todo'; cases['boot_alive_placeholder'] = c
c = copy.deepcopy(boot); c['ggen']['release'] = None; cases['boot_null'] = c
c = copy.deepcopy(boot); c['standing'] = 'REFUSED:X'; cases['boot_colon'] = c
cases['clean_session_min'] = {'receipt_id': 'a' * 64, 'task_identity': 'b' * 64, 'standing': 'REFUSED:X', 'state_digest': 'c' * 64}
cases['ledger_min'] = {'kind': 'k', 'issued_at_ms': 1, 'digest': 'd' * 64, 'body': {'sequence': 1, 'previous_receipt_digest': 'e' * 64}}
cases['ledger_float'] = {'kind': 'k', 'issued_at_ms': 1.0, 'digest': 'd' * 64, 'body': {'sequence': 1, 'previous_receipt_digest': 'e' * 64}}
cases['empty_obj'] = {}
for name, doc in cases.items():
    json.dump(doc, open(f'{name}.json', 'w'))
same = diff = 0
for f in sorted(n for n in os.listdir('.') if n.endswith('.json')):
    for extra in ([], ['--contract=gym_autonomic_crown'], ['--contract=clean_session'], ['--contract=ecosystem_bootstrap'], ['--contract=ecosystem_sync'], ['--contract=autofde_ledger']):
        o = subprocess.run(['python3', 'old_validator.py', f, *extra], capture_output=True).returncode
        n = subprocess.run(['python3', NEW, f, *extra], capture_output=True).returncode
        print('SAME' if o == n else 'DIFF', o, n, f, *extra)
        same += o == n; diff += o != n
print(f'LEGACY old(420bc91 generated validator) vs new(66df30a): same={same} diff={diff}')
