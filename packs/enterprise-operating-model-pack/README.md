# enterprise-operating-model-pack

CapabilityPack. The semantic delta for enterprise architecture as strategy plus the ADM as
ontology and gates. It turns a recorded operating-model decision into strategy-derived
requirements and pending-approval architecture skeletons, and refuses inconsistent decisions.

## Where to read

Each quadrant is distinct. Start with the one that matches the task.

- Tutorial: [generate an industry closure](../../docs/tutorials/generate-an-industry-closure.md) (pass 1 is this pack).
- How-to: [add an industry to a closure](../../docs/how-to/add-an-industry-to-closure.md).
- Reference: [enterprise operating model contract](../../docs/reference/enterprise-operating-model-contract.md) (classes, axes truth table, ADM order, every `REFUSED:EOM_*` code, the generated-artifact contract).
- Explanation: [industry closure as architecture strategy](../../docs/explanation/industry-closure-as-architecture-strategy.md).

## What is here

- `ontology.ttl`: operating models as integration x standardization axes, the foundation for
  execution, four maturity stages with ordinals, the engagement model, ADM phases with order and
  artifact kinds, phase records, value-stream anchoring.
- `ontology/enterprise-input.ttl`: the empty input contract. A consumer supplies Turtle only.
- `gates/*.rq`: eight SELECT gates. Zero rows is a pass; any row is a typed `REFUSED:EOM_*` refusal.
- `queries/` and `templates/`: derive `ic:Requirement` rows and `ea:` building-block and contract
  skeletons. Output goes only under `generated/enterprise-operating-model/`.
- `qualification/project/ontology/enterprise-input.ttl`: a synthetic Unification enterprise.
- `witnesses/`: a passing and a failing witness per gate, sharing the gate's exact stem.

## Boundaries

- Identity of ADM phases, operating models, maturity stages and engagement mechanisms stays in
  `togaf-adm-pack`. This pack joins it by `skos:notation` only and a drift test guards the join.
  `togaf-adm-pack`, `enterprise-architecture-pack` and `chatman-togaf-closure-pack` are consumed
  by IRI and never edited.
- The axis obligations (gate 030) and maturity prerequisites (gate 040) are modelling
  interpretations, not quoted rules.
- Stage evidence (gate 040) is a design-time record: a receipt digest of the right shape for the claimed
  stage and every lower stage, with no producer, verifier or observed-outcome check. A maturity claim here
  is a modelling claim, never an observed outcome.
- A strategy is inside the gates only when it carries `eom:ofEnterprise` or a decision answers it.
- No DO authority. DO is not representable (gate 080). Generated contract skeletons are pending
  human approval, claim authority `NONE` and standing `UNKNOWN`.
- Evidence boundary: marketplace admission, rdflib gate execution against witnesses, and, only
  where a real ggen binary exists, bounded isolated manufacture and replay. Without a ggen binary
  manufacture, execution and replay are `BLOCKED:ggen_binary_unavailable`, never ALIVE. This pack
  does not prove strategic fit, decomposition adequacy, native runtime success or customer
  outcomes.
