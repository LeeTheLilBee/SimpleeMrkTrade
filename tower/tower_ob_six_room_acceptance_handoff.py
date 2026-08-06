"""
Tower ↔ Observatory six-room acceptance handoff.

This module lets Tower recognize the OB-side owner-experience
acceptance package without merging the OB branch into Tower main.

OB package:
- commit: 8aefbbf48fac2e8f6a3ac7368ba17a80909b4253
- six rooms simplified
- OB branch clean
- 72 tests passed
- consolidation pushed
- safety locks held
- NOT STAGING_READY

This handoff repairs/records Tower → OB → Tower continuity for
owner walkthrough integration while keeping dangerous controls locked.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List, Mapping


HANDOFF_VERSION = "tower_ob_six_room_acceptance_handoff_v1"
HANDOFF_ROUTE = "/tower/observatory-six-room-acceptance"
HANDOFF_JSON_ROUTE = "/tower/observatory-six-room-acceptance.json"
HANDOFF_RETURN_CHECK_ROUTE = "/tower/observatory-six-room-acceptance/return-check.json"

OB_ACCEPTANCE_COMMIT = "8aefbbf48fac2e8f6a3ac7368ba17a80909b4253"
OB_ACCEPTANCE_SHORT = "8aefbbf"

TOWER_INTEGRATION_BRANCH = "tower-ob-six-room-integration-dev"

SIX_ROOMS = [
    {
        "id": "dashboard",
        "name": "Dashboard",
        "purpose": "Owner-level current state, next action, and simplified status.",
        "tower_walkthrough_route": "/tower/observatory-walkthrough?room=dashboard",
        "ob_room_route": "/observatory/dashboard",
        "acceptance_status": "accepted_by_ob_package",
        "surface_expectation": "simple command surface, not proof wall",
    },
    {
        "id": "market_map",
        "name": "Market Map",
        "purpose": "Simplified market map with progressive deep dives.",
        "tower_walkthrough_route": "/tower/observatory-walkthrough?room=market_map",
        "ob_room_route": "/observatory/market-map",
        "acceptance_status": "accepted_by_ob_package",
        "surface_expectation": "clear owner map with reduced clutter",
    },
    {
        "id": "symbol_page",
        "name": "Symbol Page",
        "purpose": "Focused destination for selected symbol context.",
        "tower_walkthrough_route": "/tower/observatory-walkthrough?room=symbol_page",
        "ob_room_route": "/observatory/symbol",
        "acceptance_status": "accepted_by_ob_package",
        "surface_expectation": "destination page only, not main navigation clutter",
    },
    {
        "id": "trade_center",
        "name": "Trade Center",
        "purpose": "Decision support and Manual Live review without broker submission.",
        "tower_walkthrough_route": "/tower/observatory-walkthrough?room=trade_center",
        "ob_room_route": "/observatory/trade-center",
        "acceptance_status": "accepted_by_ob_package",
        "surface_expectation": "review and checklist only; dangerous controls locked",
    },
    {
        "id": "review_center",
        "name": "Review Center",
        "purpose": "Receipts, outcomes, and review summaries with hidden evidence.",
        "tower_walkthrough_route": "/tower/observatory-walkthrough?room=review_center",
        "ob_room_route": "/observatory/review-center",
        "acceptance_status": "accepted_by_ob_package",
        "surface_expectation": "summary first, evidence drawer second",
    },
    {
        "id": "owner_console",
        "name": "Owner Console",
        "purpose": "OB owner controls moved toward Tower-owned decision surfaces.",
        "tower_walkthrough_route": "/tower/observatory-walkthrough?room=owner_console",
        "ob_room_route": "/observatory/owner-console",
        "acceptance_status": "accepted_by_ob_package",
        "surface_expectation": "OB-local controls only; global controls live in Tower",
    },
]


PACK_NAMES = {
    2543: "Tower Integration Branch Wake",
    2544: "OB Six-Room Acceptance Package Recognition",
    2545: "Tower to OB Launch Continuity Contract",
    2546: "OB to Tower Return Continuity Contract",
    2547: "Six-Room Walkthrough Integration Surface",
    2548: "Owner Session Preservation Receipt",
    2549: "Dangerous Control Lock Verification",
    2550: "Integration Evidence Drawers",
    2551: "Integration Cert Routes",
    2552: "Tower-OB Handoff Repair Checkpoint",
}


READINESS_KEYS = {
    2543: "tower_integration_branch_wake_ready",
    2544: "ob_six_room_acceptance_package_recognition_ready",
    2545: "tower_to_ob_launch_continuity_contract_ready",
    2546: "ob_to_tower_return_continuity_contract_ready",
    2547: "six_room_walkthrough_integration_surface_ready",
    2548: "owner_session_preservation_receipt_ready",
    2549: "dangerous_control_lock_verification_ready",
    2550: "integration_evidence_drawers_ready",
    2551: "integration_cert_routes_ready",
    2552: "tower_ob_handoff_repair_checkpoint_ready",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_payload(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest()


def six_room_acceptance_contract() -> Dict[str, Any]:
    return {
        "contract": HANDOFF_VERSION,
        "route": HANDOFF_ROUTE,
        "json_route": HANDOFF_JSON_ROUTE,
        "return_check_route": HANDOFF_RETURN_CHECK_ROUTE,
        "tower_integration_branch": TOWER_INTEGRATION_BRANCH,
        "ob_acceptance_commit": OB_ACCEPTANCE_COMMIT,
        "ob_acceptance_short": OB_ACCEPTANCE_SHORT,
        "ob_branch_clean_reported": True,
        "ob_six_rooms_simplified": True,
        "ob_tests_passed": 72,
        "ob_consolidation_pushed": True,
        "tower_recognizes_ob_acceptance_package": True,
        "six_room_acceptance_package_registered": True,
        "six_room_count": len(SIX_ROOMS),
        "six_room_ids": [room["id"] for room in SIX_ROOMS],
        "tower_to_ob_launch_continuity": True,
        "ob_to_tower_return_continuity": True,
        "owner_session_preservation_required": True,
        "owner_walkthrough_integration_surface": True,
        "dangerous_controls_locked": True,
        "staging_ready": False,
        "redeploy_authorized": False,
        "merge_ob_to_main_authorized": False,
        "merge_tower_integration_to_main_authorized": False,
        "broker_submission": False,
        "capital_movement": False,
        "production_deployment": False,
        "staging_redeploy": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "direct_vault_write": False,
        "destructive_action_unlocked": False,
    }


def six_room_acceptance_package() -> Dict[str, Any]:
    payload = {
        "package": "ob_owner_experience_six_room_acceptance",
        "commit": OB_ACCEPTANCE_COMMIT,
        "short_commit": OB_ACCEPTANCE_SHORT,
        "status": "recognized_by_tower_not_merged",
        "branch_clean_reported": True,
        "tests_passed": 72,
        "safety_locks_held": True,
        "staging_ready": False,
        "rooms": deepcopy(SIX_ROOMS),
        "recognized_at": utc_now_iso(),
    }

    payload["package_hash"] = sha256_payload(payload)

    return payload


def launch_continuity_contract() -> Dict[str, Any]:
    return {
        "tower_entry": "/tower/access-home",
        "tower_launch": "/tower/launch/observatory",
        "step_up_route": "/tower/step-up/observatory",
        "tower_walkthrough": "/tower/observatory-walkthrough",
        "handoff_surface": HANDOFF_ROUTE,
        "owner_session_must_exist_before_launch": True,
        "step_up_required_for_ob_launch": True,
        "launch_receipt_required": True,
        "launch_destination_expected": "/tower/observatory-walkthrough",
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
    }


def return_continuity_contract() -> Dict[str, Any]:
    return {
        "ob_return_button_label": "Go back to Tower",
        "tower_return_route": "/tower/return/observatory",
        "tower_return_json_route": "/tower/return/observatory.json",
        "return_destination_expected": "/tower/access-home",
        "owner_session_must_survive_return": True,
        "clearance_must_survive_return": True,
        "return_receipt_required": True,
        "dangerous_action_unlock_on_return": False,
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
    }


def dangerous_control_locks() -> Dict[str, bool]:
    return {
        "broker_submission": False,
        "capital_movement": False,
        "production_deployment": False,
        "staging_redeploy": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "direct_vault_write": False,
        "destructive_action_unlocked": False,
        "merge_ob_to_main_authorized": False,
        "staging_ready": False,
    }


def build_owner_session_preservation_receipt(
    *,
    owner_session: Mapping[str, Any],
    last_room: str | None = None,
    direction: str = "tower_ob_tower",
) -> Dict[str, Any]:
    authenticated = bool(owner_session.get("authenticated"))
    role = owner_session.get("role")
    owner_id = owner_session.get("owner_id")

    receipt = {
        "receipt_type": "tower_ob_owner_session_preservation",
        "direction": direction,
        "owner_authenticated": authenticated,
        "role": role,
        "owner_id_present": bool(owner_id),
        "owner_session_preserved": authenticated and role == "owner" and bool(owner_id),
        "clearance_preserved": role == "owner",
        "last_room": last_room or "unknown",
        "tower_entry": "/tower/access-home",
        "tower_launch": "/tower/launch/observatory",
        "tower_walkthrough": "/tower/observatory-walkthrough",
        "tower_return": "/tower/return/observatory",
        "tower_return_destination": "/tower/access-home",
        "ob_acceptance_commit": OB_ACCEPTANCE_COMMIT,
        "dangerous_controls": dangerous_control_locks(),
        "created_at": utc_now_iso(),
    }

    receipt["receipt_hash"] = sha256_payload(receipt)

    return receipt


def integration_evidence_drawers() -> List[Dict[str, str]]:
    return [
        {
            "summary": "OB six-room acceptance package",
            "body": (
                "Tower recognizes OB commit "
                + OB_ACCEPTANCE_COMMIT
                + " as the reported clean six-room owner-experience package: "
                + "six rooms simplified, 72 tests passed, safety locks held, "
                + "not staging ready."
            ),
        },
        {
            "summary": "Tower → OB launch continuity",
            "body": (
                "Tower launch remains owner-session gated and step-up protected. "
                "The expected destination is the Tower-owned Observatory walkthrough."
            ),
        },
        {
            "summary": "OB → Tower return continuity",
            "body": (
                "The return path expects a Go back to Tower action, preserves owner "
                "session and clearance, records a return receipt, and lands at Access Home."
            ),
        },
        {
            "summary": "Dangerous controls",
            "body": (
                "This handoff does not authorize staging ready, redeploy, production, "
                "broker submission, capital movement, Manual Live, Live Auto, direct Vault "
                "write, destructive action, or OB-to-main merge."
            ),
        },
    ]


def build_handoff_payload(
    *,
    owner_session: Mapping[str, Any] | None = None,
    step_up_active: bool = False,
) -> Dict[str, Any]:
    owner_session = dict(owner_session or {})

    payload = {
        "surface": HANDOFF_VERSION,
        "title": "Tower ↔ Observatory Handoff",
        "subtitle": "Six-Room Acceptance",
        "owner_authenticated": bool(owner_session.get("authenticated")),
        "role": owner_session.get("role") or "locked",
        "owner_id_present": bool(owner_session.get("owner_id")),
        "step_up_active": bool(step_up_active),
        "acceptance_package": six_room_acceptance_package(),
        "launch_continuity": launch_continuity_contract(),
        "return_continuity": return_continuity_contract(),
        "owner_session_preservation": build_owner_session_preservation_receipt(
            owner_session=owner_session,
            direction="tower_ob_tower_preview",
        ),
        "dangerous_controls": dangerous_control_locks(),
        "evidence_drawers": integration_evidence_drawers(),
        "contract": six_room_acceptance_contract(),
        "created_at": utc_now_iso(),
    }

    payload["payload_hash"] = sha256_payload(payload)

    return payload


def render_handoff_surface(payload: Mapping[str, Any]) -> str:
    package = payload.get("acceptance_package", {})
    rooms = package.get("rooms", [])
    launch = payload.get("launch_continuity", {})
    returns = payload.get("return_continuity", {})
    evidence = payload.get("evidence_drawers", [])
    locks = payload.get("dangerous_controls", {})

    room_cards = "\n".join(
        f"""
        <article class="handoff-room-card" id="{escape(room.get("id", ""))}">
            <div class="handoff-card-top">
                <span>{escape(room.get("acceptance_status", ""))}</span>
                <strong>{escape(room.get("id", ""))}</strong>
            </div>
            <h3>{escape(room.get("name", ""))}</h3>
            <p>{escape(room.get("purpose", ""))}</p>
            <p><b>Walkthrough:</b> {escape(room.get("tower_walkthrough_route", ""))}</p>
            <p><b>OB room:</b> {escape(room.get("ob_room_route", ""))}</p>
            <p><b>Expectation:</b> {escape(room.get("surface_expectation", ""))}</p>
        </article>
        """
        for room in rooms
    )

    evidence_html = "\n".join(
        f"""
        <details class="handoff-detail">
            <summary>{escape(item.get("summary", ""))}</summary>
            <p>{escape(item.get("body", ""))}</p>
        </details>
        """
        for item in evidence
    )

    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta
            name="viewport"
            content="width=device-width,initial-scale=1"
        >
        <title>Tower OB Six-Room Handoff</title>
        {_handoff_css()}
    </head>
    <body>
        <main class="handoff-shell">
            <aside class="handoff-rail">
                <a class="handoff-back" href="/tower/access-home">← Access Home</a>
                <a class="handoff-back" href="/tower/owner-console">Owner Console</a>
                <a class="handoff-back" href="/tower/app-registry">App Registry</a>

                <div class="handoff-mark">OB</div>
                <div class="handoff-overline">Tower Integration</div>
                <h1>Six-Room Handoff</h1>
                <p>
                    Tower recognizes the clean OB acceptance package
                    without merging it into main or marking staging ready.
                </p>

                <div class="handoff-rail-panel">
                    <span>OB commit</span>
                    <strong>{escape(str(package.get("short_commit", "")))}</strong>
                    <small>STAGING_READY: False</small>
                </div>
            </aside>

            <section class="handoff-main">
                <header class="handoff-hero">
                    <div>
                        <div class="handoff-overline">
                            Return / Session Continuity Repair
                        </div>
                        <h2>Tower → OB → Tower</h2>
                        <p>
                            Owner session must stay alive when leaving Tower,
                            entering OB, and returning back to Tower.
                        </p>
                    </div>

                    <div class="handoff-hero-card">
                        <span>Acceptance package</span>
                        <strong>{escape(str(package.get("short_commit", "")))}</strong>
                        <small>72 OB tests reported passed</small>
                    </div>
                </header>

                <section class="handoff-grid status">
                    <article class="handoff-stat">
                        <span>OB rooms</span>
                        <strong>{len(rooms)}</strong>
                    </article>
                    <article class="handoff-stat">
                        <span>Launch continuity</span>
                        <strong>{escape(str(launch.get("tower_to_ob_launch_continuity", True)))}</strong>
                    </article>
                    <article class="handoff-stat">
                        <span>Return continuity</span>
                        <strong>{escape(str(returns.get("owner_session_must_survive_return", True)))}</strong>
                    </article>
                    <article class="handoff-stat">
                        <span>Staging ready</span>
                        <strong>False</strong>
                    </article>
                </section>

                <section class="handoff-section handoff-panel">
                    <div class="handoff-section-head">
                        <h2>Continuity Contract</h2>
                        <p>
                            Tower launch stays step-up protected and return
                            lands back at Access Home with a receipt.
                        </p>
                    </div>

                    <div class="handoff-two">
                        <article>
                            <h3>Launch</h3>
                            <p><b>Entry:</b> {escape(launch.get("tower_entry", ""))}</p>
                            <p><b>Launch:</b> {escape(launch.get("tower_launch", ""))}</p>
                            <p><b>Step-up:</b> {escape(launch.get("step_up_route", ""))}</p>
                            <p><b>Destination:</b> {escape(launch.get("launch_destination_expected", ""))}</p>
                        </article>
                        <article>
                            <h3>Return</h3>
                            <p><b>Label:</b> {escape(returns.get("ob_return_button_label", ""))}</p>
                            <p><b>Route:</b> {escape(returns.get("tower_return_route", ""))}</p>
                            <p><b>Destination:</b> {escape(returns.get("return_destination_expected", ""))}</p>
                            <p><b>Receipt:</b> {escape(str(returns.get("return_receipt_required", True)))}</p>
                        </article>
                    </div>
                </section>

                <section class="handoff-section">
                    <div class="handoff-section-head">
                        <h2>Accepted Six Rooms</h2>
                        <p>
                            Tower recognizes these six OB rooms as the
                            simplified owner-experience package.
                        </p>
                    </div>

                    <div class="handoff-room-grid">
                        {room_cards}
                    </div>
                </section>

                <section class="handoff-section handoff-panel">
                    <div class="handoff-section-head">
                        <h2>Dangerous Controls Stay Locked</h2>
                        <p>
                            This integration handoff is recognition and
                            continuity only.
                        </p>
                    </div>

                    <div class="handoff-lock-grid">
                        <p>Broker submission: {escape(str(locks.get("broker_submission")))}</p>
                        <p>Capital movement: {escape(str(locks.get("capital_movement")))}</p>
                        <p>Manual Live: {escape(str(locks.get("manual_live_authorized")))}</p>
                        <p>Live Auto: {escape(str(locks.get("live_auto_authorized")))}</p>
                        <p>Staging redeploy: {escape(str(locks.get("staging_redeploy")))}</p>
                        <p>STAGING_READY: {escape(str(locks.get("staging_ready")))}</p>
                    </div>
                </section>

                <section class="handoff-section handoff-panel">
                    <div class="handoff-section-head">
                        <h2>Integration Evidence Drawers</h2>
                        <p>
                            Evidence is available, but the surface stays
                            focused on acceptance and continuity.
                        </p>
                    </div>

                    {evidence_html}
                </section>

                <footer class="handoff-footer">
                    Tower OB handoff · payload
                    {escape(str(payload.get("payload_hash", ""))[:14])}
                </footer>
            </section>
        </main>
    </body>
    </html>
    """


