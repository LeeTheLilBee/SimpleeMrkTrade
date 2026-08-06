"""
Tower Access Home UI v2.

Simplee front door / owner control room surface.

This module is UI/presentation-focused. It does not unlock
dangerous actions, deployment, broker submission, live trading,
capital movement, or direct Vault writes.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List

from flask import render_template_string, request, session


TOWER_UI_V2_THEME = {
    "name": "Simplee Tower Black Glass",
    "primary": "obsidian_black",
    "secondary": "deep_royal_violet",
    "owner_accent": "soft_gold",
    "glass": True,
    "blue_minimized": True,
    "portal_glow_only_on_launch": True,
}


APP_CARDS = [
    {
        "id": "observatory",
        "name": "The Observatory",
        "subtitle": "Market intelligence and trading command",
        "status": "Owner access ready",
        "tone": "active",
        "href": "/tower/launch/observatory",
        "primary_action": "Open Observatory",
        "description": (
            "Enter the protected owner walkthrough, rooms, "
            "signals, review, and command surfaces."
        ),
        "requires_step_up": True,
    },
    {
        "id": "vault",
        "name": "Archive Vault",
        "subtitle": "Sealed memory and evidence",
        "status": "Locked / safe",
        "tone": "safe",
        "href": "#vault-preview",
        "primary_action": "View status",
        "description": (
            "Vault remains sealed. Requests and proofs route "
            "through Tower-controlled boundaries."
        ),
        "requires_step_up": False,
    },
    {
        "id": "teller",
        "name": "The Teller",
        "subtitle": "People, payroll, payments, and requests",
        "status": "Workflow planned",
        "tone": "planned",
        "href": "#teller-preview",
        "primary_action": "Preview",
        "description": (
            "Future desk for employee, vendor, payroll, "
            "payment, and request workflows."
        ),
        "requires_step_up": False,
    },
    {
        "id": "grounds",
        "name": "The Grounds",
        "subtitle": "Property operations and stewardship",
        "status": "Planned",
        "tone": "planned",
        "href": "#grounds-preview",
        "primary_action": "Preview",
        "description": (
            "Future real-estate command for units, vendors, "
            "leases, maintenance, taxes, and assets."
        ),
        "requires_step_up": False,
    },
    {
        "id": "clouds",
        "name": "The Clouds",
        "subtitle": "Executive owner summary layer",
        "status": "Command layer planned",
        "tone": "planned",
        "href": "#clouds-preview",
        "primary_action": "Preview",
        "description": (
            "Future owner summary surface across Tower, OB, "
            "Vault, Teller, Grounds, and business lanes."
        ),
        "requires_step_up": False,
    },
]


OWNER_ACTIONS = [
    {
        "label": "Review owner access",
        "status": "Available",
        "detail": "Inspect current owner session, role, and launch status.",
    },
    {
        "label": "Open Observatory",
        "status": "Step-up protected",
        "detail": "Tower verifies owner permission before opening OB.",
    },
    {
        "label": "Security check",
        "status": "Clean",
        "detail": "Anonymous and non-owner access remain denied.",
    },
]


EVIDENCE_DRAWERS = [
    {
        "summary": "Owner session evidence",
        "body": (
            "Shows owner role, owner id presence, session state, "
            "and step-up status. Kept collapsed by default."
        ),
    },
    {
        "summary": "Launch receipt evidence",
        "body": (
            "Shows whether Tower created an OB launch receipt. "
            "No broker submission, money movement, or live mode "
            "authorization is included."
        ),
    },
    {
        "summary": "Return receipt evidence",
        "body": (
            "Shows whether the owner returned from OB into Tower "
            "with session continuity preserved."
        ),
    },
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def canonical_json(payload: Dict[str, Any]) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def receipt_hash(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(
        canonical_json(payload).encode("utf-8")
    ).hexdigest()


def active_return_receipt() -> Dict[str, Any] | None:
    value = session.get(
        "tower_ob_return_receipt"
    )

    if isinstance(value, dict):
        return deepcopy(value)

    return None


def record_ob_return_receipt(
    *,
    source: str = "observatory",
    last_room: str | None = None,
) -> Dict[str, Any]:
    owner_id = session.get(
        "owner_id"
    )

    role = session.get(
        "tower_role"
    )

    receipt = {
        "receipt_type": "tower_ob_return",
        "source": source,
        "destination": "/tower/access-home",
        "owner_id": owner_id,
        "role": role,
        "owner_session_preserved": bool(owner_id and role == "owner"),
        "clearance_preserved": role == "owner",
        "last_room": last_room or "unknown",
        "returned_at": utc_now().isoformat(),
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "dangerous_action_unlocked": False,
    }

    receipt["receipt_hash"] = receipt_hash(receipt)

    session["tower_ob_return_receipt"] = receipt

    return deepcopy(receipt)


def owner_session_summary(
    *,
    step_up_active: bool,
) -> Dict[str, Any]:
    return {
        "authenticated": (
            session.get("tower_authenticated") is True
        ),
        "role": session.get("tower_role"),
        "owner_id_present": bool(session.get("owner_id")),
        "username": session.get("tower_username", "Owner"),
        "step_up_active": bool(step_up_active),
        "launch_receipt_present": bool(
            session.get("tower_ob_launch_receipt")
        ),
        "return_receipt_present": bool(
            session.get("tower_ob_return_receipt")
        ),
        "default_deny": True,
    }


def ui_v2_contract() -> Dict[str, Any]:
    return {
        "contract": "tower_access_home_ui_v2",
        "theme": deepcopy(TOWER_UI_V2_THEME),
        "clean_access_home": True,
        "app_launch_cards": True,
        "owner_session_status": True,
        "clear_tower_to_ob_launch": True,
        "clear_ob_to_tower_return": True,
        "return_receipt_status_panel": True,
        "owner_actions_panel": True,
        "quick_launch_panel": True,
        "hidden_evidence_drawers": True,
        "proof_page_main_experience": False,
        "list_heavy_main_surface": False,
        "credentials_committed": False,
        "broker_submission": False,
        "capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_write": False,
    }


def render_access_home_v2(
    *,
    step_up_active: bool,
    username: str,
) -> str:
    summary = owner_session_summary(
        step_up_active=step_up_active
    )

    return_receipt = active_return_receipt()

    step_status = (
        "Active"
        if summary["step_up_active"]
        else "Required before OB launch"
    )

    return_status = (
        "Returned from The Observatory. Owner session preserved."
        if return_receipt
        else "No active OB return yet."
    )

    return_room = (
        return_receipt.get("last_room", "unknown")
        if return_receipt
        else "—"
    )

    return_hash = (
        return_receipt.get("receipt_hash", "")[:14]
        if return_receipt
        else "Not created"
    )

    card_html = "\n".join(
        _render_app_card(card)
        for card in APP_CARDS
    )

    owner_action_html = "\n".join(
        f"""
        <div class="tower-action-row">
            <div>
                <strong>{escape(action["label"])}</strong>
                <p>{escape(action["detail"])}</p>
            </div>
            <span>{escape(action["status"])}</span>
        </div>
        """
        for action in OWNER_ACTIONS
    )

    evidence_html = "\n".join(
        f"""
        <details class="tower-detail">
            <summary>{escape(drawer["summary"])}</summary>
            <p>{escape(drawer["body"])}</p>
        </details>
        """
        for drawer in EVIDENCE_DRAWERS
    )

    page = f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <meta
            name="viewport"
            content="width=device-width,initial-scale=1"
        >
        <title>Tower Access Home</title>
        {_tower_css()}
    </head>
    <body>
        <main class="tower-shell">
            <aside class="tower-rail">
                <div class="tower-mark">T</div>
                <div>
                    <div class="tower-overline">
                        Simplee Tower
                    </div>
                    <h2>Control Room</h2>
                </div>

                <nav class="tower-nav">
                    <a href="/tower/access-home">Access Home</a>
                    <a href="/tower/launch/observatory">Observatory</a>
                    <a href="#owner-actions">Owner Actions</a>
                    <a href="#evidence-drawers">Evidence</a>
                    <a href="/tower/logout">Logout</a>
                </nav>

                <div class="tower-rail-card">
                    <span>Owner clearance</span>
                    <strong>{escape(str(summary["role"] or "locked"))}</strong>
                </div>
            </aside>

            <section class="tower-main">
                <header class="tower-hero">
                    <div>
                        <div class="tower-overline">
                            Tower Access Command Center
                        </div>
                        <h1>Welcome back, {escape(username)}.</h1>
                        <p>
                            Choose the door you need. Tower keeps
                            identity, permission, step-up, and
                            evidence behind the scenes.
                        </p>
                    </div>

                    <div class="tower-session-card">
                        <span>Owner session</span>
                        <strong>
                            {"Verified" if summary["authenticated"] else "Locked"}
                        </strong>
                        <small>Step-up: {escape(step_status)}</small>
                    </div>
                </header>

                <section class="tower-status-grid">
                    <div class="tower-status-tile">
                        <span>Access</span>
                        <strong>Owner</strong>
                    </div>
                    <div class="tower-status-tile">
                        <span>Security</span>
                        <strong>Default deny</strong>
                    </div>
                    <div class="tower-status-tile">
                        <span>OB launch</span>
                        <strong>
                            {"Receipt ready" if summary["launch_receipt_present"] else "Ready"}
                        </strong>
                    </div>
                    <div class="tower-status-tile">
                        <span>Return</span>
                        <strong>
                            {"Preserved" if return_receipt else "Waiting"}
                        </strong>
                    </div>
                </section>

                <span class="tower-sr-only">Open The Observatory</span>

                <section class="tower-section">
                    <div class="tower-section-head">
                        <div>
                            <h2>Access Hub</h2>
                            <p>
                                These are the main doors into Simplee.
                                Each card shows what opens now and
                                what stays protected.
                            </p>
                        </div>
                    </div>

                    <div class="tower-app-grid">
                        {card_html}
                    </div>
                </section>

                <section class="tower-lower-grid">
                    <article class="tower-panel tower-return-panel">
                        <div class="tower-panel-head">
                            <span>Return status</span>
                            <strong>OB → Tower</strong>
                        </div>
                        <h3>{escape(return_status)}</h3>
                        <p>
                            Last room: {escape(str(return_room))}
                        </p>
                        <p>
                            Receipt: {escape(return_hash)}
                        </p>
                    </article>

                    <article
                        id="owner-actions"
                        class="tower-panel"
                    >
                        <div class="tower-panel-head">
                            <span>Owner Actions</span>
                            <strong>Protected</strong>
                        </div>
                        {owner_action_html}
                    </article>

                    <article class="tower-panel">
                        <div class="tower-panel-head">
                            <span>Quick Launch</span>
                            <strong>Doors</strong>
                        </div>
                        <div class="tower-quick-actions">
                            <a
                                class="tower-button"
                                href="/tower/launch/observatory"
                            >
                                Open OB
                            </a>
                            <a
                                class="tower-button secondary"
                                href="/tower/auth/status.json"
                            >
                                Auth status
                            </a>
                            <a
                                class="tower-button secondary"
                                href="/tower/return/observatory"
                            >
                                Simulate return
                            </a>
                        </div>
                    </article>
                </section>

                <section
                    id="evidence-drawers"
                    class="tower-section tower-evidence"
                >
                    <div class="tower-section-head">
                        <div>
                            <h2>Evidence drawers</h2>
                            <p>
                                Proof stays available, but it no
                                longer dominates the owner experience.
                            </p>
                        </div>
                    </div>

                    {evidence_html}
                </section>

                <footer class="tower-footer">
                    Tower Access Command Center · © Simplee
                </footer>
            </section>
        </main>
    </body>
    </html>
    """

    return render_template_string(page)


