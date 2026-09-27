"""GRD004: pure reference maintenance-intake and lifecycle domain contract.

This module does NOT authenticate users, grant roles, persist records, notify
residents, upload files, or authorize real property work. The role argument is
descriptive only. A future entrypoint must first verify Tower claims and scope,
enforce tenant/unit and staff/assignment restrictions, and write an audit receipt.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

WORK_ORDER_STATES = (
    "submitted", "received", "under_review", "scheduled", "assigned",
    "in_progress", "waiting", "completed", "confirmation", "closed", "reopened",
)
ENTRY_PERMISSIONS = frozenset({"yes", "no", "contact_first"})
TRANSITIONS = {
    ("submitted", "received"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("received", "under_review"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("under_review", "scheduled"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("scheduled", "assigned"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("assigned", "in_progress"): frozenset({"maintenance_technician"}),
    ("in_progress", "waiting"): frozenset({"maintenance_technician"}),
    ("waiting", "in_progress"): frozenset({"maintenance_technician"}),
    ("waiting", "scheduled"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("in_progress", "completed"): frozenset({"maintenance_technician"}),
    ("completed", "confirmation"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("confirmation", "closed"): frozenset({"property_manager", "maintenance_supervisor"}),
    ("confirmation", "reopened"): frozenset({"resident", "property_manager", "maintenance_supervisor"}),
    ("closed", "reopened"): frozenset({"resident", "property_manager", "maintenance_supervisor"}),
    ("reopened", "under_review"): frozenset({"property_manager", "maintenance_supervisor"}),
}

def _required(value: str, label: str, *, max_length: int = 128) -> str:
    if (not isinstance(value, str) or not value.strip()
        or len(value.strip()) > max_length or "\x00" in value):
        raise ValueError(f"{label} missing, invalid or too long")
    return value.strip()

@dataclass(frozen=True)
class MaintenanceIntake:
    property_ref: str
    unit_ref: str
    category: str
    description: str
    emergency_flag: bool
    entry_permission: str
    photo_refs: tuple[str, ...] = ()

    def __post_init__(self):
        _required(self.property_ref,"property_ref",max_length=128)
        _required(self.unit_ref,"unit_ref",max_length=128)
        _required(self.category,"category",max_length=80)
        _required(self.description,"description",max_length=2000)
        if type(self.emergency_flag) is not bool:
            raise ValueError("emergency_flag must be boolean")
        if not isinstance(self.entry_permission,str) or self.entry_permission not in ENTRY_PERMISSIONS:
            raise ValueError("invalid entry_permission")
        if (not isinstance(self.photo_refs,tuple) or len(self.photo_refs)>8
            or any(not isinstance(ref,str) or not ref.strip()
                   or len(ref.strip())>128 or "\x00" in ref for ref in self.photo_refs)):
            raise ValueError("photo_refs must be at most eight bounded opaque references")
        # An emergency flag is an intake alert, never an emergency response guarantee.

@dataclass(frozen=True)
class WorkOrder:
    work_order_ref: str
    intake: MaintenanceIntake
    state: str = "submitted"

    def __post_init__(self):
        _required(self.work_order_ref, "work_order_ref")
        if not isinstance(self.intake, MaintenanceIntake):
            raise ValueError("intake required")
        if self.state not in WORK_ORDER_STATES:
            raise ValueError("invalid work order state")

def transition_work_order(work_order: WorkOrder, *, next_state: str, actor_role: str) -> WorkOrder:
    """Pure transition model. Never substitute for Tower-scoped authorization."""
    if not isinstance(work_order, WorkOrder):
        raise ValueError("work order required")
    allowed = TRANSITIONS.get((work_order.state, next_state), frozenset())
    if actor_role not in allowed:
        raise ValueError("work order transition prohibited")
    return replace(work_order, state=next_state)