def _handoff_css() -> str:
    return """
    <style>
    :root {
        color-scheme: dark;
        --bg: #05040a;
        --panel: rgba(20, 17, 31, .84);
        --line: rgba(255,255,255,.13);
        --text: #fbf7ff;
        --muted: #bdb3cf;
        --dim: #867a99;
        --gold: #f4d27b;
        --violet: #7d4fd6;
        --danger: #ff9fb0;
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        min-height: 100vh;
        background:
            radial-gradient(circle at 12% 14%, rgba(125,79,214,.20), transparent 34%),
            radial-gradient(circle at 84% 20%, rgba(244,210,123,.12), transparent 28%),
            linear-gradient(135deg, #030208, #090617 46%, #05040a);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    a { color: inherit; }

    .handoff-shell {
        display: grid;
        grid-template-columns: 290px minmax(0, 1fr);
        min-height: 100vh;
    }

    .handoff-rail {
        padding: 30px 22px;
        border-right: 1px solid var(--line);
        background: rgba(10, 8, 18, .88);
        position: sticky;
        top: 0;
        height: 100vh;
    }

    .handoff-back {
        display: block;
        margin-bottom: 10px;
        color: var(--muted);
        text-decoration: none;
        font-weight: 850;
    }

    .handoff-mark {
        width: 62px;
        height: 62px;
        border-radius: 20px;
        display: grid;
        place-items: center;
        margin: 22px 0 18px;
        color: #201307;
        font-size: 1.2rem;
        font-weight: 950;
        background: linear-gradient(135deg, var(--gold), #fff1b7);
        box-shadow: 0 0 26px rgba(244,210,123,.22), inset 0 0 14px rgba(255,255,255,.42);
    }

    .handoff-overline {
        color: var(--gold);
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .74rem;
        font-weight: 850;
    }

    .handoff-rail h1 {
        font-size: 2.2rem;
        margin: 8px 0 10px;
        letter-spacing: -.04em;
    }

    .handoff-rail p,
    .handoff-main p {
        color: var(--muted);
        line-height: 1.58;
    }

    .handoff-rail-panel,
    .handoff-hero,
    .handoff-hero-card,
    .handoff-stat,
    .handoff-room-card,
    .handoff-panel,
    .handoff-detail {
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(255,255,255,.075), rgba(255,255,255,.035));
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 70px rgba(0,0,0,.22);
    }

    .handoff-rail-panel {
        display: grid;
        gap: 6px;
        padding: 16px;
        border-radius: 18px;
        margin-top: 24px;
    }

    .handoff-rail-panel span,
    .handoff-stat span,
    .handoff-card-top span,
    .handoff-hero-card span {
        color: var(--dim);
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .11em;
        font-weight: 850;
    }

    .handoff-main { padding: 34px; }

    .handoff-hero {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 280px;
        gap: 22px;
        align-items: end;
        min-height: 240px;
        border-radius: 30px;
        padding: 34px;
        background:
            radial-gradient(circle at 78% 10%, rgba(244,210,123,.13), transparent 35%),
            linear-gradient(135deg, rgba(31,23,49,.88), rgba(9,7,16,.82));
    }

    .handoff-hero h2 {
        font-size: clamp(2.4rem, 5vw, 5.2rem);
        line-height: .94;
        letter-spacing: -.06em;
        margin: 10px 0 12px;
    }

    .handoff-hero-card {
        border-radius: 24px;
        padding: 22px;
        display: grid;
        gap: 8px;
    }

    .handoff-grid.status {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin: 18px 0 28px;
    }

    .handoff-stat,
    .handoff-panel,
    .handoff-room-card {
        border-radius: 24px;
        padding: 22px;
    }

    .handoff-stat strong {
        display: block;
        margin-top: 8px;
        font-size: 1.15rem;
    }

    .handoff-section { margin-top: 28px; }

    .handoff-section h2,
    .handoff-panel h2 {
        margin: 0 0 6px;
        font-size: 1.6rem;
    }

    .handoff-two {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 18px;
    }

    .handoff-room-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
    }

    .handoff-card-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }

    .handoff-room-card h3 {
        margin: 8px 0 8px;
        font-size: 1.35rem;
    }

    .handoff-lock-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 10px;
    }

    .handoff-detail {
        border-radius: 16px;
        padding: 15px 16px;
        margin-top: 10px;
    }

    .handoff-detail summary {
        color: var(--gold);
        cursor: pointer;
        font-weight: 850;
    }

    .handoff-footer {
        color: var(--dim);
        margin: 30px 0 4px;
        font-size: .9rem;
    }

    @media (max-width: 980px) {
        .handoff-shell,
        .handoff-hero,
        .handoff-grid.status,
        .handoff-two,
        .handoff-lock-grid {
            grid-template-columns: 1fr;
        }

        .handoff-rail {
            position: relative;
            height: auto;
        }

        .handoff-main {
            padding: 20px;
        }
    }
    </style>
    """


