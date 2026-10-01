// SPDX-License-Identifier: MIT
// Fixture driver (step 9): drives op-examples.json through the GENERATED host (host.mjs), asserts on
// real responses, and prints {index:op: response} JSON on stdout. Not a host: no ABI glue lives here.
// usage: node drive.mjs <generated/node-wasi/host.mjs> <affidavit.wasm> <op-examples.json>
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';

const [hostPath, wasmPath, examplesPath] = process.argv.slice(2);
const { load, AUTHORITY } = await import(pathToFileURL(hostPath).href);
const engine = await load(wasmPath);
const examples = JSON.parse(readFileSync(examplesPath, 'utf8')).examples;
const byOp = Object.fromEntries(examples.map((e) => [e.op, e.request]));
const out = {};
examples.forEach((e, i) => { out[`${i}:${e.op}`] = engine.request(e.request); });
const log = (m) => console.error(`  drive: ${m}`);

// assemble output verifies accepted:true
const assembled = out[`${examples.findIndex((e) => e.op === 'assemble')}:assemble`];
assert.equal(assembled.ok, true);
const verified = engine.request({ op: 'verify', receipt: assembled.receipt });
assert.equal(verified.ok, true);
assert.equal(verified.accepted, true);
log('assemble -> verify accepted:true');

// a tampered chain_hash is refused
const flip = (h) => (h[0] === '0' ? '1' : '0') + h.slice(1);
const tampered = structuredClone(assembled.receipt);
tampered.chain_hash = flip(tampered.chain_hash);
const refused = engine.request({ op: 'verify', receipt: tampered });
assert.notEqual(refused.accepted, true, JSON.stringify(refused));
log(`tampered chain_hash refused (accepted=${refused.accepted})`);

// ops 8 and 9 (the two evidence certifiers): authority NONE, consequence EVIDENCE_ONLY
const certifiers = examples.filter((e) => /^certify_/.test(e.op));
assert.equal(certifiers.length, 2, 'positive control: both certify ops present');
for (const e of certifiers) {
  const r = out[`${examples.indexOf(e)}:${e.op}`];
  assert.equal(r.authority, 'NONE', e.op);
  assert.equal(r.consequence, 'EVIDENCE_ONLY', e.op);
  log(`${e.op}: authority NONE consequence EVIDENCE_ONLY`);
}
assert.equal(AUTHORITY, 'NONE');
console.log(JSON.stringify(out));
