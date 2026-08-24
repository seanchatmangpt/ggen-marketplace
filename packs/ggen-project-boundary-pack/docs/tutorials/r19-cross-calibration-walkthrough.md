# Walk through cross-calibrated composition

Start with candidate composition facts and observability calibration facts. Materialize a `gpb:CrossCalibratedComposition` edge that links both, then run the R19 query family. Keep every frontier member until a typed falsifier removes only the failing edge. The balanced fixture demonstrates an ALIVE reversible option; adversarial fixtures demonstrate PARTIAL_ALIVE, BLOCKED, and UNSUPPORTED without collapsing adjacent candidates.
