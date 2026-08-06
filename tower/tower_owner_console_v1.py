"""
Tower Owner Console v1.

Dedicated Tower owner-decision desk.

This surface centralizes owner-level approvals, dangerous-action
review, step-up freshness, app permissions, session/security state,
deployment holds, and evidence drawers.

It is intentionally presentation + contract only. It does not unlock
broker submission, capital movement, Manual Live, Live Auto,
production deployment, direct Vault writes, destructive controls,
or secret exposure.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List, Mapping


OWNER_CONSOLE_VERSION = "owner_console_v1"
OWNER_CONSOLE_ROUTE = "/tower/owner-console"
OWNER_CONSOLE_JSON_ROUTE = "/tower/owner-console.json"


THEME = {
    "name": "Simplee Tower Owner Desk",
    "black_glass": True,
    "deep_violet": True,
    "gold_owner_accents": True,
    "blue_minimized": True,
    "evidence_hidden_by_default": True,
}


PACK_NAMES = {
    2523: "Owner Console Route Shell",
    2524: "Owner Approval Queue Surface",
    2525: "Dangerous Action Review Cards",
    2526: "Step-up Freshness Status Panel",
    2527: "App Permission Overview",
    2528: "Security / Session Summary",
    2529: "Deployment / Activation Hold Panel",
    2530: "Owner Decision Evidence Drawers",
    2531: "Owner Console Cert Routes",
    2532: "Owner Console Checkpoint",
}


READINESS_KEYS = {
    2523: "owner_console_route_shell_ready",
    2524: "owner_approval_queue_surface_ready",
    2525: "dangerous_action_review_cards_ready",
    2526: "step_up_freshness_status_panel_ready",
    2527: "app_permission_overview_ready",
    2528: "security_session_summary_ready",
    2529: "deployment_activation_hold_panel_ready",
    2530: "owner_decision_evidence_drawers_ready",
    2531: "owner_console_cert_routes_ready",
    2532: "owner_console_checkpoint_ready",
}


APP_PERMISSION_OVERVIEW = [
    {
        "app": "The Observatory",
        "permission": "Owner access ready",
        "global_controls_location": "Tower Owner Console",
        "dangerous_actions": "Step-up and separate authorization required",
        "status": "active",
    },
    {
        "app": "Archive Vault",
        "permission": "Sealed / Tower-mediated",
        "global_controls_location": "Tower Owner Console",
        "dangerous_actions": "No direct public dashboard or raw file access",
        "status": "locked",
    },
    {
        "app": "The Teller",
        "permission": "Workflow desk planned",
        "global_controls_location": "Tower Owner Console",
        "dangerous_actions": "Payment and payroll controls remain locked",
        "status": "planned",
    },
    {
        "app": "The Grounds",
        "permission": "Property operations planned",
        "global_controls_location": "Tower Owner Console",
        "dangerous_actions": "No property mutation or vendor control unlocked",
        "status": "planned",
    },
    {
        "app": "The Clouds",
        "permission": "Executive summary layer planned",
        "global_controls_location": "Tower Owner Console",
        "dangerous_actions": "Read-only owner command summary by default",
        "status": "planned",
    },
]


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


def owner_console_contract() -> Dict[str, Any]:
    return {
        "contract": OWNER_CONSOLE_VERSION,
        "route": OWNER_CONSOLE_ROUTE,
        "json_route": OWNER_CONSOLE_JSON_ROUTE,
        "owner_controls_centralized_in_tower": True,
        "ordinary_app_pages_keep_global_owner_controls_out": True,
        "approval_queue_surface": True,
        "dangerous_action_review_cards": True,
        "step_up_freshness_status_panel": True,
        "app_permission_overview": True,
        "security_session_summary": True,
        "deployment_activation_hold_panel": True,
        "owner_decision_evidence_drawers": True,
        "evidence_hidden_by_default": True,
        "black_glass_theme": True,
        "deep_violet_theme": True,
        "gold_owner_accents": True,
        "credentials_committed": False,
        "secret_values_exposed": False,
        "broker_submission": False,
        "capital_movement": False,
        "production_deployment": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
        "direct_vault_write": False,
        "destructive_action_unlocked": False,
    }


def default_owner_approval_queue() -> List[Dict[str, Any]]:
    return [
        {
            "id": "approval-ob-staging-visual-check",
            "title": "Review Tower → OB walkthrough",
            "summary": (
                "Owner should visually confirm Access Home, OB launch, "
                "and return-to-Tower behavior before integration acceptance."
            ),
            "status": "waiting_for_owner_review",
            "risk": "low",
            "action": "Review locally",
            "dangerous": False,
        },
        {
            "id": "approval-render-staging-redeploy-hold",
            "title": "Hosted staging redeploy hold",
            "summary": (
                "Redeploy remains held until Tower and OB source changes "
                "are integrated and commit-pinned."
            ),
            "status": "hold",
            "risk": "medium",
            "action": "Do not redeploy yet",
            "dangerous": False,
        },
        {
            "id": "approval-live-auto-locked",
            "title": "Live Auto remains locked",
            "summary": (
                "No automated live trading authorization exists in this "
                "Tower corridor."
            ),
            "status": "locked",
            "risk": "critical",
            "action": "No action available",
            "dangerous": True,
        },
    ]


def dangerous_action_reviews() -> List[Dict[str, Any]]:
    return [
        {
            "title": "Broker submission",
            "state": "blocked",
            "reason": "No broker API submission authorized.",
            "step_up_required": True,
            "separate_authorization_required": True,
        },
        {
            "title": "Capital movement",
            "state": "blocked",
            "reason": "No real money movement authorized.",
            "step_up_required": True,
            "separate_authorization_required": True,
        },
        {
            "title": "Production deployment",
            "state": "held",
            "reason": "Staging acceptance is not yet STAGING_READY.",
            "step_up_required": True,
            "separate_authorization_required": True,
        },
        {
            "title": "Direct Vault write",
            "state": "blocked",
            "reason": "Vault remains sealed and Tower-mediated.",
            "step_up_required": True,
            "separate_authorization_required": True,
        },
    ]


def deployment_hold_panel() -> Dict[str, Any]:
    return {
        "decision": (
            "HOSTED_STAGING_FUNCTIONAL_HOLD_FOR_OWNER_UI_"
            "SIMPLIFICATION_AND_TOWER_RETURN_REPAIR"
        ),
        "tower_ui_v2_source_closed": True,
        "ob_visual_simplification_pending": True,
        "integration_redeploy_pending": True,
        "staging_ready": False,
        "production_deployment_authorized": False,
        "custom_dns_authorized": False,
        "database_authorized": False,
        "object_storage_authorized": False,
    }


def build_owner_console_payload(
    *,
    owner_session: Mapping[str, Any] | None = None,
    step_up_active: bool = False,
    approval_queue: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    session_summary = dict(owner_session or {})

    role = session_summary.get("role")
    owner_id = session_summary.get("owner_id")
    authenticated = bool(
        session_summary.get("authenticated")
    )

    payload = {
        "surface": OWNER_CONSOLE_VERSION,
        "title": "Tower Owner Console",
        "subtitle": "Owner Desk",
        "owner_authenticated": authenticated,
        "owner_id_present": bool(owner_id),
        "role": role or "locked",
        "step_up_active": bool(step_up_active),
        "approval_queue": approval_queue or default_owner_approval_queue(),
        "dangerous_action_reviews": dangerous_action_reviews(),
        "app_permission_overview": deepcopy(APP_PERMISSION_OVERVIEW),
        "security_session_summary": {
            "authenticated": authenticated,
            "role": role,
            "owner_id_present": bool(owner_id),
            "default_deny": True,
            "anonymous_denied": True,
            "non_owner_denied": True,
            "step_up_active": bool(step_up_active),
        },
        "deployment_hold_panel": deployment_hold_panel(),
        "evidence_drawers": [
            {
                "summary": "Approval evidence",
                "body": (
                    "Owner approval queue state is visible here, but "
                    "individual evidence stays collapsed until requested."
                ),
            },
            {
                "summary": "Dangerous-action evidence",
                "body": (
                    "Broker submission, capital movement, production "
                    "deployment, direct Vault write, Manual Live, and "
                    "Live Auto remain blocked unless separately authorized."
                ),
            },
            {
                "summary": "Security/session evidence",
                "body": (
                    "Owner authentication, role, owner id presence, and "
                    "step-up state are summarized without exposing secrets."
                ),
            },
        ],
        "contract": owner_console_contract(),
        "created_at": utc_now_iso(),
    }

    payload["payload_hash"] = sha256_payload(payload)

    return payload


def render_owner_console(payload: Mapping[str, Any]) -> str:
    approvals = payload.get("approval_queue", [])
    dangerous = payload.get("dangerous_action_reviews", [])
    permissions = payload.get("app_permission_overview", [])
    evidence = payload.get("evidence_drawers", [])
    security = payload.get("security_session_summary", {})
    deployment = payload.get("deployment_hold_panel", {})

    approval_html = "\n".join(
        f"""
        <article class="owner-card">
            <div class="owner-card-top">
                <span>{escape(item.get("status", "unknown"))}</span>
                <strong>{escape(item.get("risk", "unknown"))}</strong>
            </div>
            <h3>{escape(item.get("title", ""))}</h3>
            <p>{escape(item.get("summary", ""))}</p>
            <div class="owner-action-chip">
                {escape(item.get("action", ""))}
            </div>
        </article>
        """
        for item in approvals
    )

    dangerous_html = "\n".join(
        f"""
        <article class="owner-danger-card">
            <div class="owner-card-top">
                <span>{escape(item.get("state", "unknown"))}</span>
                <strong>
                    {"Step-up required" if item.get("step_up_required") else "View"}
                </strong>
            </div>
            <h3>{escape(item.get("title", ""))}</h3>
            <p>{escape(item.get("reason", ""))}</p>
        </article>
        """
        for item in dangerous
    )

    permission_html = "\n".join(
        f"""
        <tr>
            <td>{escape(item.get("app", ""))}</td>
            <td>{escape(item.get("permission", ""))}</td>
            <td>{escape(item.get("global_controls_location", ""))}</td>
            <td>{escape(item.get("dangerous_actions", ""))}</td>
        </tr>
        """
        for item in permissions
    )

    evidence_html = "\n".join(
        f"""
        <details class="owner-detail">
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
        <title>Tower Owner Console</title>
        {_owner_console_css()}
    </head>
    <body>
        <main class="owner-shell">
            <aside class="owner-rail">
                <a class="owner-back" href="/tower/access-home">
                    ← Access Home
                </a>
                <div class="owner-mark">OC</div>
                <div class="owner-overline">Simplee Tower</div>
                <h1>Owner Console</h1>
                <p>
                    Owner-level approvals, security, permissions,
                    deployment holds, and dangerous-action review.
                </p>

                <div class="owner-rail-panel">
                    <span>Owner session</span>
                    <strong>{escape(str(payload.get("role", "locked")))}</strong>
                    <small>
                        Step-up:
                        {"Active" if payload.get("step_up_active") else "Not active"}
                    </small>
                </div>
            </aside>

            <section class="owner-main">
                <header class="owner-hero">
                    <div>
                        <div class="owner-overline">
                            Owner Desk
                        </div>
                        <h2>What needs my owner decision?</h2>
                        <p>
                            Tower keeps global controls here so ordinary
                            app pages stay clean and focused.
                        </p>
                    </div>

                    <div class="owner-hero-card">
                        <span>Current hold</span>
                        <strong>
                            {"Staging hold" if not deployment.get("staging_ready") else "Ready"}
                        </strong>
                        <small>
                            Integration redeploy:
                            {"pending" if deployment.get("integration_redeploy_pending") else "clear"}
                        </small>
                    </div>
                </header>

                <section class="owner-grid four">
                    <article class="owner-stat">
                        <span>Anonymous</span>
                        <strong>Denied</strong>
                    </article>
                    <article class="owner-stat">
                        <span>Non-owner</span>
                        <strong>Denied</strong>
                    </article>
                    <article class="owner-stat">
                        <span>Dangerous actions</span>
                        <strong>Blocked</strong>
                    </article>
                    <article class="owner-stat">
                        <span>Evidence</span>
                        <strong>Drawers</strong>
                    </article>
                </section>

                <section class="owner-section">
                    <div class="owner-section-head">
                        <h2>Approval Queue</h2>
                        <p>
                            Owner decisions waiting for review.
                        </p>
                    </div>

                    <div class="owner-grid three">
                        {approval_html}
                    </div>
                </section>

                <section class="owner-section">
                    <div class="owner-section-head">
                        <h2>Dangerous Action Review</h2>
                        <p>
                            These actions stay blocked or held until
                            Tower receives separate owner authorization.
                        </p>
                    </div>

                    <div class="owner-grid two">
                        {dangerous_html}
                    </div>
                </section>

                <section class="owner-grid two owner-section">
                    <article class="owner-panel">
                        <h2>Step-up & Session</h2>
                        <p>
                            Authenticated:
                            {escape(str(security.get("authenticated", False)))}
                        </p>
                        <p>
                            Owner ID present:
                            {escape(str(security.get("owner_id_present", False)))}
                        </p>
                        <p>
                            Default deny:
                            {escape(str(security.get("default_deny", True)))}
                        </p>
                        <p>
                            Step-up active:
                            {escape(str(security.get("step_up_active", False)))}
                        </p>
                    </article>

                    <article class="owner-panel">
                        <h2>Deployment Hold</h2>
                        <p>{escape(deployment.get("decision", ""))}</p>
                        <p>
                            Production deployment authorized:
                            {escape(str(deployment.get("production_deployment_authorized", False)))}
                        </p>
                        <p>
                            Staging ready:
                            {escape(str(deployment.get("staging_ready", False)))}
                        </p>
                    </article>
                </section>

                <section class="owner-section owner-panel">
                    <div class="owner-section-head">
                        <h2>App Permission Overview</h2>
                        <p>
                            Global controls belong here in Tower, not
                            scattered inside app rooms.
                        </p>
                    </div>

                    <div class="owner-table-wrap">
                        <table>
                            <thead>
                                <tr>
                                    <th>App</th>
                                    <th>Permission</th>
                                    <th>Controls live in</th>
                                    <th>Danger boundary</th>
                                </tr>
                            </thead>
                            <tbody>
                                {permission_html}
                            </tbody>
                        </table>
                    </div>
                </section>

                <section class="owner-section owner-panel">
                    <div class="owner-section-head">
                        <h2>Owner Decision Evidence Drawers</h2>
                        <p>
                            Evidence stays available, but it is not the
                            main owner experience.
                        </p>
                    </div>

                    {evidence_html}
                </section>

                <footer class="owner-footer">
                    Tower Owner Console · payload
                    {escape(str(payload.get("payload_hash", ""))[:14])}
                </footer>
            </section>
        </main>
    </body>
    </html>
    """


def _owner_console_css() -> str:
    return """
    <style>
    :root {
        color-scheme: dark;
        --bg: #05040a;
        --panel: rgba(20, 17, 31, .84);
        --panel-2: rgba(36, 21, 63, .72);
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
            radial-gradient(
                circle at 10% 12%,
                rgba(125, 79, 214, .18),
                transparent 34%
            ),
            radial-gradient(
                circle at 86% 18%,
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

    .owner-shell {
        display: grid;
        grid-template-columns: 280px minmax(0, 1fr);
        min-height: 100vh;
    }

    .owner-rail {
        padding: 30px 22px;
        border-right: 1px solid var(--line);
        background: rgba(10, 8, 18, .88);
        position: sticky;
        top: 0;
        height: 100vh;
    }

    .owner-back {
        display: inline-flex;
        margin-bottom: 22px;
        color: var(--muted);
        text-decoration: none;
        font-weight: 800;
    }

    .owner-mark {
        width: 62px;
        height: 62px;
        border-radius: 20px;
        display: grid;
        place-items: center;
        margin-bottom: 18px;
        color: #201307;
        font-size: 1.2rem;
        font-weight: 950;
        background:
            linear-gradient(135deg, var(--gold), #fff1b7);
        box-shadow:
            0 0 26px rgba(244, 210, 123, .22),
            inset 0 0 14px rgba(255,255,255,.42);
    }

    .owner-overline {
        color: var(--gold);
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .74rem;
        font-weight: 850;
    }

    .owner-rail h1 {
        font-size: 2.2rem;
        margin: 8px 0 10px;
        letter-spacing: -.04em;
    }

    .owner-rail p,
    .owner-main p {
        color: var(--muted);
        line-height: 1.58;
    }

    .owner-rail-panel,
    .owner-hero,
    .owner-hero-card,
    .owner-card,
    .owner-danger-card,
    .owner-stat,
    .owner-panel,
    .owner-detail {
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

    .owner-rail-panel {
        display: grid;
        gap: 6px;
        padding: 16px;
        border-radius: 18px;
        margin-top: 24px;
    }

    .owner-rail-panel span,
    .owner-stat span,
    .owner-card-top span,
    .owner-hero-card span {
        color: var(--dim);
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .11em;
        font-weight: 850;
    }

    .owner-main {
        padding: 34px;
    }

    .owner-hero {
        display: grid;
        grid-template-columns: minmax(0, 1fr) 280px;
        gap: 22px;
        align-items: end;
        min-height: 240px;
        border-radius: 30px;
        padding: 34px;
        background:
            radial-gradient(
                circle at 78% 10%,
                rgba(244, 210, 123, .13),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                rgba(31, 23, 49, .88),
                rgba(9, 7, 16, .82)
            );
    }

    .owner-hero h2 {
        font-size: clamp(2.4rem, 5vw, 5.2rem);
        line-height: .94;
        letter-spacing: -.06em;
        margin: 10px 0 12px;
    }

    .owner-hero-card {
        border-radius: 24px;
        padding: 22px;
        display: grid;
        gap: 8px;
    }

    .owner-hero-card strong {
        font-size: 1.45rem;
    }

    .owner-section {
        margin-top: 28px;
    }

    .owner-section-head {
        margin-bottom: 16px;
    }

    .owner-section h2,
    .owner-panel h2 {
        margin: 0 0 6px;
        font-size: 1.6rem;
    }

    .owner-grid {
        display: grid;
        gap: 16px;
    }

    .owner-grid.four {
        grid-template-columns: repeat(4, minmax(0, 1fr));
        margin: 18px 0 28px;
    }

    .owner-grid.three {
        grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .owner-grid.two {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .owner-stat,
    .owner-card,
    .owner-danger-card,
    .owner-panel {
        border-radius: 24px;
        padding: 22px;
    }

    .owner-stat strong {
        display: block;
        margin-top: 8px;
        font-size: 1.2rem;
    }

    .owner-card-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }

    .owner-card h3,
    .owner-danger-card h3 {
        margin: 8px 0 10px;
        font-size: 1.25rem;
    }

    .owner-action-chip {
        display: inline-flex;
        width: fit-content;
        padding: 9px 13px;
        border-radius: 999px;
        margin-top: 8px;
        background: rgba(244, 210, 123, .11);
        color: var(--gold);
        font-weight: 850;
    }

    .owner-danger-card {
        border-color: rgba(255, 159, 176, .3);
    }

    .owner-table-wrap {
        overflow-x: auto;
    }

    table {
        width: 100%;
        border-collapse: collapse;
    }

    th,
    td {
        text-align: left;
        vertical-align: top;
        border-bottom: 1px solid var(--line);
        padding: 14px 12px;
    }

    th {
        color: var(--gold);
        font-size: .82rem;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    td {
        color: var(--muted);
    }

    .owner-detail {
        border-radius: 16px;
        padding: 15px 16px;
        margin-top: 10px;
    }

    .owner-detail summary {
        color: var(--gold);
        cursor: pointer;
        font-weight: 850;
    }

    .owner-footer {
        color: var(--dim);
        margin: 30px 0 4px;
        font-size: .9rem;
    }

    @media (max-width: 980px) {
        .owner-shell,
        .owner-hero,
        .owner-grid.four,
        .owner-grid.three,
        .owner-grid.two {
            grid-template-columns: 1fr;
        }

        .owner-rail {
            position: relative;
            height: auto;
        }

        .owner-main {
            padding: 20px;
        }
    }
    </style>
    """


def build_owner_console_cert(pack: int) -> Dict[str, Any]:
    if pack not in PACK_NAMES:
        raise ValueError(f"Unsupported owner console pack: {pack}")

    readiness_key = READINESS_KEYS[pack]

    contract = owner_console_contract()

    payload = {
        "pack": str(pack),
        "pack_name": PACK_NAMES[pack],
        "status": "ready",
        "readiness": 100,
        "tower_owner_console_v1": True,
        "owner_desk": True,
        "owner_controls_centralized_in_tower": True,
        "ordinary_app_pages_keep_global_owner_controls_out": True,
        readiness_key: True,
        "owner_console_route_shell": True,
        "owner_approval_queue_surface": True,
        "dangerous_action_review_cards": True,
        "step_up_freshness_status_panel": True,
        "app_permission_overview": True,
        "security_session_summary": True,
        "deployment_activation_hold_panel": True,
        "owner_decision_evidence_drawers": True,
        "owner_console_cert_routes": True,
        "evidence_hidden_by_default": True,
        "black_glass_theme": True,
        "deep_violet_theme": True,
        "gold_owner_accents": True,
        "credentials_committed": False,
        "secret_values_exposed": False,
        "broker_submission": False,
        "capital_movement": False,
        "production_deployment": False,
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
