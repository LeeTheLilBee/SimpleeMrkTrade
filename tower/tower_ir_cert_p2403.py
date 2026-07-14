"""
SEARCHABLE LABEL: TOWER_PACK_2403_RISK_LOCKDOWN_INTERRUPT

Pack 2403 — Risk and Lockdown Interrupt Gate
"""

from __future__ import annotations

from copy import deepcopy
from functools import lru_cache
from typing import Any, Dict


PACK_ID = "2403"
ENDPOINT = "/tower/ir-cert-v2403.json"


def evaluate_runtime_interrupt(
    *,
    original_risk_state: str,
    current_risk_state: str,
    original_lockdown_state: str,
    current_lockdown_state: str,
    account_active: bool,
    identity_still_verified: bool,
) -> Dict[str, Any]:
    triggers = []

    if not identity_still_verified:
        triggers.append("ob_identity_no_longer_verified")

    if not account_active:
        triggers.append("tower_account_not_active")

    if current_risk_state != "acceptable":
        triggers.append("ob_risk_gate_denied")

    if (
        original_risk_state != current_risk_state
        and current_risk_state != "acceptable"
    ):
        triggers.append("ob_runtime_risk_state_changed")

    if current_lockdown_state == "active":
        triggers.append("ob_lockdown_active")

    if original_lockdown_state != current_lockdown_state:
        if current_lockdown_state == "active":
            triggers.append("tower_lockdown_activated")

    interrupted = bool(triggers)

    return {
        "allowed": not interrupted,
        "interrupted": interrupted,
        "reason_code": (
            triggers[0]
            if interrupted
            else "ob_runtime_interrupt_gate_clear"
        ),
        "trigger_codes": triggers,
        "required_action": (
            "emergency_lockback"
            if interrupted
            else "continue_protected_session"
        ),
        "default_deny_on_interrupt": True,
        "preview_only": True,
        "writes_state": False,
    }


@lru_cache(maxsize=1)
def _build_cached() -> Dict[str, Any]:
    return {
        "pack": PACK_ID,
        "pack_name": "Risk and Lockdown Interrupt Gate",
        "status": "ready",
        "readiness": 100,
        "endpoint": ENDPOINT,
        "monitored_conditions": [
            "identity_verified",
            "account_active",
            "risk_state",
            "lockdown_state",
        ],
        "interrupt_requires_lockback": True,
        "default_deny_on_interrupt": True,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
        "next_pack": "2404",
        "safe_to_continue_to_pack_2404": True,
    }


def build_ir_cert_p2403_preview() -> Dict[str, Any]:
    return deepcopy(_build_cached())


def prepare_pack_2404_ir_cert_p2404() -> Dict[str, Any]:
    return {
        "ready": True,
        "source_pack": PACK_ID,
        "next_pack": "2404",
        "name": "Protected Session Drift Detector",
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }
