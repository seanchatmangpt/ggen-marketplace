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
        required: ['file', 'line', 'summary', 'failureScenario'],
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

const SYNTHESIS_SCHEMA = {
  type: 'object',
  properties: {
    keepIndices: {
      type: 'array',
      items: { type: 'number' },
      description: 'Indices (into the provided findings list, 0-based) to KEEP -- one per ' +
        'distinct underlying defect, preferring the sharper framing when multiple findings ' +
        'describe the same defect.',
    },
  },
  required: ['keepIndices'],
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
      `-- apply her documented methodology as a rigor standard. Reading a manifest file and ` +
      `judging it "looks valid" is NOT this lens's job -- that already failed to catch a real ` +
      `defect once (a pack.toml shipped a [semantic_crown] TOML table that was syntactically ` +
      `perfect and still got rejected by the real ggen binary's deny_unknown_fields schema). ` +
      `You MUST actually invoke the real, pinned ggen binary against every manifest file ` +
      `(pack.toml, ggen.toml, qualification.toml) in ${target} before reporting anything as ` +
      `valid or invalid -- a claim not backed by a real command's exit code and output is not a ` +
      `finding, it's a guess. Concrete recipe: find the repo root containing marketplace.toml ` +
      `(walk up from ${target} if it is a path outside the current working directory) to get ` +
      `the pinned ggen version, then locate a local ggen binary (try \`which ggen\`, ` +
      `\`~/.local/bin/ggen\`, or search common install paths) -- if none of pack.toml's own ` +
      `repo's tooling is reachable, run \`python3 <repo-root>/scripts/qualify_packs.py --ggen ` +
      `<ggen-binary-path> --shard-index 0 --shard-count 1 --timeout-seconds 5 --report ` +
      `/tmp/adversarial-review-lens-formal-correctness.json\` from the repo root (if ${target} ` +
      `is OUTSIDE that repo root -- e.g. a scratch worktree at a different path -- run ` +
      `\`<ggen-binary> sync run\` directly against a minimal scratch ggen.toml wiring \`[packs] ` +
      `"<name>" = { path = "<absolute path to target>" }\` in a temp directory, per this repo's ` +
      `own scripts/qualify_packs.py:projection_ggen_toml/semantic_ggen_toml functions for the ` +
      `exact wiring shape. NEVER symlink or copy the target pack directory into that repo's own ` +
      `packs/ directory -- this repo's scripts/marketplace.py refuses any symlink under packs/, ` +
      `and a stray copied directory becomes an unadmitted pack that corrupts the marketplace ` +
      `fingerprint on the user's next validate run; review of that repo must stay read-only. ` +
      `Read the report/output for REFUSED status and cite the exact error ` +
      `message. Only after you have a real command's output may you report a finding about ` +
      `schema validity -- cite the command you ran and its output as your failure scenario, not ` +
      `a description of what you'd expect to happen. Report ONLY findings with a real file:line ` +
      `citation and a concrete failure scenario backed by an actual command run. Do not report ` +
      `style preferences.`,
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

function refutePrompt(finding, target) {
  return `Try to REFUTE this finding. It is about this exact review target -- do not check any ` +
    `other repo, checkout, or commit; if the finding's cited file is a relative path, resolve it ` +
    `relative to THIS target, not your own working directory, and if your own working directory ` +
    `contains a same-named file from a different commit/checkout, that is a DIFFERENT file and ` +
    `is not what this finding is about:\n\n` +
    `Review target: ${target}\n\n` +
    `Read the cited file (resolved against the review target above) yourself and check it ` +
    `against the actual content -- do not trust the finding's citation blindly. Default to ` +
    `refuted=true if you cannot confirm the cited file:line, resolved against the review target, ` +
    `actually shows what the finding claims, or if the failure scenario does not actually follow ` +
    `from the code as written. Do NOT refute a finding merely because a same-named file elsewhere ` +
    `(e.g. in your own cwd, a different commit, or a different checkout) shows different content ` +
    `-- only the review target's copy of the file is relevant.\n\n` +
    `File: ${finding.file}${finding.line ? ':' + finding.line : ''}\n` +
    `Summary: ${finding.summary}\n` +
    `Failure scenario: ${finding.failureScenario}`
}

let parsedArgs = args
if (typeof parsedArgs === 'string') {
  try {
    parsedArgs = JSON.parse(parsedArgs)
  } catch (err) {
    throw new Error(`adversarial-review: args arrived as a string and failed to JSON.parse: ${err.message}`)
  }
}
if (typeof parsedArgs?.targetDescription !== 'string' || parsedArgs.targetDescription.length === 0) {
  throw new Error('adversarial-review: args.targetDescription is required and must be a non-empty string')
}

phase('Review')
const target = parsedArgs.targetDescription
const CITATION_INSTRUCTION = `\n\nIMPORTANT on citations: report every finding's "file" as the ` +
  `full path you actually read it from, unambiguous regardless of anyone else's working ` +
  `directory (if the review target above is a path, prefix relative paths with it; do not report ` +
  `a bare repo-relative path like "packs/foo/pack.toml" with no indication of which checkout it's ` +
  `in). This finding will later be verified by a different agent that may be sitting in a ` +
  `different checkout/commit of the same repo -- an ambiguous path risks it checking the wrong file.`
const lensResults = await pipeline(
  LENSES,
  (lens) => agent(lens.prompt(target) + CITATION_INSTRUCTION, {
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
        agent(refutePrompt(finding, target), { phase: 'Verify', schema: VERDICT_SCHEMA })
      )
    )
    const refutations = votes.filter(Boolean).filter((v) => v.refuted).length
    const survived = refutations < 2
    return survived ? { ...finding, verdict: refutations === 0 ? 'CONFIRMED' : 'PLAUSIBLE' } : null
  })
)