def _render_app_card(card: Dict[str, Any]) -> str:
    classes = (
        "tower-app-card tower-app-card-active"
        if card["id"] == "observatory"
        else "tower-app-card"
    )

    step_label = (
        "<span>Step-up protected</span>"
        if card.get("requires_step_up")
        else "<span>View only / planned</span>"
    )

    return f"""
    <article
        id="{escape(card["id"])}-preview"
        class="{classes}"
    >
        <div class="tower-card-top">
            <span>{escape(card["status"])}</span>
            {step_label}
        </div>

        <h3>{escape(card["name"])}</h3>
        <p class="tower-card-subtitle">
            {escape(card["subtitle"])}
        </p>
        <p>{escape(card["description"])}</p>

        <a
            class="tower-button"
            href="{escape(card["href"])}"
        >
            {escape(card["primary_action"])}
        </a>
    </article>
    """


def _tower_css() -> str:
    return """
    <style>
    :root {
        color-scheme: dark;
        --bg: #05040a;
        --panel: rgba(20, 17, 31, .84);
        --panel-2: rgba(37, 26, 58, .74);
        --glass: rgba(255,255,255,.07);
        --line: rgba(255,255,255,.13);
        --text: #fbf7ff;
        --muted: #bdb3cf;
        --dim: #867a99;
        --violet: #7d4fd6;
        --violet-2: #24153f;
        --gold: #f4d27b;
        --gold-2: #a67c2b;
        --danger: #ff9fb0;
        --good: #bdf7da;
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        min-height: 100vh;
        background:
            radial-gradient(
                circle at 18% 12%,
                rgba(125, 79, 214, .22),
                transparent 34%
            ),
            radial-gradient(
                circle at 80% 16%,
                rgba(244, 210, 123, .12),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #030208,
                #090617 46%,
                #05040a
            );
        color: var(--text);
        font-family:
            Inter, ui-sans-serif, system-ui,
            -apple-system, BlinkMacSystemFont,
            "Segoe UI", sans-serif;
    }

    a {
        color: inherit;
    }

    .tower-shell {
        display: grid;
        grid-template-columns: 260px minmax(0, 1fr);
        min-height: 100vh;
    }

    .tower-rail {
        position: sticky;
        top: 0;
        height: 100vh;
        padding: 30px 22px;
        border-right: 1px solid var(--line);
        background:
            linear-gradient(
                180deg,
                rgba(18, 14, 29, .92),
                rgba(7, 6, 13, .84)
            );
        backdrop-filter: blur(22px);
    }

    .tower-mark {
        width: 58px;
        height: 58px;
        border-radius: 18px;
        display: grid;
        place-items: center;
        margin-bottom: 18px;
        color: #201307;
        font-size: 1.55rem;
        font-weight: 950;
        background:
            linear-gradient(
                135deg,
                var(--gold),
                #fff1b7
            );
        box-shadow:
            0 0 24px rgba(244, 210, 123, .24),
            inset 0 0 12px rgba(255,255,255,.5);
    }

    .tower-overline {
        color: var(--gold);
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .74rem;
        font-weight: 800;
    }

    .tower-rail h2 {
        margin: 8px 0 24px;
    }

    .tower-nav {
        display: grid;
        gap: 10px;
        margin: 24px 0;
    }

    .tower-nav a,
    .tower-rail-card {
        padding: 13px 14px;
        border: 1px solid var(--line);
        border-radius: 16px;
        background: rgba(255,255,255,.045);
        text-decoration: none;
        color: var(--muted);
    }

    .tower-nav a:hover {
        color: var(--text);
        border-color: rgba(244, 210, 123, .45);
        background: rgba(244, 210, 123, .08);
    }

    .tower-rail-card {
        margin-top: 28px;
        display: grid;
        gap: 6px;
    }

    .tower-rail-card span,
    .tower-status-tile span,
    .tower-panel-head span,
    .tower-card-top span {
        color: var(--dim);
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .11em;
        font-weight: 800;
    }

    .tower-main {
        padding: 34px;
    }

    .tower-hero {
        min-height: 260px;
        display: grid;
        grid-template-columns: minmax(0, 1fr) 260px;
        gap: 22px;
        align-items: end;
        padding: 34px;
        border: 1px solid var(--line);
        border-radius: 30px;
        background:
            linear-gradient(
                135deg,
                rgba(31, 23, 49, .88),
                rgba(9, 7, 16, .82)
            );
        box-shadow: 0 34px 120px rgba(0,0,0,.34);
        overflow: hidden;
        position: relative;
    }

    .tower-hero:before {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        right: -110px;
        top: -120px;
        border-radius: 999px;
        background:
            radial-gradient(
                circle,
                rgba(244, 210, 123, .18),
                rgba(125, 79, 214, .15) 42%,
                transparent 68%
            );
        filter: blur(4px);
    }

    .tower-hero > * {
        position: relative;
        z-index: 2;
    }

    .tower-hero h1 {
        margin: 10px 0 12px;
        font-size: clamp(2.4rem, 5vw, 5.7rem);
        line-height: .94;
        letter-spacing: -.06em;
    }

    .tower-hero p,
    .tower-section p,
    .tower-panel p,
    .tower-app-card p {
        color: var(--muted);
        line-height: 1.58;
    }

    .tower-session-card,
    .tower-status-tile,
    .tower-panel,
    .tower-app-card,
    .tower-detail {
        border: 1px solid var(--line);
        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,.075),
                rgba(255,255,255,.035)
            );
        backdrop-filter: blur(20px);
        box-shadow: 0 20px 70px rgba(0,0,0,.22);
    }

    .tower-session-card {
        border-radius: 24px;
        padding: 22px;
        display: grid;
        gap: 8px;
    }

    .tower-session-card strong {
        font-size: 1.6rem;
    }

    .tower-session-card small {
        color: var(--muted);
    }

    .tower-status-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 18px 0 28px;
    }

    .tower-status-tile {
        padding: 20px;
        border-radius: 20px;
    }

    .tower-status-tile strong {
        display: block;
        margin-top: 8px;
        font-size: 1.1rem;
    }

    .tower-section {
        margin-top: 28px;
    }

    .tower-section-head {
        display: flex;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 16px;
    }

    .tower-section h2 {
        margin: 0 0 6px;
        font-size: 1.7rem;
    }

    .tower-app-grid {
        display: grid;
        grid-template-columns:
            repeat(auto-fit, minmax(240px, 1fr));
        gap: 16px;
    }

    .tower-app-card {
        border-radius: 24px;
        padding: 22px;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }

    .tower-app-card-active {
        border-color: rgba(244, 210, 123, .5);
        background:
            radial-gradient(
                circle at 80% 8%,
                rgba(244, 210, 123, .14),
                transparent 32%
            ),
            linear-gradient(
                180deg,
                rgba(125, 79, 214, .2),
                rgba(255,255,255,.035)
            );
    }

    .tower-card-top,
    .tower-panel-head {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        align-items: center;
        margin-bottom: 12px;
    }

    .tower-app-card h3 {
        margin: 8px 0 8px;
        font-size: 1.45rem;
    }

    .tower-card-subtitle {
        color: var(--gold) !important;
        margin-top: 0;
    }

    .tower-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        width: fit-content;
        padding: 0 18px;
        border-radius: 999px;
        background:
            linear-gradient(
                135deg,
                var(--gold),
                #fff2bd
            );
        color: #1a1109;
        text-decoration: none;
        font-weight: 900;
        border: 0;
    }

    .tower-button.secondary {
        background: rgba(255,255,255,.08);
        color: var(--text);
        border: 1px solid var(--line);
    }

    .tower-lower-grid {
        display: grid;
        grid-template-columns:
            minmax(0, 1.05fr)
            minmax(0, 1fr)
            minmax(0, .85fr);
        gap: 16px;
        margin-top: 28px;
    }

    .tower-panel {
        border-radius: 24px;
        padding: 22px;
    }

    .tower-panel h3 {
        margin: 4px 0 12px;
        font-size: 1.25rem;
    }

    .tower-return-panel {
        border-color: rgba(244, 210, 123, .35);
    }

    .tower-action-row {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        padding: 13px 0;
        border-top: 1px solid var(--line);
    }

    .tower-action-row:first-of-type {
        border-top: 0;
    }

    .tower-action-row p {
        margin: 4px 0 0;
    }

    .tower-action-row span {
        color: var(--gold);
        white-space: nowrap;
        font-weight: 800;
    }

    .tower-quick-actions {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .tower-evidence {
        padding: 22px;
        border: 1px solid var(--line);
        border-radius: 24px;
        background: rgba(255,255,255,.035);
    }

    .tower-detail {
        border-radius: 16px;
        padding: 15px 16px;
        margin-top: 10px;
    }

    .tower-detail summary {
        cursor: pointer;
        color: var(--gold);
        font-weight: 850;
    }

    .tower-footer {
        color: var(--dim);
        margin: 30px 0 4px;
        font-size: .9rem;
    }

    .tower-sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border: 0;
    }

    .tower-ob-return-chip {
        position: fixed;
        left: 18px;
        bottom: 18px;
        z-index: 99999;
        display: inline-flex;
        align-items: center;
        min-height: 42px;
        padding: 0 16px;
        border-radius: 999px;
        color: #1a1109;
        background:
            linear-gradient(
                135deg,
                #f4d27b,
                #fff2bd
            );
        text-decoration: none;
        font-weight: 900;
        box-shadow: 0 14px 44px rgba(0,0,0,.34);
    }

    @media (max-width: 980px) {
        .tower-shell {
            grid-template-columns: 1fr;
        }

        .tower-rail {
            position: relative;
            height: auto;
        }

        .tower-hero,
        .tower-lower-grid,
        .tower-status-grid {
            grid-template-columns: 1fr;
        }

        .tower-main {
            padding: 20px;
        }
    }
    </style>
    """


def inject_ob_return_button(
    response,
    *,
    owner_session_active: bool,
):
    if (
        not owner_session_active
        or response.status_code != 200
        or not response.content_type
        or "text/html" not in response.content_type
        or not request.path.startswith(
            "/tower/observatory-walkthrough"
        )
    ):
        return response

    body = response.get_data(
        as_text=True
    )

    marker = "tower-ob-return-chip"

    if marker in body:
        return response

    chip = """
    <a
        class="tower-ob-return-chip"
        href="/tower/return/observatory"
    >
        Go back to Tower
    </a>
    """

    if "</body>" in body:
        body = body.replace(
            "</body>",
            chip + "</body>",
            1,
        )
    else:
        body += chip

    response.set_data(body)

    return response
