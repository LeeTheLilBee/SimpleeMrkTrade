"""Canonical Tower-owned ecosystem destination registry.

Clouds may recommend where the owner should go. Tower owns every protected
crossing. The receiving application retains authority after entry.

Connection states are deliberately truthful:
- open: a current Tower launch adapter exists.
- summary_only: Tower can expose a narrow safe read surface, not an operational room.
- contract_ready: destination metadata exists, but the receiving runtime is not connected.
"""

from __future__ import annotations

import re
from copy import deepcopy
from urllib.parse import urlencode


CONTRACT_VERSION = "tower-ecosystem-destination-v1"

RUNTIME_OPEN = "open"
RUNTIME_SUMMARY_ONLY = "summary_only"
RUNTIME_CONTRACT_READY = "contract_ready"

_SYMBOL_RE = re.compile(r"^[A-Z][A-Z0-9.\-]{0,11}$")


APP_REGISTRY = {
    "tower": {
        "label": "The Tower",
        "runtime_state": RUNTIME_OPEN,
        "feed_state": "internal_authority",
        "default_destination": "access_home",
        "requires_owner_permission": True,
        "requires_step_up": False,
        "return_supported": True,
        "destinations": {
            "access_home": {
                "label": "Access Home",
                "target_route": "/tower/access-home",
                "item_mode": "none",
            },
        },
    },
    "clouds": {
        "label": "The Clouds",
        "runtime_state": RUNTIME_OPEN,
        "feed_state": "internal_owner_command",
        "default_destination": "owner_command",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "return_supported": True,
        "destinations": {
            "owner_command": {
                "label": "Owner Command",
                "target_route": "/clouds",
                "item_mode": "optional",
            },
        },
    },
    "observatory": {
        "label": "The Observatory",
        "runtime_state": RUNTIME_OPEN,
        "feed_state": "projection_reference",
        "default_destination": "dashboard",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "return_supported": True,
        "destinations": {
            "dashboard": {
                "label": "Dashboard",
                "target_route": "/ob/dashboard",
                "room_id": "ob_room_dashboard",
                "item_mode": "none",
            },
            "market_map": {
                "label": "Market Map",
                "target_route": "/ob/market-map",
                "room_id": "ob_room_market_map",
                "item_mode": "none",
            },
            "symbol": {
                "label": "Symbol Page",
                "target_route": "/ob/symbol/{item}",
                "room_id": "ob_room_symbol_page",
                "item_mode": "symbol",
            },
            "trade_center": {
                "label": "Trade Center",
                "target_route": "/ob/trade-center",
                "room_id": "ob_room_trade_center",
                "item_mode": "optional",
            },
            "review_center": {
                "label": "Review Center",
                "target_route": "/ob/review-center",
                "room_id": "ob_room_review_center",
                "item_mode": "optional",
            },
            "owner_console": {
                "label": "Owner Console",
                "target_route": "/ob/owner-console",
                "room_id": "ob_room_owner_console",
                "item_mode": "optional",
            },
        },
    },
    "archive_vault": {
        "label": "Archive Vault",
        "runtime_state": RUNTIME_SUMMARY_ONLY,
        "feed_state": "projection_reference",
        "default_destination": "status_bridge",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "return_supported": True,
        "destinations": {
            "status_bridge": {
                "label": "Vault Status Bridge",
                "target_route": "/vault/headless-tower-status-bridge-layer.json",
                "item_mode": "none",
            },
            "owner_clearance": {
                "label": "Owner Clearance Status",
                "target_route": "/vault/tower-owner-clearance-status-bridge.json",
                "item_mode": "none",
            },
        },
    },
    "teller": {
        "label": "The Teller",
        "runtime_state": RUNTIME_CONTRACT_READY,
        "feed_state": "unavailable",
        "default_destination": "payroll_review",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "return_supported": True,
        "destinations": {
            "home": {"label": "Teller Home", "target_route": None, "item_mode": "none"},
            "payroll_review": {"label": "Payroll Review", "target_route": None, "item_mode": "optional"},
            "payment_review": {"label": "Payment Review", "target_route": None, "item_mode": "optional"},
            "records": {"label": "Records", "target_route": None, "item_mode": "optional"},
            "onboarding": {"label": "Onboarding", "target_route": None, "item_mode": "optional"},
        },
    },
    "grounds": {
        "label": "The Grounds",
        "runtime_state": RUNTIME_CONTRACT_READY,
        "feed_state": "unavailable",
        "default_destination": "portfolio",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "return_supported": True,
        "destinations": {
            "portfolio": {"label": "Property Portfolio", "target_route": None, "item_mode": "optional"},
            "tenant_home": {"label": "Tenant Home", "target_route": None, "item_mode": "optional"},
            "maintenance": {"label": "Maintenance", "target_route": None, "item_mode": "optional"},
            "acquisitions": {"label": "Acquisitions", "target_route": None, "item_mode": "optional"},
        },
    },
    "atm_operations": {
        "label": "ATM Operations",
        "runtime_state": RUNTIME_CONTRACT_READY,
        "feed_state": "unavailable",
        "default_destination": "operations",
        "requires_owner_permission": True,
        "requires_step_up": True,
        "return_supported": True,
        "destinations": {
            "operations": {"label": "Operations", "target_route": None, "item_mode": "optional"},
            "machines": {"label": "Machines", "target_route": None, "item_mode": "optional"},
            "routes": {"label": "Routes", "target_route": None, "item_mode": "optional"},
            "cash": {"label": "Cash / Vault Reserve", "target_route": None, "item_mode": "optional"},
        },
    },
}


