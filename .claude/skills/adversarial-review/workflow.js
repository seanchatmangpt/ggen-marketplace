export const meta = {
  name: 'adversarial-review',
  description: 'Four-lens adversarial review (RDF correctness, TDD rigor, formal correctness, pragmatism) with independent verification per finding',
  phases: [
    { title: 'Review', detail: 'one agent per lens' },
    { title: 'Verify', detail: 'two independent skeptics per finding' },
  ],
}

const FINDINGS_SCHEMA = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          file: { type: 'string' },
          line: { type: 'number' },
          summary: { type: 'string' },
          failureScenario: { type: 'string' },
        },
        required: ['file', 'summary', 'failureScenario'],
      },
    },
  },
  required: ['findings'],
}

const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    refuted: { type: 'boolean' },
    reason: { type: 'string' },
  },
  required: ['refuted', 'reason'],
}

const LENSES = [
  {
    key: 'rdf-correctness',
    label: 'Semantic web / RDF correctness',
    prompt: (target) => `Review ${target} through the lens of Tim Berners-Lee's Linked ` +
      `Data principles and SPARQL query-correctness discipline. You are not impersonating ` +
      `him -- apply his documented methodology as a rigor standard. For every SPARQL query ` +
      `in a gate or template: does it actually bind what the template consumes downstream? ` +
      `For every ontology individual/class: does it follow RDF/OWL conventions (no ` +
      `literal-typed subjects, no undeclared predicates used as if declared)? For every ` +
      `template's projected output: does it semantically match the ontology facts it claims ` +
      `to derive from, or does it silently diverge? Report ONLY findings with a real file:line ` +
      `citation and a concrete failure scenario (specific input/state -> wrong output). Do not ` +
      `report style preferences or anything you cannot point to in the actual files.`,
  },
  {
    key: 'tdd-rigor',
    label: 'Testing discipline / TDD rigor',
    prompt: (target) => `Review ${target} through the lens of Kent Beck's Chicago-school ` +
      `classicist testing discipline. You are not impersonating him -- apply his documented ` +
      `methodology as a rigor standard. For every test: does it use real collaborators or ` +
      `does it mock something this codebase owns or could run in-process/locally? Are ` +
      `assertions state-based (real returned/persisted values) or interaction-based ("was X ` +
      `called")? For every claim in a description/README that something is "verified" or ` +
      `"tested": is there an actual citable passing run, or is it asserted without evidence? ` +
      `Report ONLY findings with a real file:line citation and a concrete failure scenario. Do ` +
      `not report style preferences.`,
  },
  {
    key: 'formal-correctness',
    label: 'Formal correctness / interface design',
    prompt: (target) => `Review ${target} through the lens of Barbara Liskov's ` +
      `substitutability principle and strict-schema discipline. You are not impersonating her ` +
      `-- apply her documented methodology as a rigor standard. For every manifest/schema file ` +
      `(pack.toml, ggen.toml, qualification.toml): does every field actually validate against ` +
      `the real parser/tool this repo pins (not just look syntactically plausible on a read-` +
      `through)? Are contracts checked exhaustively, or does the review assume validity from ` +
      `visual inspection alone? Flag any field, table, or key that isn't demonstrably accepted ` +
      `by the real tool. Report ONLY findings with a real file:line citation and a concrete ` +
      `failure scenario (what breaks, and how you'd prove it breaks). Do not report style ` +
      `preferences.`,
  },
  {
    key: 'pragmatism',
    label: 'Software engineering pragmatism',
    prompt: (target) => `Review ${target} through the lens of YAGNI/simplicity discipline and ` +
      `no-overclaiming rigor. For every abstraction, config option, or generalization: is it ` +
      `actually used, or speculative? For every claim of correctness/completeness/verification: ` +
      `is it backed by a citable run, or asserted? Would a simpler design serve the same real, ` +
      `currently-existing requirement? Report ONLY findings with a real file:line citation and ` +
      `a concrete failure scenario or concrete cost (e.g. "this table is read nowhere, dead ` +
      `code"). Do not report generic advice.`,
  },
]

function refutePrompt(finding) {
  return `Try to REFUTE this finding. Read the cited file yourself and check it against the ` +
    `actual content -- do not trust the finding's citation blindly. Default to refuted=true if ` +
    `you cannot confirm the cited file:line actually shows what the finding claims, or if the ` +
    `failure scenario does not actually follow from the code as written.\n\n` +
    `File: ${finding.file}${finding.line ? ':' + finding.line : ''}\n` +
    `Summary: ${finding.summary}\n` +
    `Failure scenario: ${finding.failureScenario}`
}

phase('Review')
const target = args.targetDescription
const lensResults = await pipeline(
  LENSES,
  (lens) => agent(lens.prompt(target), {
    label: `review:${lens.key}`,
    phase: 'Review',
    schema: FINDINGS_SCHEMA,
  }),
  (result, lens) => (result?.findings ?? []).map((f) => ({ ...f, lens: lens.label }))
)

const allFindings = lensResults.flat()
log(`${allFindings.length} raw findings across ${LENSES.length} lenses`)

phase('Verify')
const verified = await parallel(
  allFindings.map((finding) => async () => {
    const votes = await parallel(
      Array.from({ length: 2 }, () => () =>
        agent(refutePrompt(finding), { phase: 'Verify', schema: VERDICT_SCHEMA })
      )
    )
    const refutations = votes.filter(Boolean).filter((v) => v.refuted).length
    const survived = refutations < 2
    return survived ? { ...finding, verdict: refutations === 0 ? 'CONFIRMED' : 'PLAUSIBLE' } : null
  })
)

const confirmed = verified.filter(Boolean)
log(`${confirmed.length}/${allFindings.length} findings survived adversarial verification`)

// Dedupe: same file + overlapping summary text across lenses -> keep the first (sharper
// framing tends to come from the more specific lens, which runs earlier in LENSES order).
const seen = new Set()
const deduped = []
for (const f of confirmed) {
  const key = `${f.file}:${f.line ?? ''}:${f.summary.slice(0, 60)}`
  if (seen.has(key)) continue
  seen.add(key)
  deduped.push(f)
}

return deduped
