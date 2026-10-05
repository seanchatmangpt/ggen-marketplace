# GCP Commerce Sim API

Wire-level reference for `k8s/gcp-marketplace-sim/server.py`, a
`http.server.HTTPServer` speaking the Google Cloud Commerce Procurement and
Service Control surface. All responses are `application/json` with `Server: ESF`
and `X-Content-Type-Options: nosniff` headers.

## Configuration

| Env var | Default | Effect |
|---|---|---|
| `AAIF_SIM_PORT` | `8443` | Listen port (binds `0.0.0.0`) |
| `AAIF_SIM_DISCOVERY_DIR` | `/app` | Directory holding the discovery JSON files |

## Endpoints

### x509 metadata — GET

Path suffix:
`/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com`.

Response: a JSON object mapping the SHA-1 digest of the certificate DER
(`KEY_ID`) to the certificate PEM string, e.g. `{ "<sha1-of-DER>": "<PEM>" }`.
The keypair is RS256, 2048-bit, generated at process start; the self-signed
certificate is valid 365 days with CN
`cloud-commerce-partner@system.gserviceaccount.com`.

### Discovery documents — GET

Any path containing `cloudcommerceprocurement` and `$discovery/rest` serves the
file `<AAIF_SIM_DISCOVERY_DIR>/procurement_discovery.json`; any path containing
`servicecontrol` and `$discovery/rest` serves
`<AAIF_SIM_DISCOVERY_DIR>/servicecontrol_discovery.json`. Response is the file
content verbatim as JSON.

### /healthz — GET

Response: `{"status": "SERVING", "service": "cloudcommerceprocurement.googleapis.com"}`.

### /v1/billing/summary — GET

Response fields:

- `totalOperations` — count of recorded usage reports
- `totalMeteredUnits` — sum of `int64Value` over all reports
- `remainingQuota` — remaining `default` quota bucket
- `unitPriceUsd` — `0.05`
- `totalRealizedRevenueUsd` — units times price, rounded to 2 decimals
- `accounts` — full `ACCOUNTS` map
- `entitlements` — full `ENTITLEMENTS` map
- `recentReports` — last 10 usage report records

### Entitlement lookup — GET

Any path containing `/entitlements` looks up the last path segment (query
stripped) as entitlement id.

Response: the entitlement record (see `:approve` below), or error envelope
`{"error": {"code": 404, "message": "Entitlement <id> not found"}}`.

### /oauth2/v4/token (also `/token`) — POST

Request body is ignored. Response: `access_token` (`ya29.c.aaif-sim-<epoch>`),
`expires_in` (`3600`), `token_type` (`"Bearer"`).

### Account :approve — POST

Path: `.../accounts/<acc_id>:approve`. Creates the account record:

- `name` — `providers/demo-provider/accounts/<acc_id>`
- `state` — `ACCOUNT_ACTIVE`
- `createTime`, `approvalTime` — RFC3339 UTC timestamps

### Entitlement :approve — POST

Path: `.../entitlements/<ent_id>:approve`. Request body fields (both
optional): `account`, `plan` (default `enterprise-unlimited`).

Response: the entitlement record, containing:

- `name` — `providers/demo-provider/entitlements/<ent_id>`
- `account` — from request (default `providers/demo-provider/accounts/acc-001`)
- `plan`, `state` (`ENTITLEMENT_ACTIVE`), `usageReportingId` (`usage-<ent_id>`)
- `jwt` — RS256 JWT minted by the sim. Header: `alg RS256`, `typ JWT`,
  `kid <KEY_ID>`. Claims: `iss` (the x509 metadata URL), `sub`
  (`account-default`), `aud` (`demo-provider`), `entitlement_id`, `exp` (now+86400).
- `createTime`, `updateTime`
- `pubsubEnvelope` — a push-notification envelope with `subscription`
  (`projects/demo-provider/subscriptions/gcp-marketplace-entitlements`) and
  `message`: `data` (base64 JSON with `eventId`, `eventType`
  `ENTITLEMENT_ACTIVE`, `providerId`, `entitlement: {id, updateTime}`),
  `messageId`, `publishTime`.

### Service Control :check — POST

Any path containing `:check`. Request body is ignored. Response:
`checkErrors` (empty, or one `{code: "RESOURCE_EXHAUSTED", detail: ...}` when
the `default` bucket is at 0) and `serviceConfigId` (`2026-10-04r1`).

### Service Control :allocateQuota — POST

Any path containing `:allocateQuota`. Request fields: `allocateOperation` with
`operationId` and `quotaMetrics` (list of `{metricValues: [{int64Value}]}`).
The requested amount is the sum of `int64Value` values plus 1.

Response: `allocateErrors` (empty, or `RESOURCE_EXHAUSTED` if the bucket
cannot cover the request), `serviceConfigId`, and `operationId` echoed from
the request. On success the bucket is debited.

### Service Control :report — POST

Any path containing `:report`. Request fields: `operations` — list of
`{operationId, consumerId, metricValueSets: [{metricValues: [{int64Value}]}]}`.
Each operation becomes a record appended to `USAGE_REPORTS`:
`operationId`, `consumerId`, `int64Value` (summed units), `recordedAt`,
`revenueEarnedUsd` (units times price, 4 decimals).

Response: `serviceConfigId`, `reportErrors` (always empty), `serviceRolloutId`
(`rollout-aaif-001`), `admittedCount`.

## Error envelope

Unknown paths return `{"error": {"code": 404, "message": ...}}` with HTTP 404;
the message distinguishes `Method not found` (GET fallback) from
`Path not found: <path>` (POST fallback). Malformed JSON bodies are silently
treated as `{}`.

## Honesty section — what is NOT faithful

- **Single key, not a rotating set.** Real Google serves multiple x509 certs;
  the sim serves one key generated at process start.
- **In-memory state.** `ACCOUNTS`, `ENTITLEMENTS`, `USAGE_REPORTS`, and
  `QUOTA_BUCKETS` reset on restart; quota is a single `default` bucket of
  10,000 units with a fixed `requested = 1 + sum` rule.
- **No push subscription.** `pubsubEnvelope` is embedded in the approve
  response; nothing is delivered to a subscriber endpoint.
- **JWT minted by the sim, verified by the client.** The sim signs with its
  own key; `entitlement.py` `decide()` now cryptographically verifies that
  JWT (RS256 + x509 `kid` lookup + `iss`/`aud`/`exp`) before honoring an
  entitlement. `:check` still does not validate any caller JWT or OAuth
  token, and the `/oauth2/v4/token` endpoint still returns a static-shape
  token without credential checking.
- Requests are matched by substring/`endswith` on the raw path, not by the
  real resource-path grammar.