const confirmed = verified.filter(Boolean)
log(`${confirmed.length}/${allFindings.length} findings survived adversarial verification`)

// Filter out findings missing file, line, or failureScenario
const filtered = confirmed.filter((f) => f.file && f.line && f.failureScenario)
const dropped = confirmed.length - filtered.length
if (dropped > 0) {
  log(`${dropped} findings dropped for missing file/line/failureScenario`)
}

// Cross-lens dedupe: the same underlying defect can surface from two lenses with entirely
// different phrasing, so a string-prefix match on the summary essentially never catches a
// real duplicate. Group by file (same file = candidate duplicates regardless of lens), and
// for any file with more than one surviving finding, dispatch one synthesis agent call to
// judge which findings describe the SAME underlying defect and which to keep.
const byFile = new Map()
for (const f of filtered) {
  const list = byFile.get(f.file) ?? []
  list.push(f)
  byFile.set(f.file, list)
}

const dedupeGroups = await parallel(
  Array.from(byFile.entries()).map(([file, findings]) => async () => {
    if (findings.length === 1) return findings
    const listing = findings
      .map((f, i) => `[${i}] lens=${f.lens} line=${f.line} summary=${f.summary}\n    failureScenario=${f.failureScenario}`)
      .join('\n')
    const prompt = `These findings were all reported against the same file (${file}) by ` +
      `different review lenses. Some may describe the SAME underlying defect from different ` +
      `angles (not merely the same file) -- identify those duplicates and keep only one per ` +
      `distinct underlying defect, preferring the sharper/more concrete framing (the one with ` +
      `the more specific failure scenario or command output). Findings that describe genuinely ` +
      `different defects in the same file must ALL be kept.\n\n${listing}`
    const result = await agent(prompt, { phase: 'Review', schema: SYNTHESIS_SCHEMA })
    const keep = new Set(Array.isArray(result?.keepIndices) ? result.keepIndices : findings.map((_, i) => i))
    const kept = findings.filter((_, i) => keep.has(i))
    return kept.length > 0 ? kept : findings
  })
)

const deduped = dedupeGroups.flat()

return deduped
