"""pm4pytest.ocel

High-performance event and multi-object trace collector adhering to the IEEE OCEL v2 standard.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class OCELObject:
    """An object instance in OCEL v2."""
    id: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCELEvent:
    """An event instance in OCEL v2 with multi-object relationships."""
    id: str
    type: str
    time: datetime
    attributes: Dict[str, Any] = field(default_factory=dict)
    relationships: List[Dict[str, str]] = field(default_factory=list)


class ProcessTraceCollector:
    """Collects multi-object events during a test run and exports to JSON/SQLite OCEL v2."""

    def __init__(self) -> None:
        self.objects: List[OCELObject] = []
        self.events: List[OCELEvent] = []
        self.object_types: set[str] = set()
        self.event_types: set[str] = set()

    def register_object(self, obj_id: str, obj_type: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Register an entity object."""
        self.object_types.add(obj_type)
        self.objects.append(OCELObject(id=obj_id, type=obj_type, attributes=attributes or {}))

    def emit_event(
        self,
        event_id: str,
        event_type: str,
        timestamp: Optional[datetime] = None,
        attributes: Optional[Dict[str, Any]] = None,
        relationships: Optional[List[Dict[str, str]]] = None,
    ) -> None:
        """Emit a multi-object event with relationships."""
        self.event_types.add(event_type)
        t = timestamp or datetime.now(timezone.utc)
        rels = []
        if relationships:
            for r in relationships:
                rels.append({
                    "objectId": r["objectId"],
                    "qualifier": r.get("qualifier", "related"),
                })
        self.events.append(
            OCELEvent(
                id=event_id,
                type=event_type,
                time=t,
                attributes=attributes or {},
                relationships=rels,
            )
        )

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to standard JSON-OCEL format."""
        def _sanitize_val(val: Any) -> Any:
            if isinstance(val, (list, dict)):
                import json
                return json.dumps(val)
            return val

        return {
            "objectTypes": [{"name": ot} for ot in sorted(self.object_types)],
            "eventTypes": [{"name": et} for et in sorted(self.event_types)],
            "objects": [
                {
                    "id": obj.id,
                    "type": obj.type,
                    "attributes": [
                        {"name": k, "value": _sanitize_val(v), "time": "1970-01-01T00:00:00Z"}
                        for k, v in obj.attributes.items()
                    ],
                }
                for obj in self.objects
            ],
            "events": [
                {
                    "id": ev.id,
                    "type": ev.type,
                    "time": ev.time.isoformat(),
                    "attributes": [
                        {"name": k, "value": _sanitize_val(v)}
                        for k, v in ev.attributes.items()
                    ],
                    "relationships": ev.relationships,
                }
                for ev in self.events
            ],
        }

    def write_sqlite(self, db_path: Path) -> Path:
        """Write relational SQLite OCEL v2 using PM4Py."""
        import pm4py
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if db_path.exists():
            db_path.unlink()

        temp_json = db_path.with_suffix(".temp.json")
        with open(temp_json, "w", encoding="utf-8") as f:
            json.dump(self.to_json_dict(), f, indent=2)

        try:
            ocel = pm4py.read_ocel2_json(str(temp_json))
            pm4py.write_ocel2_sqlite(ocel, str(db_path))
        finally:
            if temp_json.exists():
                temp_json.unlink()
        return db_path
