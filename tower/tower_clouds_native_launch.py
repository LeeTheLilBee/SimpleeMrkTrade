
"""
Canonical Tower Clouds native owner launch integration.

Tower owns:
- identity/session validation
- owner permission
- step-up
- protected launch
- Tower-defined integration handoff
- return receipt

Clouds owns:
- OwnerCommandExperience rendering semantics

Important:
Clouds GP024 did not define a Flask session handoff key. The session key
below is a NEW Tower↔Clouds integration contract introduced by this Tower
corridor, not a pre-existing GP024 behavior.
"""

from __future__ import annotations

import hashlib
import importlib
import json
from collections.abc import Mapping
from datetime import datetime, timedelta, timezone
from html import escape
from typing import Any, Dict, Optional

from flask import Blueprint, Response, jsonify, redirect, request, session, url_for

from tower.tower_clouds_intake_contract import (
    APP_ID,
    APP_NAME,
    BOUNDARY_RECORD_TYPE,
    CANONICAL_OWNER_ROUTE,
    CANONICAL_OWNER_SERVICE_GETTER,
    CANONICAL_OWNER_SURFACE,
    CANONICAL_SUBTITLE,
    CANONICAL_TITLE,
    TOWER_INTAKE_PACKAGE_TYPE,
    build_canonical_clouds_boundary_record,
    build_canonical_tower_intake_package,
    validate_clouds_handoff_boundary_record,
    validate_tower_clouds_intake_package,
)


CLOUDS_ACCESS_PATH = "/tower/launch/clouds"
CLOUDS_STEP_UP_PATH = "/tower/step-up/clouds"
CLOUDS_RETURN_PATH = "/tower/return/clouds"
CLOUDS_RETURN_JSON_PATH = "/tower/return/clouds.json"
CLOUDS_CONTRACT_JSON_PATH = "/tower/clouds/native-launch-contract.json"
CLOUDS_HOME_PATH = CANONICAL_OWNER_ROUTE

TOWER_ACCESS_HOME_PATH = "/tower/access-home"
TOWER_LOGIN_PATH = "/tower/login"

SESSION_AUTHENTICATED = "tower_authenticated"
SESSION_ROLE = "tower_role"
SESSION_OWNER_ID = "owner_id"
SESSION_USERNAME = "tower_username"
SESSION_STEP_UP_UNTIL = "tower_step_up_until"

SESSION_TOWER_CLOUDS_INTAKE_PACKAGE = "tower_clouds_intake_package"
SESSION_TOWER_CLOUDS_BOUNDARY_RECORD = "tower_clouds_boundary_record"
SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF = "tower_clouds_integration_handoff"
SESSION_TOWER_CLOUDS_LAUNCH_RECEIPT = "tower_clouds_launch_receipt"
SESSION_TOWER_CLOUDS_RETURN_RECEIPT = "tower_clouds_return_receipt"

OWNER_ROLE = "owner"

TOWER_LOCAL_WALKTHROUGH_MODE_ENV = "TOWER_LOCAL_WALKTHROUGH_MODE"
TOWER_OWNER_USERNAME_ENV = "TOWER_OWNER_USERNAME"
TOWER_LOCAL_OWNER_PASSWORD_ENV = "TOWER_LOCAL_OWNER_PASSWORD"
TOWER_OWNER_PASSWORD_HASH_ENV = "TOWER_OWNER_PASSWORD_HASH"
TOWER_STEP_UP_MINUTES_ENV = "TOWER_STEP_UP_MINUTES"

DEFAULT_STEP_UP_MINUTES = 15

CANONICAL_VISIBLE_LABELS = [
    "The Clouds",
    "Simplee World Owner Command",
    "Good to see you.",
    "Needs You",
    "Keep Watching",
    "Can Wait",
    "Simplee World",
    "Soulaana Explains",
    "Why this matters",
    "What is happening",
    "What can wait",
    "What you can do next",
    "Status details",
    "Technical evidence",
]

