# forensic-audit-dossier-pack

OCEL 2.0-aligned forensic audit dossier pack. Generates a deterministic,
content-addressed dossier exporter from an fa: event/object/relationship
vocabulary.

## Semantics (alignment receipt)

Aligned with ash_pplan `ProcessEvidence.Event`
(`lib/ash_pplan/process_evidence/event.ex`): events carry
id/activity/timestamp/objects/attributes/subject_id; objects are unique-id'd;
relationships reference event+object ids with a qualifier. The pack pins the
alignment as gate 020 over ontology.ttl, not prose.

## Generated exporter

`generated/dossier_exporter.py` (Python 3 stdlib only) assembles
{events, objects, subject_id} into a canonical JSON dossier:
- canonical digest serialization: sorted keys, separators, UTF-8
- explicit top-level field order: subject_id, events, objects, digest
- sha256 content binding over events+objects+subject_id
- typed refusal (exit 2, `REFUSED DANGLING_OBJECT_REF` on stderr) when a
  relationship references a nonexistent object id, fail-closed

## Consumer use

Copy ggen.toml, bind your fa:DossierConfig individual in ontology.ttl
(exportModule/digestAlgorithm/canonicalization/subjectIdField/
refuseOnDanglingObjectRef), run `ggen sync run`; courts and shapes come with
the pack.

## Layout

Standard pack layout: ontology.ttl, shapes.ttl, queries/, templates/,
generated/, gates/ (000 shell, 010/020 .rq, 030 falsifier court with real
fixtures), qualification/fixtures/.
