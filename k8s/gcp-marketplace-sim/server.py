import base64
import json
import time
import os
import hashlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from cryptography.x509.oid import NameOID
import datetime

# 1. Cryptographic Identity Setup: Real RS256 CA and Keypair
PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
PUBLIC_KEY = PRIVATE_KEY.public_key()

subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Google LLC"),
    x509.NameAttribute(NameOID.COMMON_NAME, "cloud-commerce-partner@system.gserviceaccount.com"),
])

CERT = x509.CertificateBuilder().subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    PUBLIC_KEY
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.now(datetime.timezone.utc)
).not_valid_after(
    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
).sign(PRIVATE_KEY, hashes.SHA256())

CERT_PEM = CERT.public_bytes(serialization.Encoding.PEM).decode('utf-8')
KEY_ID = hashlib.sha1(CERT.public_bytes(serialization.Encoding.DER)).hexdigest()

ACCOUNTS = {}
ENTITLEMENTS = {}
USAGE_REPORTS = []
QUOTA_BUCKETS = {"default": 10000}  # 10,000 units
PRICING_PER_METRIC_UNIT = 0.05

def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def create_google_jwt(claims: dict) -> str:
    header = {"alg": "RS256", "typ": "JWT", "kid": KEY_ID}
    header_b64 = b64url_encode(json.dumps(header).encode('utf-8'))
    claims_b64 = b64url_encode(json.dumps(claims).encode('utf-8'))
    signing_input = f"{header_b64}.{claims_b64}".encode('utf-8')
    sig = PRIVATE_KEY.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return f"{header_b64}.{claims_b64}.{b64url_encode(sig)}"

