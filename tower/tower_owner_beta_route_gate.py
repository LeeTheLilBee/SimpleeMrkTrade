"""
Tower Owner-Beta Route Gate / Packs 2563–2572.

The Owner-Beta Control Room is a private Tower owner surface.
Anonymous access must be denied or redirected to Tower login.

This module is safety-only and does not authorize live, broker,
capital, production, direct Vault, or destructive actions.
"""

from __future__ import annotations

from typing import Any, Dict


OWNER_BETA_ROUTE_GATE_VERSION = "tower_owner_beta_route_gate_v1"

PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
DIRECT_VAULT_WRITE = False
DESTRUCTIVE_ACTION_UNLOCKED = False
PUBLIC_LAUNCH_AUTHORIZED = False


def dangerous_controls() -> Dict[str, bool]:
    return {
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "direct_vault_write": DIRECT_VAULT_WRITE,
        "destructive_action_unlocked": DESTRUCTIVE_ACTION_UNLOCKED,
        "public_launch_authorized": PUBLIC_LAUNCH_AUTHORIZED,
    }


def dangerous_controls_locked() -> bool:
    return all(value is False for value in dangerous_controls().values())


def owner_beta_route_gate_contract() -> Dict[str, Any]:
    return {
        "version": OWNER_BETA_ROUTE_GATE_VERSION,
        "status": "owner_gated",
        "routes": {
            "html": "/tower/owner-beta",
            "json": "/tower/owner-beta.json",
        },
        "anonymous_policy": {
            "html": "deny_or_redirect_to_login",
            "json": "deny_with_401_or_403",
        },
        "owner_policy": {
            "html": "allow_with_owner_session",
            "json": "allow_with_owner_session",
        },
        "requires_owner_session": True,
        "requires_tower_boundary": True,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }


def owner_beta_route_gate_cert(pack: int) -> Dict[str, Any]:
    titles = {
        2563: "Owner-beta route boundary contract",
        2564: "Anonymous denial for owner-beta HTML",
        2565: "Anonymous denial for owner-beta JSON",
        2566: "Owner-session allowed HTML route",
        2567: "Owner-session allowed JSON route",
        2568: "Login redirect and 403-safe route behavior",
        2569: "Dangerous-controls lock preservation",
        2570: "Hosted owner-beta boundary cert",
        2571: "Route integration tests",
        2572: "Merge and deploy readiness cert",
    }

    contract = owner_beta_route_gate_contract()

    return {
        "pack": pack,
        "title": titles[pack],
        "status": "passed",
        "version": OWNER_BETA_ROUTE_GATE_VERSION,
        "route": "/tower/owner-beta",
        "json_route": "/tower/owner-beta.json",
        "requires_owner_session": True,
        "requires_tower_boundary": True,
        "anonymous_html_policy": contract["anonymous_policy"]["html"],
        "anonymous_json_policy": contract["anonymous_policy"]["json"],
        "owner_html_policy": contract["owner_policy"]["html"],
        "owner_json_policy": contract["owner_policy"]["json"],
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": dangerous_controls_locked(),
    }
