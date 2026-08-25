# Reference: R66 receipt-realization calibration

R66 adds `ReceiptRealizationCalibration`, `ConsumerEvidenceReturn`, `RealizationCalibrationMeasurement`, `ReceiptAssimilationGap`, `IndependentConsumerRoot`, and `PortfolioEvidenceProjection` to the epistemic sensor factory vocabulary while reusing PROV-O, DQV, DCAT, DCTERMS, and ODRL.

Sensor range: `1452`–`1501` inclusive, exactly 50 executable SPARQL queries. Projection query: `1502_r66_receipt_realization_projection.rq`.

Core metrics: predicted/realized consumer fanout; returned/assimilated receipt counts; independent evidence-root count; predicted/realized opportunity yield, dependency relief, and epistemic score; receipt and assimilation coverage; return and assimilation latency.

Standing is scoped. `ALIVE` for R66 requires the exact R66 court to execute all 50 sensors on the exact admitted head. Sensor 1496 is the only R66 1000X admission query; no matching row means `NOT_ADMITTED`.
