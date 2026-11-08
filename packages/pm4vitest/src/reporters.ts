/**
 * pm4vitest.reporters — TAP v13 and JUnit XML emitters for process
 * intelligence outcomes, for CI consumption.
 */

export interface ProcessTestOutcome {
  name: string;
  passed: boolean;
  skip?: boolean;
  skipReason?: string;
  diagnostics?: Record<string, unknown>;
  durationSeconds?: number;
}

function yamlScalar(v: unknown): string {
  if (typeof v === 'string') return v;
  return JSON.stringify(v);
}

/** Render outcomes as TAP v13 with YAML diagnostic blocks. */
export function toTAP13(outcomes: readonly ProcessTestOutcome[], plan?: number): string {
  const lines: string[] = ['TAP version 13'];
  const total = plan ?? outcomes.length;
  lines.push(`1..${total}`);
  outcomes.forEach((o, i) => {
    const status = o.passed ? 'ok' : 'not ok';
    lines.push(`${status} ${i + 1} - ${o.name}${o.skip ? ` # SKIP ${o.skipReason ?? ''}` : ''}`);
    if (o.diagnostics && Object.keys(o.diagnostics).length > 0) {
      lines.push('  ---');
      for (const [k, v] of Object.entries(o.diagnostics)) {
        lines.push(`  ${k}: ${yamlScalar(v)}`);
      }
      lines.push('  ...');
    }
  });
  return lines.join('\n') + '\n';
}

function escapeXml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/** Render outcomes as JUnit XML for CI systems. */
export function toJUnitXml(outcomes: readonly ProcessTestOutcome[], suiteName = 'pm4vitest'): string {
  const total = outcomes.length;
  const failures = outcomes.filter((o) => !o.passed && !o.skip).length;
  const skipped = outcomes.filter((o) => o.skip === true).length;
  const totalTime = outcomes.reduce((s, o) => s + (o.durationSeconds ?? 0), 0);
  const timestamp = new Date().toISOString();

  const xml: string[] = [
    '<?xml version="1.0" encoding="utf-8"?>',
    `<testsuites name="${escapeXml(suiteName)}" tests="${total}" failures="${failures}" errors="0" skipped="${skipped}" time="${totalTime.toFixed(4)}">`,
    `  <testsuite name="${escapeXml(suiteName)}" tests="${total}" failures="${failures}" errors="0" skipped="${skipped}" time="${totalTime.toFixed(4)}" timestamp="${timestamp}">`,
  ];

  for (const o of outcomes) {
    xml.push(
      `    <testcase name="${escapeXml(o.name)}" classname="pm4vitest" time="${(o.durationSeconds ?? 0).toFixed(4)}">`,
    );
    if (o.skip) {
      xml.push(`      <skipped message="${escapeXml(o.skipReason ?? 'Skipped')}"/>`);
    } else if (!o.passed) {
      const msg = escapeXml(String(o.diagnostics?.['message'] ?? 'Test failed'));
      const diag = escapeXml(JSON.stringify(o.diagnostics ?? {}));
      xml.push(`      <failure message="${msg}">${diag}</failure>`);
    }
    xml.push('    </testcase>');
  }

  xml.push('  </testsuite>');
  xml.push('</testsuites>');
  return xml.join('\n') + '\n';
}
