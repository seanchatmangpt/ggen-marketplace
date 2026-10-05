#!/usr/bin/env python3
"""Monetization registry: per-solution commerce configuration, from monetization.toml.

Mirrors scripts/marketplace_lifecycle.py exactly: root-level TOML registry,
pure functions, stdlib only (tomllib), an absent file is empty defaults and
never an error. Refusals carry typed `REFUSED:<CODE>:<detail>` codes.

Billing-authority vocabulary is the same 9-authority set as
packs/chatman-marketplace-commerce-dod-pack/gates/definition_of_done.py
(KNOWN_AUTHORITIES) — duplicated here deliberately to keep this module
stdlib-pure and dependency-free; if that tuple changes, change it here too.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, Mapping

REGISTRY_RELATIVE = "monetization.toml"
SCHEMA_VERSION = "1.0.0"

BACKENDS = ("sim", "real")
# KNOWN_AUTHORITIES from packs/chatman-marketplace-commerce-dod-pack/gates/definition_of_done.py
KNOWN_AUTHORITIES = (
    "AWS_MARKETPLACE", "MICROSOFT_MARKETPLACE", "GOOGLE_CLOUD_MARKETPLACE",
    "ORACLE_MARKETPLACE", "IBM_MARKETPLACE", "SAP_MARKETPLACE",
    "SALESFORCE_APPEXCHANGE", "DIRECT_STRIPE", "GENERIC_MARKETPLACE",
)
ENTRY_KEYS = frozenset({"backend", "billing_authorities", "provider_id", "unit_price_usd", "plan"})

DEFAULTS: dict[str, Any] = {
    "backend": "sim",
    "billing_authorities": ["GOOGLE_CLOUD_MARKETPLACE"],
    "provider_id": "demo-provider",
    "unit_price_usd": 0.05,
    "plan": None,
}


def _refused(code: str, detail: Any) -> str:
    return f"REFUSED:{code}:{detail}"


def load(root: Path) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """(config, problems). Missing file -> ({}, []). Problems are `REFUSED:<CODE>:<detail>`."""
    path = root / REGISTRY_RELATIVE
    if not path.is_file():
        return {}, []
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        return {}, [_refused("REFUSED_MONETIZATION_TOML_INVALID", exc)]

    problems: list[str] = []
    if document.get("schema_version") != SCHEMA_VERSION:
        problems.append(
            _refused(
                "REFUSED_MONETIZATION_SCHEMA_VERSION",
                f"{document.get('schema_version')!r}!={SCHEMA_VERSION}",
            )
        )
    for table_key in ("monetization", "solutions"):
        value = document.get(table_key)
        if value is not None and not isinstance(value, dict):
            problems.append(_refused("REFUSED_MONETIZATION_TOML_INVALID", f"[{table_key}] must be a table"))

    config: dict[str, dict[str, Any]] = {}
    default_table = document.get("monetization", {})
    if isinstance(default_table, dict):
        config["_defaults"] = default_table
    solutions = document.get("solutions", {})
    if isinstance(solutions, dict):
        for slug, entry in solutions.items():
            if isinstance(entry, dict):
                config[slug] = entry
            else:
                problems.append(_refused("REFUSED_MONETIZATION_TOML_INVALID", f"[solutions.{slug}] must be a table"))
    return config, problems


def _effective(config: Mapping[str, Mapping[str, Any]], slug: str | None) -> dict[str, Any]:
    """Defaults overlaid by [solutions.<slug>] (full solution mapping, `plan` included)."""
    effective = dict(DEFAULTS)
    if slug is not None and slug in config:
        effective.update(config[slug])
    else:
        effective.update(config.get("_defaults", {}))
    return effective


def entry_issues(
    config: Mapping[str, Mapping[str, Any]],
    known_solutions: Mapping[str, Any] | None = None,
    refuse: Any = _refused,
) -> list[str]:
    """Refusals for unknown keys, unknown authorities, cardinality, backend, and price.

    `known_solutions` optionally maps solution slugs to anything; when given, registry
    slugs outside it are refused. Omit it to validate only structure.
    """
    issues: list[str] = []
    slugs = [k for k in config if k != "_defaults"]
    if known_solutions is not None:
        for slug in sorted(slugs):
            if slug not in known_solutions:
                issues.append(refuse("REFUSED_MONETIZATION_SOLUTION_UNKNOWN", slug))
    for slug in sorted(slugs):
        entry = config[slug]
        for key in sorted(set(entry) - ENTRY_KEYS):
            issues.append(refuse("REFUSED_MONETIZATION_UNKNOWN_KEY", f"{slug}:{key}"))

        merged = dict(DEFAULTS)
        merged.update(entry)

        authorities = merged["billing_authorities"]
        if (
            not isinstance(authorities, list)
            or not authorities
            or not all(isinstance(a, str) and a.strip() for a in authorities)
        ):
            issues.append(refuse("REFUSED_MONETIZATION_AUTHORITY_CARDINALITY", f"{slug}:billing_authorities"))
            authorities = []
        else:
            for authority in authorities:
                if authority not in KNOWN_AUTHORITIES:
                    issues.append(refuse("REFUSED_MONETIZATION_AUTHORITY_UNKNOWN", f"{slug}:{authority}"))
            if len(authorities) != 1:
                issues.append(
                    refuse("REFUSED_MONETIZATION_AUTHORITY_CARDINALITY", f"{slug}:len={len(authorities)}!=1")
                )

        backend = merged["backend"]
        if backend not in BACKENDS:
            issues.append(refuse("REFUSED_MONETIZATION_BACKEND_UNKNOWN", f"{slug}:{backend!r}"))

        price = merged["unit_price_usd"]
        if not isinstance(price, (int, float)) or isinstance(price, bool) or price <= 0:
            issues.append(refuse("REFUSED_MONETIZATION_PRICE_INVALID", f"{slug}:{price!r}"))

        provider_id = merged["provider_id"]
        if not isinstance(provider_id, str) or not provider_id.strip():
            issues.append(refuse("REFUSED_MONETIZATION_PROVIDER_ID_INVALID", f"{slug}:{provider_id!r}"))

        plan = merged.get("plan")
        if plan is not None and not (isinstance(plan, str) and plan.strip()):
            issues.append(refuse("REFUSED_MONETIZATION_PLAN_INVALID", f"{slug}:{plan!r}"))
    return issues


def effective_for(config: Mapping[str, Mapping[str, Any]], slug: str | None) -> dict[str, Any]:
    """Public accessor: defaults overlaid by the solution's own table (or root defaults)."""
    return _effective(config, slug)
