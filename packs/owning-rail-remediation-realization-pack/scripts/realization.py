from dataclasses import dataclass

@dataclass(frozen=True)
class Realization:
    blocker_before: int
    blocker_after: int
    post_state: str

    def classify(self) -> str:
        if self.post_state in {"FAIL", "BUILD_BROKEN"}:
            return "BUILD_BROKEN"
        if self.blocker_after > self.blocker_before:
            return "REGRESSED"
        if self.blocker_after == 0 and self.post_state == "PASS":
            return "REALIZED"
        if self.blocker_after < self.blocker_before:
            return "UNREALIZED"
        return "UNKNOWN"
