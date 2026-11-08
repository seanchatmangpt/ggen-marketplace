export interface TestOutcome {
  name: string;
  ok: boolean;
  durationMs?: number;
  diagnostic?: string;
}

export function toTAP13(outcomes: readonly TestOutcome[]): string {
  const lines: string[] = ['TAP version 13', `1..${outcomes.length}`];

  outcomes.forEach((outcome, idx) => {
    const num = idx + 1;
    const status = outcome.ok ? 'ok' : 'not ok';
    lines.push(`${status} ${num} - ${outcome.name}`);
    if (!outcome.ok && outcome.diagnostic) {
      lines.push('  ---');
      outcome.diagnostic.split('\n').forEach((d) => lines.push(`  ${d}`));
      lines.push('  ...');
    }
  });

  return lines.join('\n');
}

export function toJUnitXml(outcomes: readonly TestOutcome[], suiteName = 'pm4playwright'): string {
  const total = outcomes.length;
  const failures = outcomes.filter((o) => !o.ok).length;
  const timeSec = outcomes.reduce((acc, o) => acc + (o.durationMs ?? 0), 0) / 1000.0;

  const lines: string[] = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    `<testsuites name="${suiteName}" tests="${total}" failures="${failures}" time="${timeSec.toFixed(3)}">`,
    `  <testsuite name="${suiteName}" tests="${total}" failures="${failures}" time="${timeSec.toFixed(3)}">`,
  ];

  for (const o of outcomes) {
    const t = ((o.durationMs ?? 0) / 1000.0).toFixed(3);
    lines.push(`    <testcase name="${escapeXml(o.name)}" time="${t}">`);
    if (!o.ok) {
      lines.push(
        `      <failure message="Conformance or SLA assertion failed">${escapeXml(o.diagnostic ?? '')}</failure>`
      );
    }
    lines.push('    </testcase>');
  }

  lines.push('  </testsuite>', '</testsuites>');
  return lines.join('\n');
}

function escapeXml(unsafe: string): string {
  return unsafe
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
