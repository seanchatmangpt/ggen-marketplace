# otel-weaver-pack

A ggen marketplace source pack that manufactures a governed OpenTelemetry Weaver registry rather than hand-maintaining telemetry schema files.

## Coverage

The pack projects an application-registry `manifest.yaml`, `.weaver.toml`, Weaver V2 service model, Rego admission policy, GitHub Actions registry/static + runtime live-check gates, and generated reference documentation. Its ontology also models Weaver check, package, generate, diff, emit, live-check, MCP, infer, and JSON Schema surfaces with explicit standing.

The current runtime target is OpenTelemetry Weaver **v0.25.1**. `resolve` is intentionally not a primary generated workflow because Weaver has deprecated it in favor of `generate` and `package`.

## Manufacture

```bash
ggen sync
weaver registry check -r . --v2 -p policies --future
weaver registry package -r . --v2 -p policies -o ./dist
```

Generated consumer files are consequences and should not be copied back into this marketplace as canonical metadata.

## Runtime proof

Static `weaver registry check` validates registry syntax/semantics/policies. It does **not** prove an application emits conforming telemetry. Runtime standing requires the exact application to export OTLP into `weaver registry live-check`, with `fail_on = "violation"`, and a preserved report.

## Authority

`infer` produces raw candidate observations, not admitted schema. MCP is a semantic read/tool surface, not actuation authority. `emit` is bounded to explicit test receivers. The generated CI includes a deliberate placeholder integration hook that downstream repositories must replace with their real subject exercise before claiming runtime ALIVE.
