"""OCEL v2 Emitter.

Serializes agent swarm execution traces and GCP Marketplace events to:
1. Standard JSON-OCEL (.json)
2. Relational SQLite OCEL v2 (.sqlite) compatible with PM4Py `read_ocel2_sqlite`.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ggen_marketplace.ocel2.models import OCEL2Log, OCELEvent, OCELObject


class OCEL2Emitter:
    """Emits multi-object event logs adhering to the IEEE OCEL v2.0 specification."""

    OBJECT_TYPES = [
        "CustomerAccount",
        "GcpEntitlement",
        "SwarmCoordinator",
        "A2AExecutionTask",
        "McpToolCall",
        "ServiceControlReport",
    ]

    EVENT_TYPES = [
        "GCP_ENTITLEMENT_REQUESTED",
        "GCP_ENTITLEMENT_ACTIVATED",
        "AAIF_SWARM_BOOTSTRAPPED",
        "A2A_TASK_DELEGATED",
        "MCP_TOOL_INVOKED",
        "SPARQL_GATE_EVALUATED",
        "GCP_METERING_REPORTED",
    ]

    def __init__(self) -> None:
        self.log = OCEL2Log(
            object_types=list(self.OBJECT_TYPES),
            event_types=list(self.EVENT_TYPES),
        )

    def register_object(self, obj_id: str, obj_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Register a domain object in the OCEL v2 model."""
        if obj_type not in self.log.object_types:
            self.log.object_types.append(obj_type)
        self.log.objects.append(
            OCELObject(id=obj_id, type=obj_type, attributes=attributes or {})
        )

    def emit_event(
        self,
        event_id: str,
        event_type: str,
        timestamp: datetime,
        attributes: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Emit a multi-object event with relationships."""
        if event_type not in self.log.event_types:
            self.log.event_types.append(event_type)

        rels = []
        if relationships:
            for r in relationships:
                rels.append({
                    "objectId": r["objectId"],
                    "qualifier": r.get("qualifier", "related"),
                })

        self.log.events.append(
            OCELEvent(
                id=event_id,
                type=event_type,
                time=timestamp,
                attributes=attributes or {},
                relationships=rels,
            )
        )

    def write_json(self, output_path: Path) -> Path:
        """Serialize log to standard JSON-OCEL file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.log.to_json_dict(), f, indent=2)
        return output_path

    def write_sqlite(self, db_path: Path) -> Path:
        """Serialize log to relational SQLite OCEL v2 database via PM4Py."""
        import pm4py
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if db_path.exists():
            db_path.unlink()

        temp_json = db_path.with_suffix(".temp.json")
        self.write_json(temp_json)
        try:
            ocel = pm4py.read_ocel2_json(str(temp_json))
            pm4py.write_ocel2_sqlite(ocel, str(db_path))
        finally:
            if temp_json.exists():
                temp_json.unlink()
        return db_path
