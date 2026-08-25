# Tutorial: trace one control-plane causal chain

Use this pack to distinguish a real Project-memory consequence from nearby workflow activity.

1. Identify one bounded Project-memory request and its exact request commit SHA.
2. Represent the request as `cpc:Request` with `cpc:requestId`, `cpc:headSha`, currentness, provenance, and exact-subject evidence.
3. Represent only the proxy workflow that actually consumed that request as a `cpc:WorkflowRun`, linked with `prov:used`.
4. Represent the returned typed receipt as `cpc:Receipt`, linked with `prov:wasGeneratedBy`.
5. Run `python3 tests/test_contract.py` from the pack directory context (or the repository-root qualification command).
6. Inspect court `050_clean_causal_chain.sparql` for the positive crown and courts 001–049 for falsifiers and quality observations.

The result is evidence about request → relevant workflow → receipt causality. It is not authority to actuate another system.