ALIASES = {
    "ob": "observatory",
    "the_observatory": "observatory",
    "archive-vault": "archive_vault",
    "vault": "archive_vault",
    "the_teller": "teller",
    "the_grounds": "grounds",
    "atm": "atm_operations",
    "atm-operations": "atm_operations",
}


def normalize_app_id(value: str) -> str:
    key = str(value or "").strip().lower().replace(" ", "_")
    return ALIASES.get(key, key)


def get_app_contract(app_id: str) -> dict | None:
    app_id = normalize_app_id(app_id)
    raw = APP_REGISTRY.get(app_id)
    if raw is None:
        return None
    result = deepcopy(raw)
    result["app_id"] = app_id
    result["contract_version"] = CONTRACT_VERSION
    return result


def get_destination_contract(app_id: str, destination: str | None = None) -> dict | None:
    app = get_app_contract(app_id)
    if app is None:
        return None

    destination_id = str(destination or app["default_destination"]).strip().lower()
    raw = app["destinations"].get(destination_id)
    if raw is None:
        return None

    result = deepcopy(raw)
    result.update({
        "app_id": app["app_id"],
        "app_label": app["label"],
        "destination_id": destination_id,
        "runtime_state": app["runtime_state"],
        "requires_owner_permission": app["requires_owner_permission"],
        "requires_step_up": app["requires_step_up"],
        "return_supported": app["return_supported"],
        "contract_version": CONTRACT_VERSION,
    })
    return result


def _normalize_item(destination: dict, item: str | None) -> tuple[bool, str, str]:
    mode = destination.get("item_mode", "none")
    text = str(item or "").strip()

    if mode == "none":
        return True, "", "item_not_used"

    if mode == "optional":
        if len(text) > 120:
            return False, "", "item_too_long"
        return True, text, "item_optional"

    if mode == "symbol":
        symbol = text.upper()
        if not _SYMBOL_RE.fullmatch(symbol):
            return False, "", "symbol_item_invalid"
        return True, symbol, "symbol_item_valid"

    return False, "", "unknown_item_mode"


def validate_launch_intent(
    *,
    app_id: str,
    destination: str | None = None,
    item: str | None = None,
    return_context: str | None = None,
) -> dict:
    app = get_app_contract(app_id)
    if app is None:
        return {
            "valid": False,
            "reason_code": "ecosystem_app_unknown",
            "app_id": normalize_app_id(app_id),
        }

    dest = get_destination_contract(app["app_id"], destination)
    if dest is None:
        return {
            "valid": False,
            "reason_code": "ecosystem_destination_unknown",
            "app_id": app["app_id"],
            "destination": str(destination or ""),
        }

    item_ok, normalized_item, item_reason = _normalize_item(dest, item)
    if not item_ok:
        return {
            "valid": False,
            "reason_code": item_reason,
            "app_id": app["app_id"],
            "destination": dest["destination_id"],
        }

    context = str(return_context or "").strip()
    if len(context) > 160:
        return {
            "valid": False,
            "reason_code": "return_context_too_long",
            "app_id": app["app_id"],
            "destination": dest["destination_id"],
        }

    target_route = dest.get("target_route")
    if target_route and "{item}" in target_route:
        target_route = target_route.format(item=normalized_item)

    return {
        "valid": True,
        "reason_code": "ecosystem_launch_intent_valid",
        "app_id": app["app_id"],
        "app_label": app["label"],
        "destination": dest["destination_id"],
        "destination_label": dest["label"],
        "item": normalized_item,
        "return_context": context,
        "runtime_state": app["runtime_state"],
        "feed_state": app["feed_state"],
        "target_route": target_route,
        "room_id": dest.get("room_id"),
        "requires_owner_permission": app["requires_owner_permission"],
        "requires_step_up": app["requires_step_up"],
        "return_supported": app["return_supported"],
        "contract_version": CONTRACT_VERSION,
    }


def build_launch_reference(
    app_id: str,
    *,
    destination: str | None = None,
    item: str | None = None,
    return_context: str | None = None,
) -> str:
    app_id = normalize_app_id(app_id)
    query = {}
    if destination:
        query["destination"] = destination
    if item:
        query["item"] = item
    if return_context:
        query["return_context"] = return_context

    base = f"/tower/ecosystem/launch/{app_id}"
    return base + (("?" + urlencode(query)) if query else "")


def build_line_matrix() -> tuple[dict, ...]:
    rows = []
    for app_id, app in APP_REGISTRY.items():
        runtime_state = app["runtime_state"]

        rows.append({
            "app_id": app_id,
            "label": app["label"],
            "line_state": runtime_state,
            "feed_state": app["feed_state"],
            "launch_state": runtime_state,
            "deep_link_state": (
                "ready"
                if runtime_state == RUNTIME_OPEN
                else "not_operational"
            ),
            "return_state": (
                "ready"
                if app["return_supported"] and runtime_state == RUNTIME_OPEN
                else (
                    "contract_ready"
                    if app["return_supported"]
                    else "not_supported"
                )
            ),
            "default_destination": app["default_destination"],
            "launch_reference": build_launch_reference(
                app_id,
                destination=app["default_destination"],
                return_context=f"clouds-{app_id}",
            ),
            "requires_tower": app_id not in {"tower", "clouds"},
            "requires_owner_permission": app["requires_owner_permission"],
            "requires_step_up": app["requires_step_up"],
            "direct_clouds_bypass_allowed": False,
            "downstream_execution_performed": False,
        })

    return tuple(rows)
