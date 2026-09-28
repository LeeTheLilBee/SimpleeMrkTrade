"""Owner-only integration desk for the real Tower app registry.

An app source branch is not a live runtime. This page reports only the
canonical hosted Tower registry and its effective, independently projected
publication truth; missing providers always remain blocked. It cannot issue
handoffs, publish readiness receipts, or activate any service.
"""
from __future__ import annotations

from html import escape

from flask import Flask, jsonify, make_response

from tower.app_registry import registered_apps
from tower.app_truth_projection import app_truth_by_id
from tower.tower_human_login_ob_launch import page, require_human_owner

INTEGRATION_DESK_PATH = "/tower/integrations"
INTEGRATION_DESK_JSON_PATH = "/tower/integrations.json"

# Owner work plan, NOT asserted system evidence or credentials.
DEPENDENCIES = {
    "observatory": (
        "Actual owner browser return acceptance; durable production handoff ledger.",
    ),
    "teller": (
        "Current owner launch/return browser acceptance; authenticated Teller "
        "invoice, reconciliation and exact-deal readiness provider checks.",
    ),
    "grounds": (
        "Certified current Tower resident/staff owner receiver and exact "
        "lease/property/job grants; separate owner operational-release guard; "
        "approved private PostgreSQL/restore; Teller, Vault, delivery and "
        "legal/owner acceptance.",
    ),
    "buybox": (
        "Hosted owner/step-up issuer and revocable receiver; authenticated "
        "Teller deal/capacity, Tower-mediated Vault original/receipt and "
        "verified-close Grounds/ATM acceptance; owner-approved hosting.",
    ),
    "vault": (
        "Independent archival and recovery authorization, scanner/storage "
        "provider and signed original receipt; no registry-only storage launch.",
    ),
    "clouds": (
        "Authenticated source freshness, permission-minimized publishers "
        "and owner launch/return acceptance; never infer current data from "
        "a registered owner route.",
    ),
}

# Exact intended app IDs only; unknown apps fail closed rather than inheriting
# the Observatory or Teller route.
KNOWN_IDS = frozenset(DEPENDENCIES)


def _project_registered_app(app: dict) -> dict:
    app_id = app.get("app_id")
    if app_id not in KNOWN_IDS:
        return {
            "app_id": str(app_id or "unknown")[:80],
            "state": "BLOCKED_UNREVIEWED_APP",
            "launchable": False,
            "separate_product_runtime_activated": False,
            "owner_acceptance_verified": False,
            "required_next": "Owner/security review required.",
        }

    try:
        truth = app_truth_by_id(app_id)
    except Exception:
        truth = None
    launchable = bool(
        isinstance(truth, dict) and truth.get("launchable") is True
        and app.get("app_status") == "protected_hosted"
        and app.get("tower_launch_route", "").startswith("/tower/launch/")
    )
    # 'launchable' is a runtime projection, not a test of owner browser
    # completion and never enables an unregistered future app.
    return {
        "app_id": app_id,
        "label": app.get("app_name", app_id),
        "registry_state": app.get("app_status"),
        "state": "RUNTIME_LAUNCH_TRUTH_VERIFIED" if launchable else "BLOCKED_EXTERNAL_INTEGRATION",
        "tower_launch_route": app.get("tower_launch_route")
            if app.get("app_status") == "protected_hosted" else None,
        "launchable": launchable,
        "separate_product_runtime_activated": False if app_id in {
            "grounds", "buybox", "vault", "clouds",
        } else None,
        "owner_acceptance_verified": False,
        "required_next": " ".join(DEPENDENCIES[app_id]),
        "broker_submission": False,
        "capital_movement": False,
        "payroll_execution": False,
        "tenant_access": False,
    }


def integration_desk_snapshot() -> dict:
    return {
        "schema_version": "tower.ecosystem.integrations.owner.v1",
        "source": "canonical_hosted_app_registry_and_current_publication_truth",
        "note": "Runtime launch truth is not owner walkthrough or an external-provider certificate.",
        "systems": [_project_registered_app(app) for app in registered_apps()],
        "grants_issued": False,
        "external_calls_made": False,
        "owner_release_authorized": False,
        "paid_resources_provisioned": False,
    }


def _no_store(body, code=200):
    response = make_response(body, code)
    response.headers["Cache-Control"] = "no-store, private, max-age=0"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    return response


def _owner_integration_desk_page():
    snapshot = integration_desk_snapshot()
    cards = []
    for item in snapshot["systems"]:
        state = escape(item["state"])
        label = escape(str(item.get("label", item["app_id"])))
        required = escape(item["required_next"])
        launch = (
            '<a href="' + escape(item["tower_launch_route"], quote=True)
            + '">Open through Tower</a>'
            if item["launchable"] and item.get("tower_launch_route")
            else '<span aria-label="Launch blocked">Launch blocked — no permission issued</span>'
        )
        cards.append(
            '<article style="border:1px solid rgba(255,255,255,.15);'
            'border-radius:18px;background:rgba(255,255,255,.04);padding:18px">'
            '<h2>' + label + '</h2>'
            '<p><strong>' + state + '</strong></p><p>' + required + '</p>'
            '<p>' + launch + '</p></article>'
        )
    body = (
        '<section class="hero"><h1>Ecosystem Integration Desk</h1>'
        '<p>Source completion, publication truth and actual authorization are '
        'independent. Tower stays the only front door.</p></section>'
        '<section class="card"><p><a href="/tower/access-home">← Tower Access Home</a></p>'
        '<p>No new grants, releases, payments, storage access or trading modes are '
        'issued from this desk.</p></section>'
        '<section class="card" aria-label="System integration status" '
        'style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px">'
        + ''.join(cards) + '</section>'
    )
    return _no_store(page(title="Tower Ecosystem Integration Desk", content=body))


def _owner_integration_desk_json():
    return _no_store(jsonify(integration_desk_snapshot()))


def register_tower_integration_desk(app: Flask):
    if "tower_owner_integration_desk_v1" not in app.view_functions:
        app.add_url_rule(
            INTEGRATION_DESK_PATH,
            endpoint="tower_owner_integration_desk_v1",
            view_func=require_human_owner(_owner_integration_desk_page),
            methods=["GET"],
        )
    if "tower_owner_integration_desk_json_v1" not in app.view_functions:
        app.add_url_rule(
            INTEGRATION_DESK_JSON_PATH,
            endpoint="tower_owner_integration_desk_json_v1",
            view_func=require_human_owner(_owner_integration_desk_json),
            methods=["GET"],
        )
    return app
