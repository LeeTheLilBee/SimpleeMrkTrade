"""Authenticated Tower launch gates for Grounds and BuyBox.

These routes deliberately separate *a real Tower doorway* from *a released
product runtime*. Registration of /tower/launch/<app> never manufactures a
receiver, storage proof, publication, entitlement, or browser bootstrap.

Grounds can cross only when its same-origin WSGI route is actually mounted and
both independent Tower runtime/release providers are healthy. BuyBox can reach
READY_FOR_BOOTSTRAP only when Tower's signed-owner-handoff preflight is green;
actual browser bootstrap remains blocked until BuyBox publishes a reviewed
same-origin token bootstrap transport compatible with POST /tower/owner-exchange.
"""
from __future__ import annotations

from datetime import timedelta
from html import escape
from typing import Any, Mapping

from flask import Flask, jsonify, redirect, request, session
from werkzeug.exceptions import HTTPException

from tower.app_truth_projection import app_truth_by_id
from tower.buybox_owner_handoff_issuer import inspect_current_buybox_issue_preflight
from tower.ecosystem_direct_route_guard import (
    ACCESS_RECEIPT_KEYS,
    build_ecosystem_access_receipt,
)
from tower.tower_human_login_ob_launch import (
    ACCESS_HOME_PATH,
    SESSION_AUTHENTICATED,
    SESSION_ID,
    SESSION_OWNER_ID,
    SESSION_ROLE,
    SESSION_STEP_UP_UNTIL,
    SESSION_USERNAME,
    configured_step_up_minutes,
    ensure_tower_session_id,
    page,
    require_human_owner,
    step_up_active,
    utc_now,
    verify_owner_credentials,
)

GROUNDS_LAUNCH_PATH = "/tower/launch/grounds"
BUYBOX_LAUNCH_PATH = "/tower/launch/buybox"
ECOSYSTEM_STEP_UP_PATH = "/tower/step-up/ecosystem"
GROUNDS_STATUS_PATH = "/tower/launch/grounds.json"
BUYBOX_STATUS_PATH = "/tower/launch/buybox.json"

_ALLOWED_APPS = {
    "grounds": GROUNDS_LAUNCH_PATH,
    "buybox": BUYBOX_LAUNCH_PATH,
}


def _session_context() -> dict[str, Any]:
    return {
        "authenticated": session.get(SESSION_AUTHENTICATED) is True,
        "role": session.get(SESSION_ROLE),
        "owner_id": session.get(SESSION_OWNER_ID),
        "tower_session_ref": ensure_tower_session_id(),
        "step_up_active": step_up_active(),
    }


def _grounds_runtime_health() -> tuple[bool, list[str]]:
    reasons: list[str] = []
    try:
        from tower.grounds_runtime_receiver import create_certified_grounds_receiver
        receiver = create_certified_grounds_receiver()
        health = getattr(receiver, "health_check", None)
        if not callable(health) or health() is not True:
            reasons.append("GROUNDS_RUNTIME_RECEIVER_NOT_HEALTHY")
    except Exception:
        reasons.append("GROUNDS_RUNTIME_RECEIVER_NOT_CERTIFIED")

    try:
        from tower.grounds_operational_release import (
            create_certified_grounds_operational_release_guard,
        )
        release = create_certified_grounds_operational_release_guard()
        health = getattr(release, "health_check", None)
        if not callable(health) or health() is not True:
            reasons.append("GROUNDS_OPERATIONAL_RELEASE_NOT_HEALTHY")
    except Exception:
        reasons.append("GROUNDS_OPERATIONAL_RELEASE_NOT_CERTIFIED")

    return not reasons, reasons


def _route_present(app: Flask, path: str) -> bool:
    return path in {rule.rule for rule in app.url_map.iter_rules()}


