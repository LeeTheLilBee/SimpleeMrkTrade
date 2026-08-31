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
        "subtitle": "Market intelligence and trading",
        "status": "Protected entry",
        "tone": "protected",
        "href": "/tower/launch/observatory",
        "primary_action": "Enter Observatory",
        "description": (
            "Tower verifies the current owner session and "
            "required step-up before handing control to OB."
        ),
        "requires_step_up": True,
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



def verify_return_receipt(
    value: Dict[str, Any] | None,
) -> bool:
    if not isinstance(value, dict):
        return False

    supplied = deepcopy(value)

    supplied_hash = str(
        supplied.pop("receipt_hash", "")
        or ""
    )

    if not supplied_hash:
        return False

    return supplied_hash == receipt_hash(
        supplied
    )


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
        "username": session.get("tower_username"),
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
        "owner_actions_panel": False,
        "quick_launch_panel": True,
        "hidden_evidence_drawers": False,
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

    return_verified = verify_return_receipt(
        return_receipt
    )

    step_status = (
        "Verified for protected entry"
        if summary["step_up_active"]
        else "Additional verification required"
    )

    return_status = (
        "Verified return receipt"
        if return_verified
        else "No verified return receipt"
    )

    card_html = "\n".join(
        _render_app_card(card)
        for card in APP_CARDS
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
                    <h2>Access Home</h2>
                </div>

                <nav class="tower-nav">
                    <a href="/tower/access-home">
                        Access Home
                    </a>

                    <a href="/tower/launch/observatory">
                        Observatory
                    </a>

                    <a href="/tower/owner-dashboard">
                        Owner Headquarters
                    </a>

                    <a href="/tower/logout">
                        Logout
                    </a>
                </nav>

                <div class="tower-rail-card">
                    <span>Session role</span>
                    <strong>
                        {escape(str(summary["role"] or "UNAVAILABLE"))}
                    </strong>
                </div>
            </aside>

            <section class="tower-main">
                <header class="tower-hero">
                    <div>
                        <div class="tower-overline">
                            Tower Access Home
                        </div>

                        <h1>
                            Welcome back, {escape(username)}.
                        </h1>

                        <p>
                            Tower shows only doors and state it can
                            support. Unpublished products stay out
                            of the operating surface.
                        </p>
                    </div>

                    <div class="tower-session-card">
                        <span>Owner session</span>

                        <strong>
                            {
                                "Authenticated"
                                if summary["authenticated"]
                                else "Not authenticated"
                            }
                        </strong>

                        <small>
                            Step-up: {escape(step_status)}
                        </small>
                    </div>
                </header>

                <section class="tower-status-grid">
                    <div class="tower-status-tile">
                        <span>Role</span>
                        <strong>
                            {escape(str(summary["role"] or "UNAVAILABLE"))}
                        </strong>
                    </div>

                    <div class="tower-status-tile">
                        <span>Boundary</span>
                        <strong>Default deny</strong>
                    </div>

                    <div class="tower-status-tile">
                        <span>OB entry</span>
                        <strong>{escape(step_status)}</strong>
                    </div>

                    <div class="tower-status-tile">
                        <span>Return</span>
                        <strong>{escape(return_status)}</strong>
                    </div>
                </section>

                <section class="tower-section">
                    <div class="tower-section-head">
                        <div>
                            <h2>Your access</h2>
                            <p>
                                Only published product entry belongs here.
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
                            Technical receipt proof is not shown
                            on the normal Access Home.
                        </p>
                    </article>

                    <article class="tower-panel">
                        <div class="tower-panel-head">
                            <span>Owner control</span>
                            <strong>Protected</strong>
                        </div>

                        <h3>Owner Headquarters</h3>

                        <p>
                            People and access state will remain
                            explicitly unavailable until authoritative
                            providers are connected.
                        </p>

                        <a
                            class="tower-button secondary"
                            href="/tower/owner-dashboard"
                        >
                            Open Owner Headquarters
                        </a>
                    </article>

                    <article class="tower-panel">
                        <div class="tower-panel-head">
                            <span>Product entry</span>
                            <strong>Protected</strong>
                        </div>

                        <h3>The Observatory</h3>

                        <p>
                            Tower performs the current session and
                            step-up boundary before product handoff.
                        </p>

                        <a
                            class="tower-button"
                            href="/tower/launch/observatory"
                        >
                            Enter Observatory
                        </a>
                    </article>
                </section>

                <footer class="tower-footer">
                    Tower Access Home · © Simplee
                </footer>
            </section>
        </main>
    </body>
    </html>
    """

    return render_template_string(
        page
    )


def _render_app_card(
    card: Dict[str, Any],
) -> str:
    step_label = (
        "<span>Step-up protected</span>"
        if card.get("requires_step_up")
        else "<span>Protected</span>"
    )

    return f"""
    <article
        id="{escape(card["id"])}-entry"
        class="tower-app-card tower-app-card-active"
    >
        <div class="tower-card-top">
            <span>{escape(card["status"])}</span>
            {step_label}
        </div>

        <h3>{escape(card["name"])}</h3>

        <p class="tower-card-subtitle">
            {escape(card["subtitle"])}
        </p>

        <p>
            {escape(card["description"])}
        </p>

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
    # Compatibility symbol only.
    # Historical UI injection behavior is retired.
    return response
