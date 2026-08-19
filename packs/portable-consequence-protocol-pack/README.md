# portable-consequence-protocol-pack

Runtime-neutral conformance fragment for consequential systems.

```text
Intent -> exact AuthorityDecision -> ReceiptCapability -> DO
      -> observed Consequence -> Receipt -> Replay
```

No planner, generator, CLI, MCP/A2A transport, repository, or implementation receives ambient authority. If an exact consequence cannot be receipted and replayed, consequential DO is refused before actuation.

## Public semantics first

The RDF graph uses PROV-O, ODRL, EARL, Dublin Core, and SKOS. `urn:portable-consequence:*` is only the smallest current remainder needed for digest binding, receipt capability, replay identity, and standing codes. The remainder is disposable: replace a custom term when a public equivalent is proven without semantic loss.

The protocol does not require Chatman Ecosystem, ggen, GymAct, AutoFDE, a particular language, transport, or digest algorithm at runtime.

## Conformance

```bash
python3 gates/verify_protocol.py
python3 gates/verify_protocol.py /path/to/foreign-implementation
```

A foreign implementation reads one JSON request from stdin and writes one JSON result to stdout. The bundled Python witness is dependency-free and is executed as a separate process by the court.

The vectors cover positive admission and negative authority, receiptability, receipt-binding, and replay-conflict cases. Passing them proves only this bounded fragment; it grants no production, regulatory, security, or external-authority standing.

## Extinction property

Delete the bundled witness and point the court at an independent implementation. If the same vectors pass, the protocol survives the reference implementation. The witness is evidence, not authority.
