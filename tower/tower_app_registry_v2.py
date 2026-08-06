"""
Tower App Registry v2 / Ecosystem Door Registry.

Tower's source of truth for the ecosystem doors shown from
Access Home and controlled through Owner Console.

This module defines:
- door metadata
- launch routes
- status/readiness
- permission boundaries
- owner-control linkage
- integration-readiness summaries
- hidden evidence drawers

It does not unlock broker submission, capital movement, Manual Live,
Live Auto, production deployment, direct Vault writes, destructive
controls, credentials, or secret values.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List, Mapping


APP_REGISTRY_VERSION = "app_registry_v2"
APP_REGISTRY_ROUTE = "/tower/app-registry"
APP_REGISTRY_JSON_ROUTE = "/tower/app-registry.json"


PACK_NAMES = {
    2533: "Ecosystem Door Registry Contract",
    2534: "Door Card Metadata Model",
    2535: "Door Status + Readiness Model",
    2536: "Door Permission Boundary Model",
    2537: "Door Launch / Route Map",
    2538: "Door Owner-Control Linkage",
    2539: "Door Integration Readiness View",
    2540: "Door Evidence Drawers",
    2541: "Registry Cert Routes",
    2542: "Ecosystem Door Registry Checkpoint",
}


READINESS_KEYS = {
    2533: "ecosystem_door_registry_contract_ready",
    2534: "door_card_metadata_model_ready",
    2535: "door_status_readiness_model_ready",
    2536: "door_permission_boundary_model_ready",
    2537: "door_launch_route_map_ready",
    2538: "door_owner_control_linkage_ready",
    2539: "door_integration_readiness_view_ready",
    2540: "door_evidence_drawers_ready",
    2541: "registry_cert_routes_ready",
    2542: "ecosystem_door_registry_checkpoint_ready",
}


DOORS = [
    {
        "id": "observatory",
        "name": "The Observatory",
        "short_name": "OB",
        "stone_role": "Mind / market intelligence",
        "purpose": "Market intelligence, trading command, review, and owner walkthrough.",
        "launch_route": "/tower/launch/observatory",
        "return_route": "/tower/return/observatory",
        "status": "source_ready_for_integration",
        "readiness": "tower_launch_and_return_ready",
        "door_state": "open_to_owner_after_step_up",
        "theme_hint": "cosmic market room",
        "primary_action": "Open Observatory",
        "owner_controls_route": "/tower/owner-console",
        "permission_boundary": "owner_session_required_plus_step_up_for_launch",
        "danger_boundary": "no broker submission, no capital movement, Manual Live and Live Auto locked",
        "integration_status": "pending_tower_ob_integration_redeploy",
        "evidence_policy": "receipts and handoff evidence hidden in Tower drawers",
        "visible_on_access_home": True,
    },
    {
        "id": "vault",
        "name": "Archive Vault",
        "short_name": "Vault",
        "stone_role": "sealed memory",
        "purpose": "Sealed evidence, documents, receipts, recovery records, and archive memory.",
        "launch_route": "/tower/owner-console#vault",
        "return_route": "/tower/access-home",
        "status": "sealed",
        "readiness": "tower_mediated_only",
        "door_state": "locked_safe",
        "theme_hint": "sealed archive",
        "primary_action": "View Vault status",
        "owner_controls_route": "/tower/owner-console",
        "permission_boundary": "tower_mediated_owner_controls_only",
        "danger_boundary": "no direct public dashboard, no raw file URLs, no direct user Vault portal",
        "integration_status": "vault_source_work_separate",
        "evidence_policy": "sealed evidence references only",
        "visible_on_access_home": True,
    },
    {
        "id": "teller",
        "name": "The Teller",
        "short_name": "Teller",
        "stone_role": "workflow / power desk",
        "purpose": "People, payroll, payments, vendor, employee, onboarding, and request workflows.",
        "launch_route": "/tower/owner-console#teller",
        "return_route": "/tower/access-home",
        "status": "planned",
        "readiness": "workflow_surface_pending",
        "door_state": "preview_only",
        "theme_hint": "finance workflow desk",
        "primary_action": "Preview Teller",
        "owner_controls_route": "/tower/owner-console",
        "permission_boundary": "payments_and_payroll_locked_until_future_authorization",
        "danger_boundary": "no payment execution, payroll execution, or money movement",
        "integration_status": "future_teller_integration",
        "evidence_policy": "workflow proof stays Tower/Vault mediated",
        "visible_on_access_home": True,
    },
    {
        "id": "grounds",
        "name": "The Grounds",
        "short_name": "Grounds",
        "stone_role": "Reality / physical asset operations",
        "purpose": "Property operations, assets, units, leases, vendors, maintenance, taxes, and stewardship.",
        "launch_route": "/tower/owner-console#grounds",
        "return_route": "/tower/access-home",
        "status": "planned",
        "readiness": "property_surface_pending",
        "door_state": "preview_only",
        "theme_hint": "premium property operations",
        "primary_action": "Preview Grounds",
        "owner_controls_route": "/tower/owner-console",
        "permission_boundary": "property_mutations_locked_until_future_authorization",
        "danger_boundary": "no vendor activation, lease mutation, property write, or payment action",
        "integration_status": "future_grounds_integration",
        "evidence_policy": "property proof and documents remain Vault/Tower mediated",
        "visible_on_access_home": True,
    },
    {
        "id": "clouds",
        "name": "The Clouds",
        "short_name": "Clouds",
        "stone_role": "executive summary / time layer",
        "purpose": "Owner executive summaries, cross-business status, attention, and command overview.",
        "launch_route": "/tower/owner-console#clouds",
        "return_route": "/tower/access-home",
        "status": "planned",
        "readiness": "executive_summary_surface_pending",
        "door_state": "preview_only",
        "theme_hint": "soft executive command layer",
        "primary_action": "Preview Clouds",
        "owner_controls_route": "/tower/owner-console",
        "permission_boundary": "read_summary_only_until_future_authorization",
        "danger_boundary": "no mutation, deployment, capital, payroll, or broker control",
        "integration_status": "future_clouds_integration",
        "evidence_policy": "summaries reference Tower-approved safe states",
        "visible_on_access_home": True,
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


def app_registry_contract() -> Dict[str, Any]:
    return {
        "contract": APP_REGISTRY_VERSION,
        "route": APP_REGISTRY_ROUTE,
        "json_route": APP_REGISTRY_JSON_ROUTE,
        "tower_source_of_truth_for_app_doors": True,
        "ecosystem_doors_registered": True,
        "door_card_metadata_model": True,
        "door_status_readiness_model": True,
        "door_permission_boundary_model": True,
        "door_launch_route_map": True,
        "door_owner_control_linkage": True,
        "door_integration_readiness_view": True,
        "door_evidence_drawers": True,
        "visible_door_count": len(DOORS),
        "registered_door_ids": [door["id"] for door in DOORS],
        "owner_controls_route": "/tower/owner-console",
        "access_home_route": "/tower/access-home",
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


def ecosystem_doors() -> List[Dict[str, Any]]:
    return deepcopy(DOORS)


def door_by_id(door_id: str) -> Dict[str, Any]:
    for door in DOORS:
        if door["id"] == door_id:
            return deepcopy(door)

    raise KeyError(f"Unknown ecosystem door: {door_id}")


def integration_readiness_summary() -> Dict[str, Any]:
    return {
        "tower_access_home_v2": "closed",
        "tower_owner_console_v1": "closed",
        "tower_app_registry_v2": "building_or_ready",
        "observatory_simplification": "pending",
        "tower_ob_integration_branch": "pending",
        "render_staging_redeploy": "pending",
        "staging_ready": False,
        "production_ready": False,
        "reason": (
            "Tower doors and owner-control surfaces are being made "
            "integration-ready before hosted staging redeploy."
        ),
    }


def evidence_drawers() -> List[Dict[str, Any]]:
    return [
        {
            "summary": "Door registry evidence",
            "body": (
                "Tower records the five ecosystem doors, their launch routes, "
                "permission boundaries, owner-control linkage, and integration status."
            ),
        },
        {
            "summary": "Danger boundary evidence",
            "body": (
                "The registry does not authorize broker submission, capital movement, "
                "Manual Live, Live Auto, production deployment, direct Vault write, "
                "secret exposure, or destructive controls."
            ),
        },
        {
            "summary": "Integration readiness evidence",
            "body": (
                "Tower Access Home v2 and Owner Console v1 are closed. OB visual "
                "simplification and Tower-OB integration redeploy remain pending."
            ),
        },
    ]


def build_app_registry_payload(
    *,
    owner_authenticated: bool = False,
    role: str | None = None,
) -> Dict[str, Any]:
    payload = {
        "surface": APP_REGISTRY_VERSION,
        "title": "Tower App Registry",
        "subtitle": "Ecosystem Door Registry",
        "owner_authenticated": bool(owner_authenticated),
        "role": role or "locked",
        "doors": ecosystem_doors(),
        "integration_readiness": integration_readiness_summary(),
        "evidence_drawers": evidence_drawers(),
        "contract": app_registry_contract(),
        "created_at": utc_now_iso(),
    }

    payload["payload_hash"] = sha256_payload(payload)

    return payload


def render_app_registry(payload: Mapping[str, Any]) -> str:
    doors = payload.get("doors", [])
    readiness = payload.get("integration_readiness", {})
    evidence = payload.get("evidence_drawers", [])

    door_cards = "\n".join(
        _render_door_card(door)
        for door in doors
    )

    evidence_html = "\n".join(
        f"""
        <details class="registry-detail">
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
        <title>Tower App Registry</title>
        {_registry_css()}
    </head>
    <body>
        <main class="registry-shell">
            <aside class="registry-rail">
                <a class="registry-back" href="/tower/access-home">
                    ← Access Home
                </a>
                <a class="registry-back" href="/tower/owner-console">
                    Owner Console
                </a>
                <div class="registry-mark">DR</div>
                <div class="registry-overline">Simplee Tower</div>
                <h1>Door Registry</h1>
                <p>
                    The official Tower map of Simplee app doors,
                    routes, permissions, readiness, and owner controls.
                </p>

                <div class="registry-rail-panel">
                    <span>Door count</span>
                    <strong>{len(doors)}</strong>
                    <small>Owner controls live in Tower</small>
                </div>
            </aside>

            <section class="registry-main">
                <header class="registry-hero">
                    <div>
                        <div class="registry-overline">
                            Ecosystem Door Registry
                        </div>
                        <h2>What doors exist in Simplee?</h2>
                        <p>
                            Tower is the source of truth for what opens,
                            what stays locked, and where owner controls live.
                        </p>
                    </div>

                    <div class="registry-hero-card">
                        <span>Integration status</span>
                        <strong>
                            {"Pending" if not readiness.get("staging_ready") else "Ready"}
                        </strong>
                        <small>
                            OB simplification:
                            {escape(str(readiness.get("observatory_simplification", "pending")))}
                        </small>
                    </div>
                </header>

                <section class="registry-grid status">
                    <article class="registry-stat">
                        <span>Access Home</span>
                        <strong>{escape(str(readiness.get("tower_access_home_v2", "unknown")))}</strong>
                    </article>
                    <article class="registry-stat">
                        <span>Owner Console</span>
                        <strong>{escape(str(readiness.get("tower_owner_console_v1", "unknown")))}</strong>
                    </article>
                    <article class="registry-stat">
                        <span>Integration</span>
                        <strong>{escape(str(readiness.get("tower_ob_integration_branch", "pending")))}</strong>
                    </article>
                    <article class="registry-stat">
                        <span>Staging Ready</span>
                        <strong>{escape(str(readiness.get("staging_ready", False)))}</strong>
                    </article>
                </section>

                <section class="registry-section">
                    <div class="registry-section-head">
                        <h2>Registered Doors</h2>
                        <p>
                            Each app gets one Tower door with a clear
                            route, boundary, readiness, and owner-control link.
                        </p>
                    </div>

                    <div class="registry-door-grid">
                        {door_cards}
                    </div>
                </section>

                <section class="registry-section registry-panel">
                    <div class="registry-section-head">
                        <h2>Integration Readiness</h2>
                        <p>{escape(readiness.get("reason", ""))}</p>
                    </div>

                    <div class="registry-readiness-list">
                        <p>Access Home v2: {escape(str(readiness.get("tower_access_home_v2")))}</p>
                        <p>Owner Console v1: {escape(str(readiness.get("tower_owner_console_v1")))}</p>
                        <p>OB simplification: {escape(str(readiness.get("observatory_simplification")))}</p>
                        <p>Tower-OB integration: {escape(str(readiness.get("tower_ob_integration_branch")))}</p>
                        <p>Render staging redeploy: {escape(str(readiness.get("render_staging_redeploy")))}</p>
                    </div>
                </section>

                <section class="registry-section registry-panel">
                    <div class="registry-section-head">
                        <h2>Registry Evidence Drawers</h2>
                        <p>
                            Evidence stays available, but this page remains
                            a door map — not a proof wall.
                        </p>
                    </div>

                    {evidence_html}
                </section>

                <footer class="registry-footer">
                    Tower App Registry · payload
                    {escape(str(payload.get("payload_hash", ""))[:14])}
                </footer>
            </section>
        </main>
    </body>
    </html>
    """


def _render_door_card(door: Mapping[str, Any]) -> str:
    return f"""
    <article class="registry-door-card" id="{escape(door.get("id", ""))}">
        <div class="registry-card-top">
            <span>{escape(door.get("status", ""))}</span>
            <strong>{escape(door.get("door_state", ""))}</strong>
        </div>

        <h3>{escape(door.get("name", ""))}</h3>
        <p class="registry-subtitle">
            {escape(door.get("stone_role", ""))}
        </p>
        <p>{escape(door.get("purpose", ""))}</p>

        <div class="registry-door-meta">
            <p><b>Launch:</b> {escape(door.get("launch_route", ""))}</p>
            <p><b>Return:</b> {escape(door.get("return_route", ""))}</p>
            <p><b>Boundary:</b> {escape(door.get("permission_boundary", ""))}</p>
            <p><b>Owner controls:</b> {escape(door.get("owner_controls_route", ""))}</p>
            <p><b>Integration:</b> {escape(door.get("integration_status", ""))}</p>
        </div>

        <a class="registry-button" href="{escape(door.get("launch_route", "#"))}">
            {escape(door.get("primary_action", "Open"))}
        </a>
    </article>
    """


def _registry_css() -> str:
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
    }

    * {
        box-sizing: border-box;
    }

    body {
        margin: 0;
        min-height: 100vh;
        background:
            radial-gradient(
                circle at 12% 14%,
                rgba(125, 79, 214, .20),
                transparent 34%
            ),
            radial-gradient(
                circle at 84% 20%,
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

    .registry-shell {
        display: grid;
        grid-template-columns: 280px minmax(0, 1fr);
        min-height: 100vh;
    }

    .registry-rail {
        padding: 30px 22px;
        border-right: 1px solid var(--line);
        background: rgba(10, 8, 18, .88);
        position: sticky;
        top: 0;
        height: 100vh;
    }

    .registry-back {
        display: block;
        margin-bottom: 10px;
        color: var(--muted);
        text-decoration: none;
        font-weight: 850;
    }

    .registry-mark {
        width: 62px;
        height: 62px;
        border-radius: 20px;
        display: grid;
        place-items: center;
        margin: 22px 0 18px;
        color: #201307;
        font-size: 1.2rem;
        font-weight: 950;
        background:
            linear-gradient(135deg, var(--gold), #fff1b7);
        box-shadow:
            0 0 26px rgba(244, 210, 123, .22),
            inset 0 0 14px rgba(255,255,255,.42);
    }

    .registry-overline {
        color: var(--gold);
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .74rem;
        font-weight: 850;
    }

    .registry-rail h1 {
        font-size: 2.2rem;
        margin: 8px 0 10px;
        letter-spacing: -.04em;
    }

    .registry-rail p,
    .registry-main p {
        color: var(--muted);
        line-height: 1.58;
    }

    .registry-rail-panel,
    .registry-hero,
    .registry-hero-card,
    .registry-stat,
    .registry-door-card,
    .registry-panel,
    .registry-detail {
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

    .registry-rail-panel {
        display: grid;
        gap: 6px;
        padding: 16px;
        border-radius: 18px;
        margin-top: 24px;
    }

    .registry-rail-panel span,
    .registry-stat span,
    .registry-card-top span,
    .registry-hero-card span {
        color: var(--dim);
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .11em;
        font-weight: 850;
    }

    .registry-main {
        padding: 34px;
    }

    .registry-hero {
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

    .registry-hero h2 {
        font-size: clamp(2.4rem, 5vw, 5.2rem);
        line-height: .94;
        letter-spacing: -.06em;
        margin: 10px 0 12px;
    }

    .registry-hero-card {
        border-radius: 24px;
        padding: 22px;
        display: grid;
        gap: 8px;
    }

    .registry-grid.status {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 16px;
        margin: 18px 0 28px;
    }

    .registry-stat,
    .registry-panel,
    .registry-door-card {
        border-radius: 24px;
        padding: 22px;
    }

    .registry-stat strong {
        display: block;
        margin-top: 8px;
        font-size: 1.15rem;
    }

    .registry-section {
        margin-top: 28px;
    }

    .registry-section-head {
        margin-bottom: 16px;
    }

    .registry-section h2,
    .registry-panel h2 {
        margin: 0 0 6px;
        font-size: 1.6rem;
    }

    .registry-door-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
    }

    .registry-card-top {
        display: flex;
        justify-content: space-between;
        gap: 12px;
        margin-bottom: 12px;
    }

    .registry-door-card h3 {
        margin: 8px 0 8px;
        font-size: 1.35rem;
    }

    .registry-subtitle {
        color: var(--gold) !important;
        margin-top: 0;
        font-weight: 800;
    }

    .registry-door-meta {
        margin: 14px 0 16px;
    }

    .registry-door-meta p {
        margin: 7px 0;
        font-size: .94rem;
    }

    .registry-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        width: fit-content;
        padding: 0 16px;
        border-radius: 999px;
        background:
            linear-gradient(135deg, var(--gold), #fff2bd);
        color: #1a1109;
        text-decoration: none;
        font-weight: 900;
    }

    .registry-detail {
        border-radius: 16px;
        padding: 15px 16px;
        margin-top: 10px;
    }

    .registry-detail summary {
        color: var(--gold);
        cursor: pointer;
        font-weight: 850;
    }

    .registry-footer {
        color: var(--dim);
        margin: 30px 0 4px;
        font-size: .9rem;
    }

    @media (max-width: 980px) {
        .registry-shell,
        .registry-hero,
        .registry-grid.status {
            grid-template-columns: 1fr;
        }

        .registry-rail {
            position: relative;
            height: auto;
        }

        .registry-main {
            padding: 20px;
        }
    }
    </style>
    """


def build_app_registry_cert(pack: int) -> Dict[str, Any]:
    if pack not in PACK_NAMES:
        raise ValueError(f"Unsupported app registry pack: {pack}")

    readiness_key = READINESS_KEYS[pack]
    contract = app_registry_contract()

    payload = {
        "pack": str(pack),
        "pack_name": PACK_NAMES[pack],
        "status": "ready",
        "readiness": 100,
        "tower_app_registry_v2": True,
        "ecosystem_door_registry": True,
        "tower_source_of_truth_for_app_doors": True,
        readiness_key: True,
        "ecosystem_doors_registered": True,
        "door_card_metadata_model": True,
        "door_status_readiness_model": True,
        "door_permission_boundary_model": True,
        "door_launch_route_map": True,
        "door_owner_control_linkage": True,
        "door_integration_readiness_view": True,
        "door_evidence_drawers": True,
        "registry_cert_routes": True,
        "registered_door_ids": [door["id"] for door in DOORS],
        "registered_door_count": len(DOORS),
        "observatory_registered": True,
        "vault_registered": True,
        "teller_registered": True,
        "grounds_registered": True,
        "clouds_registered": True,
        "owner_controls_route": "/tower/owner-console",
        "access_home_route": "/tower/access-home",
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
