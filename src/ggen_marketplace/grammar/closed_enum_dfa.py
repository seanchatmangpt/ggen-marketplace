"""Closed-Enum Regular Language Lexical DFA Parser (LangSec).

Eliminates arbitrary stringly-typed payloads on the wire by enforcing that JSON
messages consist exclusively of pre-declared keys and finite closed enum variants.
Operates as a Deterministic Finite Automaton (DFA) in O(n) time.
"""
from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, Set


class WireLexerError(Exception):
    """Raised when an unapproved token or free-form string is encountered on the wire."""
    pass


class ActionIntent(str, Enum):
    INTENT_QUERY_RECORD = "INTENT_QUERY_RECORD"
    INTENT_CALCULATE_METRIC = "INTENT_CALCULATE_METRIC"
    INTENT_DISPATCH_TASK = "INTENT_DISPATCH_TASK"
    INTENT_SETTLE_PAYMENT = "INTENT_SETTLE_PAYMENT"


class CallerRole(str, Enum):
    ROLE_LEAD_ANALYST = "ROLE_LEAD_ANALYST"
    ROLE_AUDITOR = "ROLE_AUDITOR"
    ROLE_SETTLEMENT_OFFICER = "ROLE_SETTLEMENT_OFFICER"


class ResourceTarget(str, Enum):
    TARGET_DATASET_01 = "TARGET_DATASET_01"
    TARGET_LEDGER_PRIMARY = "TARGET_LEDGER_PRIMARY"
    TARGET_ROUTER_MESH = "TARGET_ROUTER_MESH"


class ClosedEnumWireDFA:
    """Deterministic Finite Automaton verifying that input payloads contain only closed sum types."""

    ALLOWED_KEYS: Set[str] = {"action_intent", "caller_role", "resource_target", "pqc_suite", "payload_hash"}

    ENUM_SCHEMAS: Dict[str, Set[str]] = {
        "action_intent": {v.value for v in ActionIntent},
        "caller_role": {v.value for v in CallerRole},
        "resource_target": {v.value for v in ResourceTarget},
        "pqc_suite": {"ML_DSA_65", "ML_DSA_87", "ML_KEM_768"},
    }

    @classmethod
    def parse_and_validate(cls, raw_json_bytes: bytes) -> Dict[str, str]:
        """Validates payload against regular closed-enum grammar. Rejects arbitrary strings fail-closed."""
        try:
            # Enforce UTF-8 strictly
            text = raw_json_bytes.decode("utf-8")
            data = json.loads(text)
        except Exception as exc:
            raise WireLexerError(f"DFA_LEXICAL_REJECT: Malformed JSON syntax: {exc}") from exc

        if not isinstance(data, dict):
            raise WireLexerError("DFA_LEXICAL_REJECT: Payload must be a flat dictionary")

        validated: Dict[str, str] = {}

        for k, v in data.items():
            if k not in cls.ALLOWED_KEYS:
                raise WireLexerError(f"DFA_UNREPRESENTABLE_KEY: Disallowed key '{k}' on wire")

            if not isinstance(v, str):
                raise WireLexerError(f"DFA_TYPE_REJECT: Field '{k}' value must be a static token string")

            # Check if this field is a closed enum
            if k in cls.ENUM_SCHEMAS:
                allowed_variants = cls.ENUM_SCHEMAS[k]
                if v not in allowed_variants:
                    raise WireLexerError(
                        f"DFA_NON_ENUM_PAYLOAD: Value '{v}' is not an admitted variant of {k}. Allowed: {sorted(allowed_variants)}"
                    )
            elif k == "payload_hash":
                # Fixed 64-char hex string (SHA-256)
                if len(v) != 64 or not all(c in "0123456789abcdefABCDEF" for c in v):
                    raise WireLexerError("DFA_FORMAT_REJECT: payload_hash must be exactly 64 hex characters")

            validated[k] = v

        return validated