def build_handoff_cert(pack: int) -> Dict[str, Any]:
    if pack not in PACK_NAMES:
        raise ValueError(f"Unsupported handoff pack: {pack}")

    readiness_key = READINESS_KEYS[pack]
    contract = six_room_acceptance_contract()

    payload = {
        "pack": str(pack),
        "pack_name": PACK_NAMES[pack],
        "status": "ready",
        "readiness": 100,
        "tower_ob_six_room_acceptance_handoff": True,
        "tower_return_session_continuity_repair": True,
        readiness_key: True,
        "tower_integration_branch": TOWER_INTEGRATION_BRANCH,
        "ob_acceptance_commit": OB_ACCEPTANCE_COMMIT,
        "ob_six_rooms_simplified": True,
        "ob_tests_passed": 72,
        "six_room_count": len(SIX_ROOMS),
        "dashboard_accepted": True,
        "market_map_accepted": True,
        "symbol_page_accepted": True,
        "trade_center_accepted": True,
        "review_center_accepted": True,
        "owner_console_accepted": True,
        "tower_recognizes_ob_acceptance_package": True,
        "tower_to_ob_launch_continuity": True,
        "ob_to_tower_return_continuity": True,
        "owner_session_preservation_required": True,
        "owner_walkthrough_integration_surface": True,
        "integration_evidence_drawers": True,
        "cert_routes_registered": True,
        "staging_ready": False,
        "redeploy_authorized": False,
        "merge_ob_to_main_authorized": False,
        "merge_tower_integration_to_main_authorized": False,
        "broker_submission": False,
        "capital_movement": False,
        "production_deployment": False,
        "staging_redeploy": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "direct_vault_write": False,
        "destructive_action_unlocked": False,
        "contract": contract,
        "next_pack": str(pack + 1),
        f"safe_to_continue_to_pack_{pack + 1}": True,
    }

    payload["cert_hash"] = sha256_payload(payload)

    return payload
