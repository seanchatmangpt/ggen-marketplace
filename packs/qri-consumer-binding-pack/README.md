# qri-consumer-binding-pack

Consumer-side binding over `qri-qualification-profile-pack`: a `qcb:ConsumerBinding` names one
capability contract, one chosen realization, one realization profile, one exact artifact pin and
`qcb:authorityCeiling "NONE"`. Anything ambiguous or unpinned is a typed refusal and emits zero
files. Authority ceiling NONE; the pin is identity, never authorization.

## Layout

- `ontology.ttl` qcb delta (ConsumerBinding, RealizationProfile, ArtifactPin, GeneratedProjection,
  ProjectionReceipt, authorityCeiling, `qcb:generation-refusals`); `ontology/alignments.ttl`
  (PROV-O, SPDX, DCAT, ODRL, DCTERMS, SKOS, qri correspondences and scope-note delta justifications for terms with no entailing public parent; nothing imported from any private vocabulary).
- `shapes/qcb.shacl.ttl` SHACL Core admission.
- `gates/*.rq` eleven gates (stems 090-160), one refusal code each; same-stem `witnesses/{pass,fail}`;
  `witnesses/extra/` holds additional single-gate fail variants.
- `runners/semantic_runner.py` court runner (`--extras` for the extra variants).
- `RESOLUTIONS.md` term list for downstream lanes.

## Evidence boundary

Marketplace admission, gate court and SHACL only. No execution authority; generation, hosts and
receipts are projections owned by later lanes.
