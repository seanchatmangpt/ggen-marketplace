# insa-law-pack

**Class/Profile:** CapabilityPack · projection · **Authority:** SELECT/CONSTRUCT, no DO (consequential actuation stays behind BRCE admission).
**Identity:** `urn:insa-law:` — canonical RDF projection of insa-replaw's eight-vow sealed typestate law (`VowEngine` Source→Pattern→Field→Motion→Receiver→Fruit→Receipt→Rest, `eight_vow.rs` L172-321).

Capability command (from the repo root or the pack dir):

```bash
cd packs/insa-law-pack && ggen sync run && python3 verify.py
```

Evidence boundary: fail-closed SPARQL gates prove exactly 8 transitions
(`010_exactly_8_transitions.rq`), linear chain closure Source..Rest with no
gaps/duplicates/skips (`020_linear_chain_closure.rq`), and every typed
`BridgeError` variant exercised by ≥1 transition (`030_refusal_exercise.rq`).
Generated `vow_order.rs` is a classification/projection consequence — its
existence is not runtime correctness of insa-replaw, and no cross-repo
boundary is exercised here.
