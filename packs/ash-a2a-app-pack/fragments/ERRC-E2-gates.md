# ERRC E2 Gates

Standing: UNVERIFIED

## Accepted forms

- 010: `aap:attribute/aap:primaryKey`, `aap:attrSpec/aap:isPrimaryKey`, `aap:attrSpec/aap:attrKind`
  in (uuid_primary_key, uuid_v7_primary_key, integer_primary_key), `aap:relationship` belongs_to
  with `aap:relPrimaryKey`. Values compared via `LCASE(STR())`.
- 020: skill `aap:ofAction` matched by `aap:name` against `aap:action | aap:manage |
  aap:l06Action | aap:reactorAction` on the same resource.
- 030: `aap:consequence` on any subject, in observe|change|external_do|unknown (optional
  leading colon).

## Residuals: other gates hard-dependent on legacy edges (not edited)

Legacy `aap:action` only (no L02/L06/L15 action acceptance):
L07_010, L07_030, L10_010, L10_020, L14_010, L14_020, L14_030, L17_100, L17_103, L17_104,
L17_106, L17_129, L20_042, L20_045, L11_bridge_shape, L16_090, L05_validation_wellformed,
L02_040 (line 26).

Legacy `aap:attribute` only (L01 `aap:attrSpec` attributes not seen):
L20_040, L17_104, L11_bridge_shape, L02_030 (lines 35, 44), L08_010, L04_030, L05_identity_key_not_attribute,
L05_validation_attribute_not_attribute, L07_040 (also `aap:primaryKey`), L03_030.
(L01_020 intentionally checks both.)

Note: L02_040 and L14/L10 will refuse manage/L06/L15 actions as targets if a TTL declares them
only via those edges. Gate 020 sentence of L02-NOTES is now satisfied.