class ProductionGradeGCPHandler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Server', 'ESF')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # 1. Official Google Robot x509 Key Metadata Endpoint
        if parsed.path.endswith('/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com'):
            return self._send_json(200, {KEY_ID: CERT_PEM})

        # 2. Dynamic Discovery Documents
        elif 'cloudcommerceprocurement' in parsed.path and '$discovery/rest' in parsed.path:
            with open('/app/procurement_discovery.json') as f:
                return self._send_json(200, json.load(f))
        elif 'servicecontrol' in parsed.path and '$discovery/rest' in parsed.path:
            with open('/app/servicecontrol_discovery.json') as f:
                return self._send_json(200, json.load(f))

        elif parsed.path == '/healthz':
            return self._send_json(200, {"status": "SERVING", "service": "cloudcommerceprocurement.googleapis.com"})

        # Billing summary & receipts
        elif parsed.path == '/v1/billing/summary':
            total_units = sum(r.get('int64Value', 0) for r in USAGE_REPORTS)
            return self._send_json(200, {
                "totalOperations": len(USAGE_REPORTS),
                "totalMeteredUnits": total_units,
                "remainingQuota": QUOTA_BUCKETS.get("default", 0),
                "unitPriceUsd": PRICING_PER_METRIC_UNIT,
                "totalRealizedRevenueUsd": round(total_units * PRICING_PER_METRIC_UNIT, 2),
                "accounts": ACCOUNTS,
                "entitlements": ENTITLEMENTS,
                "recentReports": USAGE_REPORTS[-10:]
            })
        elif '/entitlements' in parsed.path:
            ent_id = parsed.path.split('/')[-1].split('?')[0]
            ent = ENTITLEMENTS.get(ent_id)
            if ent:
                return self._send_json(200, ent)
            return self._send_json(404, {"error": {"code": 404, "message": f"Entitlement {ent_id} not found"}})

        self._send_json(404, {"error": {"code": 404, "message": "Method not found"}})

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        try:
            data = json.loads(body.decode('utf-8'))
        except Exception:
            data = {}

        # OAuth2 token exchange
        if parsed.path in ['/oauth2/v4/token', '/token']:
            return self._send_json(200, {
                "access_token": f"ya29.c.aaif-sim-{int(time.time())}",
                "expires_in": 3600,
                "token_type": "Bearer"
            })

        # Signup / Account Approval
        elif '/accounts/' in parsed.path and parsed.path.endswith(':approve'):
            parts = parsed.path.split('/')
            acc_id = parts[parts.index('accounts') + 1].split(':')[0]
            ACCOUNTS[acc_id] = {
                "name": f"providers/demo-provider/accounts/{acc_id}",
                "state": "ACCOUNT_ACTIVE",
                "createTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "approvalTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            return self._send_json(200, ACCOUNTS[acc_id])

        # Entitlement Approval with Authentic Signed RS256 JWT & Pub/Sub payload
        elif '/entitlements/' in parsed.path and parsed.path.endswith(':approve'):
            parts = parsed.path.split('/')
            ent_id = parts[parts.index('entitlements') + 1].split(':')[0]
            jwt_token = create_google_jwt({
                "iss": "https://www.googleapis.com/robot/v1/metadata/x509/cloud-commerce-partner@system.gserviceaccount.com",
                "sub": f"account-{acc_id if 'acc_id' in locals() else 'default'}",
                "aud": "demo-provider",
                "entitlement_id": ent_id,
                "exp": int(time.time()) + 86400
            })

            ent_record = {
                "name": f"providers/demo-provider/entitlements/{ent_id}",
                "account": data.get("account", "providers/demo-provider/accounts/acc-001"),
                "plan": data.get("plan", "enterprise-unlimited"),
                "state": "ENTITLEMENT_ACTIVE",
                "usageReportingId": f"usage-{ent_id}",
                "jwt": jwt_token,
                "createTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "updateTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            ENTITLEMENTS[ent_id] = ent_record

            # Emit wrapped Pub/Sub push notification envelope
            pubsub_message = {
                "eventId": f"event-{int(time.time()*1000)}",
                "eventType": "ENTITLEMENT_ACTIVE",
                "providerId": "demo-provider",
                "entitlement": {"id": ent_id, "updateTime": ent_record["updateTime"]}
            }
            raw_data = json.dumps(pubsub_message).encode('utf-8')
            ent_record["pubsubEnvelope"] = {
                "message": {
                    "data": base64.b64encode(raw_data).decode('utf-8'),
                    "messageId": f"msg-{int(time.time()*1000)}",
                    "publishTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                },
                "subscription": "projects/demo-provider/subscriptions/gcp-marketplace-entitlements"
            }
            return self._send_json(200, ent_record)

        # Service Control: check
        elif ':check' in parsed.path:
            if QUOTA_BUCKETS.get("default", 0) <= 0:
                return self._send_json(200, {
                    "checkErrors": [{"code": "RESOURCE_EXHAUSTED", "detail": "Quota exceeded for service"}],
                    "serviceConfigId": "2026-10-04r1"
                })
            return self._send_json(200, {"checkErrors": [], "serviceConfigId": "2026-10-04r1"})

        # Service Control: allocateQuota
        elif ':allocateQuota' in parsed.path:
            requested = 1
            op = data.get("allocateOperation", {})
            for mvs in op.get("quotaMetrics", []):
                for mv in mvs.get("metricValues", []):
                    requested += mv.get("int64Value", 1)
            
            current = QUOTA_BUCKETS.get("default", 0)
            if current < requested:
                return self._send_json(200, {
                    "allocateErrors": [{"code": "RESOURCE_EXHAUSTED", "detail": "Insufficient quota"}],
                    "serviceConfigId": "2026-10-04r1"
                })
            QUOTA_BUCKETS["default"] -= requested
            return self._send_json(200, {
                "allocateErrors": [],
                "serviceConfigId": "2026-10-04r1",
                "operationId": op.get("operationId")
            })

        # Service Control: report
        elif ':report' in parsed.path:
            operations = data.get("operations", [])
            admitted_ops = []
            for op in operations:
                op_id = op.get("operationId")
                consumer_id = op.get("consumerId")
                units = 0
                for mvs in op.get("metricValueSets", []):
                    for mv in mvs.get("metricValues", []):
                        units += mv.get("int64Value", 1)
                
                record = {
                    "operationId": op_id,
                    "consumerId": consumer_id,
                    "int64Value": units,
                    "recordedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "revenueEarnedUsd": round(units * PRICING_PER_METRIC_UNIT, 4)
                }
                USAGE_REPORTS.append(record)
                admitted_ops.append(record)

            return self._send_json(200, {
                "serviceConfigId": "2026-10-04r1",
                "reportErrors": [],
                "serviceRolloutId": "rollout-aaif-001",
                "admittedCount": len(admitted_ops)
            })

        self._send_json(404, {"error": {"code": 404, "message": f"Path not found: {parsed.path}"}})

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8443), ProductionGradeGCPHandler)
    print("Wire-Indistinguishable GCP Marketplace Server running on :8443")
    server.serve_forever()
