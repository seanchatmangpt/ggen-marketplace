"""Deterministic CS2 projection collection."""
from project import projection, replay_receipt


class ProjectionRegistry:
    def __init__(self, subject):
        self.subject = subject
        self.items = {}

    def construct(self, kind, payload):
        item = projection(self.subject, kind, payload)
        self.items[item["projection_digest"]] = item
        return item

    def values(self):
        return [self.items[key] for key in sorted(self.items)]

    def receipt(self):
        return replay_receipt(self.subject, self.values())


def batch_construct(subject, specs):
    registry = ProjectionRegistry(subject)
    normalized = sorted(specs, key=lambda value: str(value.get("kind", "")))
    for spec in normalized:
        kind = str(spec.get("kind", "")).strip()
        payload = spec.get("payload", {})
        if not kind:
            raise ValueError("MISSING_PROJECTION_KIND")
        if type(payload) is not dict:
            raise ValueError("INVALID_PROJECTION_PAYLOAD")
        registry.construct(kind, payload)
    return registry.values(), registry.receipt()