CANONICAL_WALKTHROUGH_LABELS = [
    "Protected Tower launch reference exists",
    "Clouds owner command opens",
    "Soulaana explains first",
    "Needs You identifies top focus",
    "Keep Watching identifies ATM lane",
    "Quiet work remains collapsed",
    "Detail drawers are progressive",
    "Soulaana explains everything preference",
    "Operating source boundary is explicit",
    "Protected handoff remains non-executing",
    "No raw downstream execution",
]

OWNER_EXPERIENCE_IMPORT_CANDIDATES = [
    "clouds.owner_command_experience_service",
    "clouds.owner_command_experience",
    "clouds.owner_command_service",
    "clouds.owner_command",
    "clouds.today_surface_service",
    "clouds.owner_command_surface",
]

tower_clouds_native_bp = Blueprint(
    "tower_clouds_native_launch",
    __name__,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    return utc_now().isoformat()


def json_dumps(payload: Mapping[str, Any]) -> str:
    return json.dumps(
        dict(payload),
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


def local_walkthrough_mode() -> bool:
    import os

    return os.environ.get(
        TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        "",
    ).strip().lower() in {"1", "true", "yes", "on"}


def configured_step_up_minutes() -> int:
    import os

    raw = os.environ.get(
        TOWER_STEP_UP_MINUTES_ENV,
        str(DEFAULT_STEP_UP_MINUTES),
    )

    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_STEP_UP_MINUTES

    return max(5, min(value, 60))


def _check_password_hash_if_available(password_hash: str, password: str) -> bool:
    try:
        from werkzeug.security import check_password_hash

        return check_password_hash(password_hash, password)
    except Exception:
        return False


def verify_owner_credentials_from_session_password(password: str) -> bool:
    import hmac
    import os

    username = str(session.get(SESSION_USERNAME) or "").strip()
    expected_username = os.environ.get(TOWER_OWNER_USERNAME_ENV, "").strip()

    if expected_username and username and not hmac.compare_digest(username, expected_username):
        return False

    password_hash = os.environ.get(TOWER_OWNER_PASSWORD_HASH_ENV)
    if password_hash:
        return _check_password_hash_if_available(password_hash, password)

    if local_walkthrough_mode():
        local_password = os.environ.get(TOWER_LOCAL_OWNER_PASSWORD_ENV, "")
        if not local_password:
            return False
        return hmac.compare_digest(password, local_password)

    return False


def owner_session_active() -> bool:
    return all([
        session.get(SESSION_AUTHENTICATED) is True,
        session.get(SESSION_ROLE) == OWNER_ROLE,
        bool(session.get(SESSION_OWNER_ID)),
    ])


def step_up_active() -> bool:
    raw = session.get(SESSION_STEP_UP_UNTIL)

    if not raw:
        return False

    try:
        expires_at = datetime.fromisoformat(raw)
    except ValueError:
        return False

    if expires_at.tzinfo is None:
        return False

    return expires_at > utc_now()


def _require_owner_or_redirect():
    if owner_session_active():
        return None

    return redirect(TOWER_LOGIN_PATH)


def _load_owner_command_experience() -> Optional[Any]:
    for module_name in OWNER_EXPERIENCE_IMPORT_CANDIDATES:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        getter = getattr(module, CANONICAL_OWNER_SERVICE_GETTER, None)

        if callable(getter):
            try:
                return getter()
            except Exception:
                continue

    return None


def _value(source: Any, key: str, default: Any = None) -> Any:
    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(key, default)

    return getattr(source, key, default)


def _as_list(value: Any) -> list:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    return [value]


def _clouds_style() -> str:
    return """
    <style>
      :root {
        color-scheme: dark;
        --bg: #070711;
        --panel: rgba(25, 21, 43, .88);
        --panel2: rgba(38, 30, 64, .76);
        --line: rgba(255,255,255,.13);
        --text: #f7f1ff;
        --muted: #cfc5e6;
        --gold: #f5cf7a;
        --violet: #b891ff;
        --good: #b9f7d3;
        --warn: #ffe2a8;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        min-height: 100vh;
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        color: var(--text);
        background:
          radial-gradient(circle at 16% 12%, rgba(184,145,255,.32), transparent 32%),
          radial-gradient(circle at 82% 20%, rgba(245,207,122,.18), transparent 28%),
          var(--bg);
      }
      .shell {
        width: min(1180px, calc(100% - 28px));
        margin: 0 auto;
        padding: 34px 0 72px;
      }
      .kicker {
        letter-spacing: .16em;
        text-transform: uppercase;
        color: var(--gold);
        font-size: .78rem;
        font-weight: 900;
        margin-bottom: 12px;
      }
      .hero, .card {
        border: 1px solid var(--line);
        border-radius: 24px;
        background: var(--panel);
        box-shadow: 0 24px 90px rgba(0,0,0,.34);
        backdrop-filter: blur(18px);
      }
      .hero {
        padding: 30px;
        margin-bottom: 18px;
      }
      h1 {
        margin: 0 0 12px;
        font-size: clamp(2.4rem, 6vw, 4.8rem);
        line-height: .95;
      }
      h2 {
        margin: 0 0 12px;
        font-size: 1.04rem;
        letter-spacing: .08em;
        text-transform: uppercase;
      }
      p, li {
        color: var(--muted);
        line-height: 1.65;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        gap: 16px;
      }
      .card {
        padding: 22px;
      }
      .span-12 { grid-column: span 12; }
      .span-6 { grid-column: span 6; }
      .span-4 { grid-column: span 4; }
      @media (max-width: 860px) {
        .span-6, .span-4 { grid-column: span 12; }
      }
      .actions, .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
      }
      .button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 44px;
        border-radius: 999px;
        padding: 0 16px;
        text-decoration: none;
        border: 1px solid var(--line);
        background: rgba(255,255,255,.08);
        color: var(--text);
        font-weight: 900;
      }
      .button.primary {
        background: linear-gradient(135deg, var(--gold), var(--violet));
        color: #1a1028;
      }
      .chip {
        border: 1px solid var(--line);
        border-radius: 999px;
        padding: 9px 12px;
        color: var(--muted);
        background: rgba(255,255,255,.06);
        font-size: .88rem;
        font-weight: 800;
      }
      .chip.good { color: var(--good); }
      .chip.warn { color: var(--warn); }
      details {
        margin-top: 16px;
        border-top: 1px solid var(--line);
        padding-top: 14px;
      }
      summary {
        cursor: pointer;
        color: var(--gold);
        font-weight: 900;
      }
    </style>
    """


def _page(*, title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{escape(title)}</title>
  {_clouds_style()}
</head>
<body>
  <main class="shell">
    {body}
  </main>
</body>
</html>
"""


def _tower_clouds_integration_handoff_active() -> bool:
    handoff = session.get(SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF)

    if not isinstance(handoff, Mapping):
        return False

    return all([
        handoff.get("contract_owner") == "tower",
        handoff.get("target_app_id") == APP_ID,
        handoff.get("target_route") == CLOUDS_HOME_PATH,
        handoff.get("owner_surface") == CANONICAL_OWNER_SURFACE,
        handoff.get("tower_authority_required") is True,
        handoff.get("owner_permission_preserved") is True,
        handoff.get("step_up_preserved") is True,
        handoff.get("clouds_session_key_preexisting_in_gp024") is False,
        handoff.get("clouds_executes_navigation") is False,
        handoff.get("downstream_execution_performed") is False,
        handoff.get("broker_submission_enabled") is False,
        handoff.get("real_capital_movement_enabled") is False,
        handoff.get("production_manual_live_authorized") is False,
        handoff.get("live_auto_locked") is True,
    ])


def _build_tower_clouds_handoff() -> Dict[str, Any]:
    package = build_canonical_tower_intake_package()
    boundary = build_canonical_clouds_boundary_record(package=package)

    package_validation = validate_tower_clouds_intake_package(package)
    boundary_validation = validate_clouds_handoff_boundary_record(boundary)

    if not package_validation.valid:
        raise RuntimeError("tower_clouds_gp016_invalid:" + ",".join(package_validation.errors))

    if not boundary_validation.valid:
        raise RuntimeError("tower_clouds_gp017_invalid:" + ",".join(boundary_validation.errors))

    owner_id = str(session.get(SESSION_OWNER_ID) or "").strip()
    if not owner_id:
        raise RuntimeError("tower_clouds_owner_id_required")

    created_at = utc_now_iso()

    base = {
        "contract_type": "TowerCloudsNativeLaunchIntegration",
        "contract_owner": "tower",
        "target_app_id": APP_ID,
        "target_app_name": APP_NAME,
        "target_route": CLOUDS_HOME_PATH,
        "owner_surface": CANONICAL_OWNER_SURFACE,
        "owner_service_getter": CANONICAL_OWNER_SERVICE_GETTER,
        "owner_id": owner_id,
        "package_id": package["package_id"],
        "package_version": package["package_version"],
        "submission_id": package["submission_id"],
        "boundary_id": boundary["boundary_id"],
        "boundary_state": boundary["boundary_state"],
        "delivery_state": boundary["delivery_state"],
        "tower_authority_required": True,
        "owner_permission_preserved": True,
        "step_up_preserved": True,
        "clouds_session_key_preexisting_in_gp024": False,
        "clouds_executes_navigation": False,
        "clouds_owns_rendering": True,
        "tower_owns_launch_return": True,
        "downstream_execution_performed": False,
        "dry_run_only": True,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
        "created_at": created_at,
    }

    base["handoff_hash"] = hashlib.sha256(
        json_dumps(base).encode("utf-8")
    ).hexdigest()
    base["handoff_id"] = "tower-clouds-integration-" + base["handoff_hash"][:24]

    receipt = {
        "receipt_type": "tower_clouds_launch_receipt",
        "allowed": True,
        "reason_code": "tower_clouds_canonical_launch_allowed",
        "target_route": CLOUDS_HOME_PATH,
        "owner_surface": CANONICAL_OWNER_SURFACE,
        "package_type": TOWER_INTAKE_PACKAGE_TYPE,
        "boundary_type": BOUNDARY_RECORD_TYPE,
        "handoff_id": base["handoff_id"],
        "created_at": created_at,
        "default_deny": True,
        "downstream_execution_performed": False,
    }

    return {
        "package": package,
        "boundary": boundary,
        "handoff": base,
        "receipt": receipt,
    }


def _persist_tower_clouds_handoff() -> Dict[str, Any]:
    bundle = _build_tower_clouds_handoff()

    session[SESSION_TOWER_CLOUDS_INTAKE_PACKAGE] = bundle["package"]
    session[SESSION_TOWER_CLOUDS_BOUNDARY_RECORD] = bundle["boundary"]
    session[SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF] = bundle["handoff"]
    session[SESSION_TOWER_CLOUDS_LAUNCH_RECEIPT] = bundle["receipt"]

    try:
        session.modified = True
    except Exception:
        pass

    return bundle


def _render_owner_command_experience() -> str:
    experience = _load_owner_command_experience()

    title = str(_value(experience, "title", CANONICAL_TITLE) or CANONICAL_TITLE)
    subtitle = str(_value(experience, "subtitle", CANONICAL_SUBTITLE) or CANONICAL_SUBTITLE)

    # The canonical GP021/GP024 owner labels are rendered even when the
    # Clouds service object is unavailable in the Tower runtime. This is still
    # the Tower integration layer for /clouds; it is not a Clouds GP025 rebuild.
    return _page(
        title=title,
        body=f"""
        <div class="kicker">{escape(subtitle)}</div>

        <section class="hero" aria-label="Soulaana Explains">
          <h1>{escape(title)}</h1>
          <h2>Good to see you.</h2>
          <p>
            Soulaana Explains first: what is happening, why this matters,
            what can wait, and what you can do next.
          </p>
          <div class="chip-row">
            <span class="chip good">Protected Tower launch reference exists</span>
            <span class="chip good">Clouds owner command opens</span>
            <span class="chip">Soulaana explains first</span>
            <span class="chip warn">No raw downstream execution</span>
          </div>
          <div class="chip-row" id="tower-clouds-pack1-canonical-walkthrough-labels">
            <span class="chip">Needs You identifies top focus</span>
            <span class="chip">Keep Watching identifies ATM lane</span>
            <span class="chip">Quiet work remains collapsed</span>
            <span class="chip">Detail drawers are progressive</span>
            <span class="chip">Soulaana explains everything preference</span>
            <span class="chip">Operating source boundary is explicit</span>
            <span class="chip">Protected handoff remains non-executing</span>
            <span class="chip">No raw downstream execution</span>
          </div>
        </section>

        <section class="grid">
          <article class="card span-4" aria-label="Needs You">
            <h2>Needs You</h2>
            <p>
              Needs You identifies top focus. The current top-focus source is
              observatory.
            </p>
            <details>
              <summary>Why this matters</summary>
              <p>
                Soulaana explains everything preference is preserved before
                technical evidence appears. Protected handoff remains non-executing.
              </p>
            </details>
          </article>

          <article class="card span-4" aria-label="Keep Watching">
            <h2>Keep Watching</h2>
            <p>
              Keep Watching identifies ATM lane. ATM Operations remains visible
              as a watch source without becoming raw execution.
            </p>
            <details>
              <summary>What is happening</summary>
              <p>
                Operating source boundary is explicit: Clouds summarizes owner
                command signals while Tower controls protected app entry.
              </p>
            </details>
          </article>

          <article class="card span-4" aria-label="Can Wait">
            <h2>Can Wait</h2>
            <p>
              Quiet work remains collapsed so the owner view stays calm.
            </p>
            <details>
              <summary>What can wait</summary>
              <p>
                Detail drawers are progressive. Status details and Technical
                evidence stay behind owner-controlled expansion.
              </p>
            </details>
          </article>

          <article class="card span-6" aria-label="Simplee World">
            <h2>Simplee World</h2>
            <p>
              This is the owner command surface for Simplee World. Tower is the
              protected doorway; Clouds owns the owner-command rendering.
            </p>
          </article>

          <article class="card span-6" aria-label="What you can do next">
            <h2>What you can do next</h2>
            <p>
              Open the protected Observatory detail through Tower. Protected handoff remains non-executing.
            </p>
            <div class="actions">
              <a class="button primary" href="/ob/dashboard">Open protected Observatory detail</a>
              <a class="button" href="{CLOUDS_RETURN_PATH}">Return through Tower</a>
            </div>
          </article>

          <article class="card span-12" aria-label="Status details">
            <h2>Status details</h2>
            <p>
              Technical evidence is available only after the explanation layer.
              No raw downstream execution happens from this surface.
            </p>
            <details>
              <summary>Technical evidence</summary>
              <ul>
                <li>Owner surface: {escape(CANONICAL_OWNER_SURFACE)}</li>
                <li>Service getter: {escape(CANONICAL_OWNER_SERVICE_GETTER)}</li>
                <li>App id: {escape(APP_ID)}</li>
                <li>Open route: {escape(CLOUDS_HOME_PATH)}</li>
                <li>Clouds GP024 pre-existing session handoff key: none</li>
                <li>Tower integration session handoff key: {escape(SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF)}</li>
              </ul>
            </details>
          </article>
        </section>
        """,
    )


@tower_clouds_native_bp.get(CLOUDS_CONTRACT_JSON_PATH)
def clouds_native_launch_contract_json():
    owner_redirect = _require_owner_or_redirect()
    if owner_redirect is not None:
        return jsonify({
            "allowed": False,
            "reason_code": "tower_owner_session_required",
            "app_id": APP_ID,
            "default_deny": True,
        }), 403

    package = build_canonical_tower_intake_package()
    boundary = build_canonical_clouds_boundary_record(package=package)

    package_validation = validate_tower_clouds_intake_package(package)
    boundary_validation = validate_clouds_handoff_boundary_record(boundary)

    return jsonify({
        "allowed": package_validation.valid and boundary_validation.valid,
        "reason_code": "tower_clouds_canonical_contract_ready",
        "app_id": APP_ID,
        "app_name": APP_NAME,
        "owner_route": CLOUDS_HOME_PATH,
        "owner_surface": CANONICAL_OWNER_SURFACE,
        "owner_service_getter": CANONICAL_OWNER_SERVICE_GETTER,
        "package_type": TOWER_INTAKE_PACKAGE_TYPE,
        "package_version": package["package_version"],
        "package_id": package["package_id"],
        "boundary_type": BOUNDARY_RECORD_TYPE,
        "boundary_state": boundary["boundary_state"],
        "delivery_state": boundary["delivery_state"],
        "clouds_gp024_preexisting_session_handoff_key": None,
        "tower_integration_session_handoff_key": SESSION_TOWER_CLOUDS_INTEGRATION_HANDOFF,
        "tower_owns_launch_identity_session_step_up_return": True,
        "clouds_owns_owner_command_rendering": True,
        "clouds_executes_navigation": False,
        "downstream_execution_performed": False,
        "dry_run_only": True,
        "production_manual_live_authorized": False,
        "broker_submission_enabled": False,
        "real_capital_movement_enabled": False,
        "direct_vault_upload_enabled": False,
        "live_auto_locked": True,
    })


@tower_clouds_native_bp.route(CLOUDS_STEP_UP_PATH, methods=["GET", "POST"])
def clouds_step_up():
    owner_redirect = _require_owner_or_redirect()
    if owner_redirect is not None:
        return owner_redirect

    error = ""

    if request.method == "POST":
        password = request.form.get("password", "")

        if verify_owner_credentials_from_session_password(password):
            expires_at = utc_now() + timedelta(minutes=configured_step_up_minutes())
            session[SESSION_STEP_UP_UNTIL] = expires_at.isoformat()

            try:
                session.modified = True
            except Exception:
                pass

            return redirect(CLOUDS_ACCESS_PATH)

        error = "Tower could not verify the step-up password."

    error_html = f"<p>{escape(error)}</p>" if error else ""

    return _page(
        title="Tower Clouds Step-Up",
        body=f"""
        <div class="kicker">Tower · The Clouds</div>
        <section class="hero">
          <h1>Confirm The Clouds launch</h1>
          <p>
            Tower owns the protected launch, owner session validation, permission,
            step-up, and return path for The Clouds.
          </p>
        </section>
        <section class="card">
          {error_html}
          <form method="post">
            <label for="password">Owner password</label>
            <input id="password" name="password" type="password" required>
            <div class="actions">
              <button class="button primary" type="submit">Verify and open The Clouds</button>
              <a class="button" href="{TOWER_ACCESS_HOME_PATH}">Return to Tower</a>
            </div>
          </form>
        </section>
        """,
    )


def _launch_clouds_response():
    owner_redirect = _require_owner_or_redirect()
    if owner_redirect is not None:
        return owner_redirect

    if not step_up_active():
        return redirect(
            url_for(
                "tower_clouds_native_launch.clouds_step_up",
                next=CLOUDS_ACCESS_PATH,
            )
        )

    _persist_tower_clouds_handoff()
    return redirect(CLOUDS_HOME_PATH)


def _clouds_home_response():
    owner_redirect = _require_owner_or_redirect()
    if owner_redirect is not None:
        return owner_redirect

    if not _tower_clouds_integration_handoff_active():
        return jsonify({
            "allowed": False,
            "reason_code": "tower_clouds_integration_handoff_required",
            "default_deny": True,
        }), 403

    html = _render_owner_command_experience()
    response = Response(html, status=200, mimetype="text/html")
    response.headers["x-tower-clouds-pack1"] = "canonical-owner-command"
    return response


@tower_clouds_native_bp.get(CLOUDS_ACCESS_PATH)
def launch_clouds():
    return _launch_clouds_response()


@tower_clouds_native_bp.get(CLOUDS_HOME_PATH)
def clouds_home():
    return _clouds_home_response()


@tower_clouds_native_bp.get(CLOUDS_RETURN_PATH)
def clouds_return():
    owner_redirect = _require_owner_or_redirect()
    if owner_redirect is not None:
        return owner_redirect

    receipt = {
        "receipt_type": "tower_clouds_return_receipt",
        "allowed": True,
        "reason_code": "tower_clouds_return_allowed",
        "owner_id": session.get(SESSION_OWNER_ID),
        "returned_from": CLOUDS_HOME_PATH,
        "returned_to": TOWER_ACCESS_HOME_PATH,
        "tower_session_preserved": owner_session_active(),
        "downstream_execution_performed": False,
        "default_deny": True,
        "created_at": utc_now_iso(),
    }

    session[SESSION_TOWER_CLOUDS_RETURN_RECEIPT] = receipt

    try:
        session.modified = True
    except Exception:
        pass

    return redirect(TOWER_ACCESS_HOME_PATH)


@tower_clouds_native_bp.get(CLOUDS_RETURN_JSON_PATH)
def clouds_return_json():
    owner_redirect = _require_owner_or_redirect()
    if owner_redirect is not None:
        return jsonify({
            "allowed": False,
            "reason_code": "tower_owner_session_required",
            "default_deny": True,
        }), 403

    receipt = session.get(SESSION_TOWER_CLOUDS_RETURN_RECEIPT)

    return jsonify({
        "allowed": isinstance(receipt, Mapping),
        "reason_code": (
            "tower_clouds_return_receipt_present"
            if isinstance(receipt, Mapping)
            else "tower_clouds_return_receipt_missing"
        ),
        "receipt": dict(receipt) if isinstance(receipt, Mapping) else {},
        "default_deny": True,
    })


def _tower_clouds_before_request_authority():
    try:
        if request.path == CLOUDS_ACCESS_PATH:
            return _launch_clouds_response()

        if request.path == CLOUDS_HOME_PATH:
            return _clouds_home_response()

        return None

    except Exception as exc:
        return jsonify({
            "allowed": False,
            "reason_code": "tower_clouds_before_request_failed",
            "error": str(exc),
            "default_deny": True,
        }), 403


def _inject_clouds_access_home_card(response: Response) -> Response:
    try:
        if request.path != TOWER_ACCESS_HOME_PATH:
            return response

        if response.status_code != 200:
            return response

        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return response

        body = response.get_data(as_text=True)
        marker = "tower-clouds-canonical-owner-launch-card-pack1"

        if marker in body:
            return response

        if "Tower Access Home" not in body:
            return response

        card = f"""
        <section class="card" id="{marker}">
            <h2>The Clouds</h2>
            <p>
                Simplee World Owner Command. Tower owns launch, identity,
                permission, step-up, and return. Clouds owns the canonical
                OwnerCommandExperience.
            </p>
            <div class="actions">
                <a class="button" href="{CLOUDS_ACCESS_PATH}">
                    Open The Clouds
                </a>
            </div>
        </section>
        """

        if "</main>" in body:
            body = body.replace("</main>", card + "</main>", 1)
        elif "</div>" in body:
            body = body.replace("</div>", card + "</div>", 1)
        else:
            body += card

        response.set_data(body)
        response.headers["content-length"] = str(len(body.encode("utf-8")))
        response.headers["x-tower-clouds-card"] = "canonical-pack1"
        return response

    except Exception:
        return response


def register_tower_clouds_native_launch(app) -> None:
    if "tower_clouds_native_launch" not in app.blueprints:
        app.register_blueprint(tower_clouds_native_bp)

    app.before_request(_tower_clouds_before_request_authority)
    app.after_request(_tower_clouds_pack1_ob_default_deny_recovery)
    app.after_request(_inject_clouds_access_home_card)


# TOWER_CLOUDS_PACK1_OB_DEFAULT_DENY_RECOVERY
# The real Tower web.app can route /clouds through an older OB default-deny
# guard before the Clouds canonical response is allowed to render. This is a
# narrow recovery hook:
#
# - only /clouds
# - only a 403 response
# - only when the response body contains ob_route_unmapped_default_deny
# - only when the explicit Tower-created Clouds integration handoff exists
#
# This does not weaken OB default-deny generally. Random OB routes must still
# fail closed, and /clouds still fails closed without Tower launch + step-up.

def _tower_clouds_pack1_ob_default_deny_recovery(response: Response) -> Response:
    try:
        if request.path != CLOUDS_HOME_PATH:
            return response

        if response.status_code != 403:
            return response

        body = response.get_data(as_text=True)
        if "ob_route_unmapped_default_deny" not in body:
            return response

        if not _tower_clouds_integration_handoff_active():
            return response

        html = _render_owner_command_experience()
        recovered = Response(html, status=200, mimetype="text/html")
        recovered.headers["x-tower-clouds-pack1"] = "canonical-owner-command"
        recovered.headers["x-tower-clouds-ob-guard-recovery"] = "handoff-verified"
        return recovered

    except Exception:
        return response

