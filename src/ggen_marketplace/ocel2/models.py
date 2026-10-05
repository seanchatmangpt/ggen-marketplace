"""OCEL v2 Models & Schemas.

Implements the IEEE OCEL v2 standard relational entities for AAIF swarms and GCP Marketplace:
- Object Types: CustomerAccount, GcpEntitlement, SwarmCoordinator, A2AExecutionTask, McpToolCall, ServiceControlReport
- Event Types: GCP_ENTITLEMENT_REQUESTED, GCP_ENTITLEMENT_ACTIVATED, AAIF_SWARM_BOOTSTRAPPED,
               A2A_TASK_DELEGATED, MCP_TOOL_INVOKED, SPARQL_GATE_EVALUATED, GCP_METERING_REPORTED
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    # relationships entries: {"objectId": str, "qualifier": str}


@dataclass
class OCEL2Log:
    """Container for an IEEE OCEL v2 event log."""
    object_types: List[str] = field(default_factory=list)
    event_types: List[str] = field(default_factory=list)
    objects: List[OCELObject] = field(default_factory=list)
    events: List[OCELEvent] = field(default_factory=list)

    def to_json_dict(self) -> Dict[str, Any]:
        """Convert to standard JSON-OCEL format."""
        return {
            "objectTypes": [{"name": ot} for ot in self.object_types],
            "eventTypes": [{"name": et} for et in self.event_types],
            "objects": [
                {
                    "id": obj.id,
                    "type": obj.type,
                    "attributes": [
                        {"name": k, "value": v, "time": "1970-01-01T00:00:00Z"}
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
                        {"name": k, "value": v}
                        for k, v in ev.attributes.items()
                    ],
                    "relationships": ev.relationships,
                }
                for ev in self.events
            ],
        }