def inspect_grounds_launch(app: Flask, *, truth: Mapping[str, Any] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    current_truth = app_truth_by_id("grounds") if truth is None else truth
    if not isinstance(current_truth, Mapping) or current_truth.get("launchable") is not True:
        reasons.append("GROUNDS_PUBLICATION_ENTITLEMENT_OR_HEALTH_NOT_VERIFIED")

    # Grounds has no cross-origin browser handoff protocol. Until one exists,
    # only a same-origin mounted runtime can be safely launched.
    if not _route_present(app, "/grounds"):
        reasons.append("GROUNDS_SAME_ORIGIN_RUNTIME_NOT_MOUNTED")

    runtime_ready, runtime_reasons = _grounds_runtime_health()
    if not runtime_ready:
        reasons.extend(runtime_reasons)

    return {
        "schema_version": "tower.grounds.owner-launch-preflight.v1",
        "app_id": "grounds",
        "state": "READY_TO_LAUNCH" if not reasons else "BLOCKED",
        "reason_codes": reasons,
        "can_launch": not reasons,
        "target_path": "/grounds" if not reasons else None,
        "owner_session_required": True,
        "step_up_required": True,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "payment_execution_authorized": False,
    }


def inspect_buybox_launch(*, truth: Mapping[str, Any] | None = None) -> dict[str, Any]:
    current_truth = app_truth_by_id("buybox") if truth is None else truth
    preflight = inspect_current_buybox_issue_preflight(
        session_context=_session_context(),
        app_truth=current_truth,
    )
    reasons = list(preflight.get("reason_codes", []))

    # The BuyBox receiver intentionally accepts only a same-origin POST body.
    # No reviewed BuyBox bootstrap page currently transports Tower's short-lived
    # handoff into that same-origin POST, so Tower must not leak it via query,
    # cross-origin form, localStorage, cookie, or an invented endpoint.
    reasons.append("BUYBOX_BROWSER_BOOTSTRAP_NOT_IMPLEMENTED")

    return {
        "schema_version": "tower.buybox.owner-launch-preflight.v1",
        "app_id": "buybox",
        "state": "BLOCKED",
        "reason_codes": list(dict.fromkeys(reasons)),
        "can_launch": False,
        "tower_handoff_preflight_ready": preflight.get("can_issue_handoff") is True,
        "receiver_contract": "POST /tower/owner-exchange",
        "browser_bootstrap_transport_ready": False,
        "owner_session_required": True,
        "step_up_required": True,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "closing_authorized": False,
        "vault_access_authorized": False,
    }


def _blocked_page(title: str, report: Mapping[str, Any], *, status_code: int = 503):
    items = "".join(
        "<li><code>" + escape(str(code)) + "</code></li>"
        for code in report.get("reason_codes", [])
    )
    html = f"""
    <section class="hero">
      <h1>{escape(title)} is not released yet</h1>
      <p>Tower authenticated the doorway, but the product crossing remains fail-closed until every independent runtime gate is verified.</p>
    </section>
    <section class="card">
      <h2>Current blockers</h2>
      <ul>{items or '<li>No safe launch evidence was returned.</li>'}</ul>
      <div class="actions">
        <a class="button secondary" href="{ACCESS_HOME_PATH}">Return to Tower</a>
        <a class="button secondary" href="/tower/integrations">Integration Desk</a>
      </div>
    </section>
    """
    return page(title=f"{title} launch blocked", content=html), status_code


def _step_up_redirect(app_id: str):
    return redirect(
        ECOSYSTEM_STEP_UP_PATH
        + "?app="
        + app_id
    )


def grounds_launch_view(app: Flask):
    if not step_up_active():
        return _step_up_redirect("grounds")
    report = inspect_grounds_launch(app)
    if report["can_launch"] is not True:
        return _blocked_page("The Grounds", report)
    # The generic direct-route guard still requires a Tower-created,
    # current-session receipt even after product-specific readiness succeeds.
    # Normalize a still-valid pre-upgrade owner session before binding receipt.
    if not ensure_tower_session_id():
        return _blocked_page(
            "The Grounds",
            {"reason_codes": ["CURRENT_TOWER_SESSION_BINDING_REQUIRED"]},
        )
    session[ACCESS_RECEIPT_KEYS["grounds"]] = build_ecosystem_access_receipt("grounds")
    return redirect("/grounds")


def buybox_launch_view():
    if not step_up_active():
        return _step_up_redirect("buybox")
    report = inspect_buybox_launch()
    # Do not issue a signed bearer handoff until the receiver-side same-origin
    # bootstrap is implemented and reviewed.
    return _blocked_page("BuyBox", report)


def _status_response(report: Mapping[str, Any]):
    response = jsonify(dict(report))
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["Vary"] = "Cookie"
    return response


def grounds_status_view(app: Flask):
    if not step_up_active():
        return _status_response({
            "schema_version": "tower.grounds.owner-launch-preflight.v1",
            "app_id": "grounds",
            "state": "BLOCKED",
            "reason_codes": ["CURRENT_TOWER_OWNER_STEP_UP_REQUIRED"],
            "can_launch": False,
        }), 403
    return _status_response(inspect_grounds_launch(app))


def buybox_status_view():
    if not step_up_active():
        return _status_response({
            "schema_version": "tower.buybox.owner-launch-preflight.v1",
            "app_id": "buybox",
            "state": "BLOCKED",
            "reason_codes": ["CURRENT_TOWER_OWNER_STEP_UP_REQUIRED"],
            "can_launch": False,
        }), 403
    return _status_response(inspect_buybox_launch())


def ecosystem_step_up_view():
    app_id = str(request.values.get("app", "") or "").strip()
    if app_id not in _ALLOWED_APPS:
        return _blocked_page(
            "Ecosystem",
            {"reason_codes": ["UNKNOWN_OR_UNREVIEWED_APP_LAUNCH"]},
            status_code=404,
        )

    error = ""
    if request.method == "POST":
        username = str(session.get(SESSION_USERNAME, "") or "").strip()
        password = request.form.get("password", "")
        if verify_owner_credentials(username=username, password=password):
            session[SESSION_STEP_UP_UNTIL] = (
                utc_now() + timedelta(minutes=configured_step_up_minutes())
            ).isoformat()
            return redirect(_ALLOWED_APPS[app_id])
        error = "Tower could not verify the step-up password."

    error_html = (
        '<div class="notice danger">' + escape(error) + "</div>"
        if error else ""
    )
    return page(
        title="Tower Ecosystem Step-Up",
        content=f"""
        <section class="hero">
          <h1>Confirm It Is You</h1>
          <p>Re-enter your Tower password before opening {escape(app_id.title())}.</p>
        </section>
        <section class="card">
          {error_html}
          <form method="post">
            <input type="hidden" name="app" value="{escape(app_id)}">
            <label for="password">Owner password</label>
            <input id="password" name="password" type="password" autocomplete="current-password" required>
            <button type="submit">Verify</button>
          </form>
        </section>
        """,
    )


def register_ecosystem_owner_launch_gates(app: Flask) -> Flask:
    routes = (
        (GROUNDS_LAUNCH_PATH, "tower_grounds_owner_launch", lambda: grounds_launch_view(app), ["GET"]),
        (BUYBOX_LAUNCH_PATH, "tower_buybox_owner_launch", buybox_launch_view, ["GET"]),
        (GROUNDS_STATUS_PATH, "tower_grounds_owner_launch_status", lambda: grounds_status_view(app), ["GET"]),
        (BUYBOX_STATUS_PATH, "tower_buybox_owner_launch_status", buybox_status_view, ["GET"]),
        (ECOSYSTEM_STEP_UP_PATH, "tower_ecosystem_owner_step_up", ecosystem_step_up_view, ["GET", "POST"]),
    )
    for path, endpoint, view, methods in routes:
        if endpoint not in app.view_functions:
            app.add_url_rule(
                path,
                endpoint=endpoint,
                view_func=require_human_owner(view),
                methods=methods,
            )

    app.extensions["tower_ecosystem_owner_launch_gates_v1"] = {
        "grounds_launch_path": GROUNDS_LAUNCH_PATH,
        "buybox_launch_path": BUYBOX_LAUNCH_PATH,
        "grounds_runtime_must_be_same_origin": True,
        "buybox_browser_bootstrap_implemented": False,
        "unknown_apps_default_denied": True,
        "broker_submission_authorized": False,
        "capital_movement_authorized": False,
        "payment_execution_authorized": False,
    }
    return app
