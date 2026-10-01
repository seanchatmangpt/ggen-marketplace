// SPDX-License-Identifier: MIT
// Fixture driver for the host-parity court (C10): drives op-examples.json through the host that
// affidavit-consumer-pack generates (affidavit_host.ts, node strip-types) and prints {index:op: response}
// JSON on stdout in the shape of drive.mjs. Not a host: no ABI glue lives here.
// usage: node --experimental-strip-types --no-warnings parity-affidavit-consumer.mjs <affidavit_host.ts> <affidavit.wasm> <op-examples.json> [<tampered.wasm>]
// With a fourth argument the driver instead prints the typed refusal code the host raises for the pin mismatch.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { pathToFileURL } from 'node:url';

const [hostPath, wasmPath, examplesPath, tamperedPath] = process.argv.slice(2);
const { AffidavitHost, AffidavitRefusal } = await import(pathToFileURL(hostPath).href);
const pin = createHash('sha256').update(readFileSync(wasmPath)).digest('hex');

if (tamperedPath) {
  try {
    await AffidavitHost.load(tamperedPath, pin);
    console.log(JSON.stringify({ refused: false }));
  } catch (error) {
    console.log(JSON.stringify({ refused: error instanceof AffidavitRefusal, code: error.code }));
  }
} else {
  const host = await AffidavitHost.load(wasmPath, pin);
  const examples = JSON.parse(readFileSync(examplesPath, 'utf8')).examples;
  const out = {};
  examples.forEach((e, i) => {
    const { op, ...rest } = e.request;
    out[`${i}:${e.op}`] = host.call(op, rest);
  });
  console.log(JSON.stringify(out));
}
