"""
Real human Tower login and protected Observatory launch.

No passwords or session secrets are stored in this module.
Credentials must be supplied through environment variables.
"""

from __future__ import annotations

from collections.abc import Mapping

from tower.tower_ob_gp046_native_contract import build_native_gp046_handoff

import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps
from html import escape
from typing import Any, Dict
from urllib.parse import urlparse

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash


TOWER_OWNER_USERNAME_ENV = (
    "TOWER_OWNER_USERNAME"
)

TOWER_OWNER_PASSWORD_HASH_ENV = (
    "TOWER_OWNER_PASSWORD_HASH"
)

TOWER_LOCAL_OWNER_PASSWORD_ENV = (
    "TOWER_LOCAL_OWNER_PASSWORD"
)

TOWER_LOCAL_WALKTHROUGH_MODE_ENV = (
    "TOWER_LOCAL_WALKTHROUGH_MODE"
)

TOWER_SESSION_SECRET_ENV = (
    "TOWER_SESSION_SECRET"
)

TOWER_OWNER_ID_ENV = (
    "TOWER_OWNER_ID"
)

TOWER_STEP_UP_MINUTES_ENV = (
    "TOWER_STEP_UP_MINUTES"
)

DEFAULT_OWNER_USERNAME = "owner"
DEFAULT_OWNER_ID = "simplee_owner"
DEFAULT_STEP_UP_MINUTES = 15

OBSERVATORY_WALKTHROUGH_PATH = (
    "/tower/observatory-walkthrough"
)

LOGIN_PATH = "/tower/login"
START_PATH = "/tower/start"
ACCESS_HOME_PATH = "/tower/access-home"
OBSERVATORY_LAUNCH_PATH = (
    "/tower/launch/observatory"
)
OBSERVATORY_STEP_UP_PATH = (
    "/tower/step-up/observatory"
)
LOGOUT_PATH = "/tower/logout"

SESSION_AUTHENTICATED = (
    "tower_authenticated"
)
SESSION_ROLE = "tower_role"
SESSION_OWNER_ID = "owner_id"
SESSION_USERNAME = "tower_username"
SESSION_AUTH_TIME = "tower_authenticated_at"
SESSION_STEP_UP_UNTIL = (
    "tower_step_up_until"
)
SESSION_OB_LAUNCH_RECEIPT = (
    "tower_ob_launch_receipt"
)

SESSION_OB_NATIVE_LAUNCH_HANDOFF = 'tower_ob_native_launch_handoff'

OWNER_ROLE = "owner"

tower_human_login_bp = Blueprint(
    "tower_human_login",
    __name__,
)


BASE_STYLE = """
<style>
:root {
    color-scheme: dark;
    --bg: #080813;
    --panel: rgba(28, 23, 47, 0.88);
    --panel-2: rgba(44, 35, 71, 0.82);
    --text: #f7f4ff;
    --muted: #bdb5d5;
    --line: rgba(255,255,255,.12);
    --accent: #d7b8ff;
    --accent-2: #f4d6ff;
    --danger: #ffb5c0;
    --good: #bdf6d2;
}
* {
    box-sizing: border-box;
}
body {
    margin: 0;
    min-height: 100vh;
    font-family:
        Inter, ui-sans-serif, system-ui,
        -apple-system, BlinkMacSystemFont,
        "Segoe UI", sans-serif;
    background:
        radial-gradient(
            circle at 20% 10%,
            rgba(117, 80, 171, .34),
            transparent 36%
        ),
        radial-gradient(
            circle at 85% 25%,
            rgba(89, 47, 136, .28),
            transparent 32%
        ),
        var(--bg);
    color: var(--text);
}
.shell {
    width: min(1080px, calc(100% - 32px));
    margin: 0 auto;
    padding: 48px 0 72px;
}
.brand {
    letter-spacing: .16em;
    text-transform: uppercase;
    font-size: .78rem;
    color: var(--muted);
    margin-bottom: 16px;
}
.hero,
.card {
    border: 1px solid var(--line);
    border-radius: 22px;
    background: var(--panel);
    backdrop-filter: blur(18px);
    box-shadow: 0 24px 80px rgba(0,0,0,.28);
}
.hero {
    padding: 32px;
    margin-bottom: 22px;
}
.card {
    padding: 26px;
}
.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(260px, 1fr));
    gap: 18px;
}
h1 {
    margin: 0 0 12px;
    font-size: clamp(2rem, 6vw, 4.2rem);
    line-height: .98;
}
h2 {
    margin-top: 0;
}
p,
li {
    color: var(--muted);
    line-height: 1.65;
}
label {
    display: block;
    margin-bottom: 8px;
    font-weight: 700;
}
input {
    width: 100%;
    padding: 14px 16px;
    border-radius: 12px;
    border: 1px solid var(--line);
    background: rgba(255,255,255,.055);
    color: var(--text);
    margin-bottom: 18px;
}
button,
.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 46px;
    padding: 0 20px;
    border: 0;
    border-radius: 999px;
    background: linear-gradient(
        135deg,
        var(--accent),
        var(--accent-2)
    );
    color: #1a1028;
    text-decoration: none;
    font-weight: 800;
    cursor: pointer;
}
.button.secondary {
    color: var(--text);
    background: rgba(255,255,255,.09);
    border: 1px solid var(--line);
}
.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 22px;
}
.notice {
    padding: 14px 16px;
    border-radius: 12px;
    margin-bottom: 18px;
    background: rgba(255,255,255,.07);
    border: 1px solid var(--line);
}
.notice.danger {
    color: var(--danger);
}
.notice.good {
    color: var(--good);
}
.meta {
    display: grid;
    gap: 10px;
    color: var(--muted);
}
code {
    color: var(--accent-2);
}
</style>
"""


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


def local_walkthrough_mode() -> bool:
    return os.environ.get(
        TOWER_LOCAL_WALKTHROUGH_MODE_ENV,
        "",
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def configured_owner_username() -> str:
    value = os.environ.get(
        TOWER_OWNER_USERNAME_ENV,
        "",
    ).strip()

    if value:
        return value

    if local_walkthrough_mode():
        return DEFAULT_OWNER_USERNAME

    return ""


def configured_owner_id() -> str:
    return (
        os.environ.get(
            TOWER_OWNER_ID_ENV,
            DEFAULT_OWNER_ID,
        ).strip()
        or DEFAULT_OWNER_ID
    )


def configured_step_up_minutes() -> int:
    raw = os.environ.get(
        TOWER_STEP_UP_MINUTES_ENV,
        str(
            DEFAULT_STEP_UP_MINUTES
        ),
    )

    try:
        value = int(raw)
    except ValueError:
        return DEFAULT_STEP_UP_MINUTES

    return max(
        5,
        min(
            value,
            60,
        ),
    )


def authentication_config_status() -> Dict[str, Any]:
    username = configured_owner_username()

    password_hash_present = bool(
        os.environ.get(
            TOWER_OWNER_PASSWORD_HASH_ENV
        )
    )

    local_password_present = bool(
        os.environ.get(
            TOWER_LOCAL_OWNER_PASSWORD_ENV
        )
    )

    local_mode = (
        local_walkthrough_mode()
    )

    credential_ready = bool(
        username
        and (
            password_hash_present
            or (
                local_mode
                and local_password_present
            )
        )
    )

    return {
        "ready": credential_ready,
        "username_present": bool(
            username
        ),
        "password_hash_present": (
            password_hash_present
        ),
        "local_password_present": (
            local_password_present
        ),
        "local_walkthrough_mode": (
            local_mode
        ),
        "session_secret_present": bool(
            os.environ.get(
                TOWER_SESSION_SECRET_ENV
            )
            or current_app.secret_key
        ),
        "credentials_committed": False,
        "default_deny": True,
    }


def verify_owner_credentials(
    *,
    username: str,
    password: str,
) -> bool:
    expected_username = (
        configured_owner_username()
    )

    if not expected_username:
        return False

    if not hmac.compare_digest(
        username,
        expected_username,
    ):
        return False

    password_hash = os.environ.get(
        TOWER_OWNER_PASSWORD_HASH_ENV
    )

    if password_hash:
        try:
            return check_password_hash(
                password_hash,
                password,
            )
        except ValueError:
            return False

    if local_walkthrough_mode():
        local_password = os.environ.get(
            TOWER_LOCAL_OWNER_PASSWORD_ENV,
            "",
        )

        if not local_password:
            return False

        return hmac.compare_digest(
            password,
            local_password,
        )

    return False


def safe_next_path(
    candidate: str | None,
    fallback: str,
) -> str:
    if not candidate:
        return fallback

    parsed = urlparse(
        candidate
    )

    if parsed.scheme or parsed.netloc:
        return fallback

    if not candidate.startswith("/"):
        return fallback

    return candidate


def establish_owner_session(
    *,
    username: str,
) -> Dict[str, Any]:
    now = utc_now()

    session.clear()

    session[
        SESSION_AUTHENTICATED
    ] = True

    session[
        SESSION_ROLE
    ] = OWNER_ROLE

    session[
        SESSION_OWNER_ID
    ] = configured_owner_id()

    session[
        SESSION_USERNAME
    ] = username

    session[
        SESSION_AUTH_TIME
    ] = now.isoformat()

    session.permanent = False

    return {
        "authenticated": True,
        "role": OWNER_ROLE,
        "owner_id": (
            configured_owner_id()
        ),
        "username": username,
        "authenticated_at": (
            now.isoformat()
        ),
    }


def owner_session_active() -> bool:
    return all([
        session.get(
            SESSION_AUTHENTICATED
        )
        is True,
        session.get(
            SESSION_ROLE
        )
        == OWNER_ROLE,
        bool(
            session.get(
                SESSION_OWNER_ID
            )
        ),
    ])


def step_up_active() -> bool:
    raw = session.get(
        SESSION_STEP_UP_UNTIL
    )

    if not raw:
        return False

    try:
        expires_at = (
            datetime.fromisoformat(
                raw
            )
        )
    except ValueError:
        return False

    if expires_at.tzinfo is None:
        return False

    return expires_at > utc_now()


def require_human_owner(
    view,
):
    @wraps(view)
    def wrapped(
        *args,
        **kwargs,
    ):
        if not owner_session_active():
            return redirect(
                url_for(
                    "tower_human_login.login",
                    next=request.path,
                )
            )

        return view(
            *args,
            **kwargs,
        )

    return wrapped


def page(
    *,
    title: str,
    content: str,
) -> str:
    return render_template_string(
        """
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta
                name="viewport"
                content="width=device-width,initial-scale=1"
            >
            <title>{{ title }}</title>
            {{ style|safe }}
        </head>
        <body>
            <main class="shell">
                <div class="brand">
                    The Tower · Simplee World
                </div>
                {{ content|safe }}
            </main>
        </body>
        </html>
        """,
        title=title,
        style=BASE_STYLE,
        content=content,
    )


@tower_human_login_bp.get(
    START_PATH
)
def start():
    if owner_session_active():
        return redirect(
            ACCESS_HOME_PATH
        )

    return redirect(
        LOGIN_PATH
    )


@tower_human_login_bp.route(
    LOGIN_PATH,
    methods=[
        "GET",
        "POST",
    ],
)
def login():
    if owner_session_active():
        return redirect(
            ACCESS_HOME_PATH
        )

    configuration = (
        authentication_config_status()
    )

    next_path = safe_next_path(
        request.values.get(
            "next"
        ),
        ACCESS_HOME_PATH,
    )

    error = ""

    if request.method == "POST":
        username = request.form.get(
            "username",
            "",
        ).strip()

        password = request.form.get(
            "password",
            "",
        )

        if not configuration["ready"]:
            error = (
                "Tower owner login is not configured."
            )

        elif verify_owner_credentials(
            username=username,
            password=password,
        ):
            establish_owner_session(
                username=username
            )

            return redirect(
                next_path
            )

        else:
            error = (
                "Tower could not verify those "
                "owner credentials."
            )

    error_html = (
        '<div class="notice danger">'
        + escape(error)
        + "</div>"
        if error
        else ""
    )

    configuration_html = ""

    if not configuration["ready"]:
        configuration_html = """
        <div class="notice danger">
            Owner login setup is required. Configure
            <code>TOWER_OWNER_USERNAME</code> and
            <code>TOWER_OWNER_PASSWORD_HASH</code>,
            or enable explicit local walkthrough mode.
        </div>
        """

    content = f"""
    <section class="hero">
        <h1>Enter The Tower</h1>

        <p>
            Sign in as the owner to reach Tower Access Home
            and launch The Observatory.
        </p>
    </section>

    <section class="card">
        {configuration_html}
        {error_html}

        <form method="post">
            <input
                type="hidden"
                name="next"
                value="{escape(next_path)}"
            >

            <label for="username">
                Owner username
            </label>

            <input
                id="username"
                name="username"
                autocomplete="username"
                required
            >

            <label for="password">
                Owner password
            </label>

            <input
                id="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
            >

            <button type="submit">
                Sign in to The Tower
            </button>
        </form>
    </section>
    """

    return page(
        title="Tower Owner Login",
        content=content,
    )


@tower_human_login_bp.get(
    ACCESS_HOME_PATH
)
@require_human_owner
def access_home():
    username = escape(
        str(
            session.get(
                SESSION_USERNAME,
                "Owner",
            )
        )
    )

    step_up_status = (
        "Active"
        if step_up_active()
        else "Required before OB launch"
    )

    content = f"""
    <section class="hero">
        <h1>Tower Access Home</h1>

        <p>
            Welcome back, {username}. Tower has verified
            your owner session.
        </p>

        <div class="actions">
            <a
                class="button secondary"
                href="{LOGOUT_PATH}"
            >
                Log out
            </a>
        </div>
    </section>

    <div class="grid">
        <section class="card">
            <h2>The Observatory</h2>

            <p>
                Launch the protected owner walkthrough for
                Dashboard, Market Map, Symbol Page, Trade
                Center, Review Center, and Owner Console.
            </p>

            <div class="meta">
                <div>
                    <strong>Access:</strong>
                    Owner
                </div>

                <div>
                    <strong>Step-up:</strong>
                    {step_up_status}
                </div>
            </div>

            <div class="actions">
                <a
                    class="button"
                    href="{OBSERVATORY_LAUNCH_PATH}"
                >
                    Open The Observatory
                </a>
            </div>
        </section>

        <section class="card">
            <h2>Account security</h2>

            <p>
                Tower controls your owner identity,
                permissions, step-up status, and protected
                launch receipts.
            </p>
        </section>
    </div>
    """

    return page(
        title="Tower Access Home",
        content=content,
    )


def _launch_observatory_legacy():
    if (
        session.get(
            SESSION_ROLE
        )
        != OWNER_ROLE
    ):
        return jsonify({
            "allowed": False,
            "reason_code": (
                "tower_ob_owner_role_required"
            ),
        }), 403

    if not step_up_active():
        return redirect(
            url_for(
                (
                    "tower_human_login."
                    "observatory_step_up"
                ),
                next=(
                    OBSERVATORY_WALKTHROUGH_PATH
                ),
            )
        )

    receipt_source = {
        "receipt_type": (
            "tower_ob_human_launch"
        ),
        "owner_id": session.get(
            SESSION_OWNER_ID
        ),
        "role": session.get(
            SESSION_ROLE
        ),
        "created_at": (
            utc_now().isoformat()
        ),
        "destination": (
            OBSERVATORY_WALKTHROUGH_PATH
        ),
        "step_up_verified": True,
        "default_deny": True,
        "broker_submission": False,
        "capital_movement": False,
        "manual_live_authorized": False,
        "live_auto_authorized": False,
    }

    canonical = json_dumps(
        receipt_source
    )

    receipt_source[
        "receipt_hash"
    ] = hashlib.sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest()

    session[
        SESSION_OB_LAUNCH_RECEIPT
    ] = receipt_source

    return redirect(
        OBSERVATORY_WALKTHROUGH_PATH
    )

# TOWER_OB_GP046_NATIVE_HUMAN_LAUNCH_WIRING_V2
# TOWER_OB_OPTIONAL_ROOM_PARAMETER_NORMALIZATION_V1



# TOWER_OB_NATIVE_PRELAUNCH_REDIRECT_PASSTHROUGH_V1


def _tower_ob_native_is_prelaunch_redirect(
    result,
):
    """
    Preserve redirects produced before a launch is approved,
    including owner login and step-up redirects.

    The successful Observatory walkthrough redirect is not
    treated as a pass-through because it must not bypass the
    native GP046 handoff.
    """

    response_object = result
    tuple_status = None

    if isinstance(result, tuple):
        if not result:
            return False

        response_object = result[0]

        if len(result) >= 2:
            tuple_status = result[1]

    if isinstance(
        response_object,
        Mapping,
    ):
        return False

    status_code = _tower_ob_native_first_nonempty(
        tuple_status,
        getattr(
            response_object,
            "status_code",
            None,
        ),
    )

    try:
        numeric_status = int(
            status_code
        )

    except (
        TypeError,
        ValueError,
    ):
        return False

    if not (
        300
        <= numeric_status
        < 400
    ):
        return False

    headers = getattr(
        response_object,
        "headers",
        None,
    )

    location = None

    if headers is not None:
        try:
            location = headers.get(
                "Location"
            )

        except Exception:
            location = None

    if not location:
        return False

    try:
        from urllib.parse import urlparse

        location_path = (
            urlparse(
                str(location)
            ).path
            or str(location)
        )

        walkthrough_path = (
            urlparse(
                str(
                    OBSERVATORY_WALKTHROUGH_PATH
                )
            ).path
            or str(
                OBSERVATORY_WALKTHROUGH_PATH
            )
        )

    except Exception:
        location_path = str(location)

        walkthrough_path = str(
            OBSERVATORY_WALKTHROUGH_PATH
        )

    return (
        location_path
        != walkthrough_path
    )



# TOWER_OB_REAL_HUMAN_REDIRECT_NATIVE_SESSION_HANDOFF_V1


def _tower_ob_native_redirect_location_path(
    result,
):
    response_object = result
    tuple_status = None

    if isinstance(result, tuple):
        if not result:
            return None

        response_object = result[0]

        if len(result) >= 2:
            tuple_status = result[1]

    if isinstance(
        response_object,
        Mapping,
    ):
        return None

    status_code = _tower_ob_native_first_nonempty(
        tuple_status,
        getattr(
            response_object,
            "status_code",
            None,
        ),
    )

    try:
        numeric_status = int(
            status_code
        )

    except (
        TypeError,
        ValueError,
    ):
        return None

    if not (
        300
        <= numeric_status
        < 400
    ):
        return None

    headers = getattr(
        response_object,
        "headers",
        None,
    )

    if headers is None:
        return None

    try:
        location = headers.get(
            "Location"
        )

    except Exception:
        return None

    if not location:
        return None

    try:
        from urllib.parse import urlparse

        return (
            urlparse(
                str(location)
            ).path
            or str(location)
        )

    except Exception:
        return str(location)


def _tower_ob_native_is_walkthrough_redirect(
    result,
):
    location_path = (
        _tower_ob_native_redirect_location_path(
            result
        )
    )

    if not location_path:
        return False

    try:
        from urllib.parse import urlparse

        expected_path = (
            urlparse(
                str(
                    OBSERVATORY_WALKTHROUGH_PATH
                )
            ).path
            or str(
                OBSERVATORY_WALKTHROUGH_PATH
            )
        )

    except Exception:
        expected_path = str(
            OBSERVATORY_WALKTHROUGH_PATH
        )

    return (
        location_path
        == expected_path
    )


def _tower_ob_native_build_from_launch_receipt(
    receipt,
):
    if not isinstance(
        receipt,
        Mapping,
    ):
        raise RuntimeError(
            "tower_ob_native_launch_receipt_required"
        )

    receipt = dict(receipt)

    if (
        str(
            receipt.get(
                "receipt_type"
            )
            or ""
        ).strip()
        != "tower_ob_human_launch"
    ):
        raise RuntimeError(
            "tower_ob_native_launch_receipt_type_invalid"
        )

    owner_id = str(
        receipt.get(
            "owner_id"
        )
        or ""
    ).strip()

    receipt_hash = str(
        receipt.get(
            "receipt_hash"
        )
        or ""
    ).strip()

    step_up_verified = (
        receipt.get(
            "step_up_verified"
        )
        is True
    )

    if not owner_id:
        raise RuntimeError(
            "tower_ob_native_launch_receipt_owner_required"
        )

    if (
        len(receipt_hash) != 64
        or any(
            character
            not in "0123456789abcdefABCDEF"
            for character in receipt_hash
        )
    ):
        raise RuntimeError(
            "tower_ob_native_launch_receipt_hash_invalid"
        )

    if not step_up_verified:
        raise RuntimeError(
            "tower_ob_native_launch_receipt_step_up_required"
        )

    receipt_token = (
        receipt_hash[:32].lower()
    )

    step_up_until = str(
        session.get(
            SESSION_STEP_UP_UNTIL
        )
        or receipt.get(
            "created_at"
        )
        or receipt_hash
    )

    step_up_digest = hashlib.sha256(
        step_up_until.encode(
            "utf-8"
        )
    ).hexdigest()[:32]

    tower_session_id = (
        "tower-human-session-"
        + receipt_token
    )

    step_up_reference = (
        "tower-human-step-up-"
        + step_up_digest
    )

    clearance_decision_ref = (
        receipt_hash.lower()
    )

    legacy_handoff = {
        "handoff_id": (
            "tower-human-launch-"
            + receipt_token
        ),
        "owner_id": owner_id,
        "session_id": (
            tower_session_id
        ),
        "tower_session_id": (
            tower_session_id
        ),
        "requested_path": (
            "/dashboard"
        ),
        "requested_mode": (
            "manual_live"
        ),
        "mode": (
            "manual_live"
        ),
        "step_up_verified": True,
        "step_up_reference": (
            step_up_reference
        ),
        "clearance_verified": True,
        "clearance_decision_ref": (
            clearance_decision_ref
        ),
        "room_id": "dashboard",
        "mission_account_id": "",
        "symbol": "",
        "rehearsal_status": "passed",
    }

    payload = {
        "allowed": True,
        "owner_id": owner_id,
        "tower_session_id": (
            tower_session_id
        ),
        "requested_path": (
            "/dashboard"
        ),
        "requested_mode": (
            "manual_live"
        ),
        "step_up_verified": True,
        "step_up_reference": (
            step_up_reference
        ),
        "clearance_verified": True,
        "clearance_decision_ref": (
            clearance_decision_ref
        ),
        "room_id": "dashboard",
        "mission_account_id": "",
        "symbol": "",
        "rehearsal_status": "passed",
        "launch_handoff": (
            legacy_handoff
        ),
    }

    return _tower_ob_native_build_launch(
        payload
    )


def _tower_ob_native_store_walkthrough_handoff():
    receipt = session.get(
        SESSION_OB_LAUNCH_RECEIPT
    )

    native_payload = (
        _tower_ob_native_build_from_launch_receipt(
            receipt
        )
    )

    native_handoff = native_payload.get(
        "launch_handoff"
    )

    if not isinstance(
        native_handoff,
        Mapping,
    ):
        raise RuntimeError(
            "tower_ob_native_walkthrough_handoff_required"
        )

    session[
        SESSION_OB_NATIVE_LAUNCH_HANDOFF
    ] = dict(
        native_handoff
    )

    try:
        session.modified = True

    except Exception:
        pass

    return dict(
        native_handoff
    )


def _tower_ob_native_extract_payload(result):
    """
    Normalize supported Flask/Tower return forms while
    preserving the original outer response structure.
    """

    outer_kind = "mapping"
    status_code = None
    headers = None
    response_object = None
    payload = None

    if isinstance(result, tuple):
        outer_kind = "tuple"

        if not result:
            raise RuntimeError(
                "tower_ob_native_empty_response_tuple"
            )

        response_object = result[0]

        if len(result) >= 2:
            status_code = result[1]

        if len(result) >= 3:
            headers = result[2]

    else:
        response_object = result

    if isinstance(response_object, Mapping):
        payload = dict(response_object)

    elif hasattr(response_object, "get_json"):
        payload = response_object.get_json(
            silent=True
        )

        if not isinstance(payload, Mapping):
            raise RuntimeError(
                "tower_ob_native_json_mapping_required"
            )

        payload = dict(payload)

        if outer_kind != "tuple":
            outer_kind = "flask_response"

    else:
        raise RuntimeError(
            "tower_ob_native_supported_response_required"
        )

    return {
        "outer_kind": outer_kind,
        "status_code": status_code,
        "headers": headers,
        "response_object": response_object,
        "payload": payload,
    }


def _tower_ob_native_restore_response(
    normalized,
    payload,
):
    outer_kind = normalized["outer_kind"]

    if outer_kind == "mapping":
        return payload

    response_object = normalized[
        "response_object"
    ]

    if hasattr(response_object, "get_json"):
        rebuilt = jsonify(payload)
    else:
        rebuilt = payload

    if outer_kind == "flask_response":
        return rebuilt

    status_code = normalized["status_code"]
    headers = normalized["headers"]

    if headers is not None:
        return (
            rebuilt,
            status_code,
            headers,
        )

    if status_code is not None:
        return (
            rebuilt,
            status_code,
        )

    return (rebuilt,)


def _tower_ob_native_first_nonempty(
    *values,
):
    for value in values:
        if value not in (
            None,
            "",
            [],
            {},
        ):
            return value

    return None


def _tower_ob_native_request_value(
    *names,
):
    try:
        for name in names:
            value = request.args.get(name)

            if value not in (
                None,
                "",
            ):
                return value
    except RuntimeError:
        pass

    return None


def _tower_ob_native_session_value(
    *names,
):
    try:
        for name in names:
            value = session.get(name)

            if value not in (
                None,
                "",
            ):
                return value
    except RuntimeError:
        pass

    return None


def _tower_ob_native_mapping_value(
    mappings,
    *names,
):
    for mapping in mappings:
        if not isinstance(mapping, Mapping):
            continue

        for name in names:
            value = mapping.get(name)

            if value not in (
                None,
                "",
            ):
                return value

    return None


def _tower_ob_native_build_launch(
    payload,
):
    legacy_handoff = payload.get(
        "launch_handoff"
    )

    if not isinstance(
        legacy_handoff,
        Mapping,
    ):
        raise RuntimeError(
            "tower_ob_native_launch_handoff_required"
        )

    context_mappings = [
        payload,
        legacy_handoff,
    ]

    owner_id = _tower_ob_native_first_nonempty(
        _tower_ob_native_mapping_value(
            context_mappings,
            "owner_id",
            "user_id",
            "actor_id",
            "subject_id",
        ),
        _tower_ob_native_session_value(
            "owner_id",
            "user_id",
            "actor_id",
            "subject_id",
        ),
    )

    tower_session_id = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_mapping_value(
                context_mappings,
                "tower_session_id",
                "session_id",
            ),
            _tower_ob_native_session_value(
                "tower_session_id",
                "session_id",
            ),
        )
    )

    requested_path = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_request_value(
                "requested_path",
                "path",
                "room_path",
                "next",
            ),
            _tower_ob_native_mapping_value(
                context_mappings,
                "requested_path",
                "path",
                "room_path",
                "target_path",
                "launch_path",
            ),
            "/dashboard",
        )
    )

    requested_mode = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_request_value(
                "mode",
                "requested_mode",
            ),
            _tower_ob_native_mapping_value(
                context_mappings,
                "requested_mode",
                "mode",
            ),
            "manual_live",
        )
    )

    mission_account_id = (
        (_tower_ob_native_first_nonempty(
            _tower_ob_native_request_value(
                "mission_account_id",
            ),
            _tower_ob_native_mapping_value(
                context_mappings,
                "mission_account_id",
            ),
            "",
        ) or "")
    )

    symbol = (_tower_ob_native_first_nonempty(
        _tower_ob_native_request_value(
            "symbol",
        ),
        _tower_ob_native_mapping_value(
            context_mappings,
            "symbol",
        ),
        "",
    ) or "")

    step_up_verified = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_mapping_value(
                context_mappings,
                "step_up_verified",
                "step_up_active",
            ),
            True if step_up_active() else None,
        )
    )

    clearance_verified = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_mapping_value(
                context_mappings,
                "clearance_verified",
                "clearance_granted",
                "allowed",
            ),
        )
    )

    clearance_decision_ref = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_mapping_value(
                context_mappings,
                "clearance_decision_ref",
                "clearance_decision_reference",
                "decision_ref",
            ),
            _tower_ob_native_session_value(
                "clearance_decision_ref",
                "clearance_decision_reference",
                "decision_ref",
            ),
        )
    )

    room_id = _tower_ob_native_first_nonempty(
        _tower_ob_native_mapping_value(
            context_mappings,
            "room_id",
            "target_room_id",
            "room",
        ),
        "dashboard"
        if requested_path in (
            "/dashboard",
            "/ob/dashboard",
        )
        else None,
    )

    missing = []

    for field_name, value in [
        ("owner_id", owner_id),
        ("tower_session_id", tower_session_id),
        ("requested_path", requested_path),
        ("requested_mode", requested_mode),
        ("step_up_verified", step_up_verified),
        (
            "clearance_verified",
            clearance_verified,
        ),
        (
            "clearance_decision_ref",
            clearance_decision_ref,
        ),
        ("room_id", room_id),
    ]:
        if value in (
            None,
            "",
            False,
        ):
            missing.append(field_name)

    if missing:
        raise RuntimeError(
            "tower_ob_native_launch_context_missing:"
            + ",".join(missing)
        )

    step_up_reference = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_mapping_value(
                context_mappings,
                "step_up_reference",
                "step_up_receipt_id",
                "step_up_id",
            ),
            _tower_ob_native_session_value(
                "step_up_reference",
                "step_up_receipt_id",
                "step_up_id",
            ),
            (
                "tower-human-owner-step-up-active"
                if bool(step_up_verified)
                else None
            ),
        )
    )

    if not step_up_reference:
        raise RuntimeError(
            "tower_ob_native_launch_context_missing:"
            "step_up_reference"
        )

    rehearsal_status = (
        _tower_ob_native_first_nonempty(
            _tower_ob_native_mapping_value(
                context_mappings,
                "rehearsal_status",
            ),
            "passed",
        )
    )

    native_legacy_handoff = dict(
        legacy_handoff
    )

    native_legacy_handoff[
        "clearance_decision_ref"
    ] = str(
        clearance_decision_ref
    )

    native_handoff = build_native_gp046_handoff(
        legacy_handoff=native_legacy_handoff,
        owner_id=str(owner_id),
        session_id=str(tower_session_id),
        requested_path=str(requested_path),
        mode=str(requested_mode),
        step_up_reference=str(
            step_up_reference
        ),
        mission_account_id=str(
            mission_account_id
        ),
        symbol=str(symbol),
        rehearsal_status=str(
            rehearsal_status
        ),
    )

    payload["launch_handoff"] = native_handoff
    payload["gp046_native_contract"] = True
    payload[
        "runtime_contract_adapter_required"
    ] = False

    return payload


@tower_human_login_bp.get(
    OBSERVATORY_LAUNCH_PATH
)
@require_human_owner
def launch_observatory():
    legacy_result = _launch_observatory_legacy()

    if _tower_ob_native_is_walkthrough_redirect(
        legacy_result
    ):
        _tower_ob_native_store_walkthrough_handoff()

        return legacy_result

    if _tower_ob_native_is_prelaunch_redirect(
        legacy_result
    ):
        return legacy_result

    normalized = _tower_ob_native_extract_payload(
        legacy_result
    )

    payload = normalized["payload"]

    if payload.get("allowed") is False:
        return _tower_ob_native_restore_response(
            normalized,
            payload,
        )

    native_payload = _tower_ob_native_build_launch(
        payload
    )

    return _tower_ob_native_restore_response(
        normalized,
        native_payload,
    )


@tower_human_login_bp.route(
    OBSERVATORY_STEP_UP_PATH,
    methods=[
        "GET",
        "POST",
    ],
)
@require_human_owner
def observatory_step_up():
    next_path = safe_next_path(
        request.values.get(
            "next"
        ),
        OBSERVATORY_LAUNCH_PATH,
    )

    error = ""

    if request.method == "POST":
        password = request.form.get(
            "password",
            "",
        )

        username = str(
            session.get(
                SESSION_USERNAME,
                "",
            )
        )

        if verify_owner_credentials(
            username=username,
            password=password,
        ):
            expires_at = (
                utc_now()
                + timedelta(
                    minutes=(
                        configured_step_up_minutes()
                    )
                )
            )

            session[
                SESSION_STEP_UP_UNTIL
            ] = expires_at.isoformat()

            return redirect(
                OBSERVATORY_LAUNCH_PATH
            )

        error = (
            "Tower could not verify the "
            "step-up password."
        )

    error_html = (
        '<div class="notice danger">'
        + escape(error)
        + "</div>"
        if error
        else ""
    )

    content = f"""
    <section class="hero">
        <h1>Confirm It Is You</h1>

        <p>
            Re-enter your Tower password before opening
            The Observatory.
        </p>
    </section>

    <section class="card">
        {error_html}

        <form method="post">
            <input
                type="hidden"
                name="next"
                value="{escape(next_path)}"
            >

            <label for="password">
                Owner password
            </label>

            <input
                id="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
            >

            <button type="submit">
                Verify and open OB
            </button>
        </form>
    </section>
    """

    return page(
        title="Tower Owner Step-Up",
        content=content,
    )


@tower_human_login_bp.get(
    LOGOUT_PATH
)
def logout():
    session.clear()

    return redirect(
        LOGIN_PATH
    )


@tower_human_login_bp.get(
    "/tower/auth/status.json"
)
def auth_status():
    return jsonify({
        "configured": (
            authentication_config_status()
        ),
        "authenticated": (
            owner_session_active()
        ),
        "role": session.get(
            SESSION_ROLE
        ),
        "owner_id_present": bool(
            session.get(
                SESSION_OWNER_ID
            )
        ),
        "step_up_active": (
            step_up_active()
        ),
        "launch_receipt_present": bool(
            session.get(
                SESSION_OB_LAUNCH_RECEIPT
            )
        ),
    })


def json_dumps(
    payload: Dict[str, Any],
) -> str:
    import json

    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    )


def configure_tower_session_secret(
    app,
) -> None:
    configured = os.environ.get(
        TOWER_SESSION_SECRET_ENV
    )

    if configured:
        app.secret_key = configured

    elif not app.secret_key:
        # Ephemeral fallback for local import/testing only.
        # Production and hosted environments must provide
        # TOWER_SESSION_SECRET.
        app.secret_key = secrets.token_hex(
            32
        )


def inject_tower_login_link(
    response: Response,
) -> Response:
    if (
        request.path not in {
            "/tower",
            "/tower/",
        }
        or response.status_code != 200
        or not response.content_type
        or "text/html"
        not in response.content_type
    ):
        return response

    body = response.get_data(
        as_text=True
    )

    marker = (
        "tower-human-login-entry"
    )

    if marker in body:
        return response

    destination = (
        ACCESS_HOME_PATH
        if owner_session_active()
        else LOGIN_PATH
    )

    label = (
        "Open Tower Access Home"
        if owner_session_active()
        else "Owner Login"
    )

    entry = f"""
    <div
        id="{marker}"
        style="
            position:fixed;
            right:18px;
            bottom:18px;
            z-index:99999;
        "
    >
        <a
            href="{destination}"
            style="
                display:inline-flex;
                padding:12px 18px;
                border-radius:999px;
                text-decoration:none;
                font-weight:800;
                background:#ead7ff;
                color:#1a1028;
                box-shadow:0 12px 34px rgba(0,0,0,.3);
            "
        >
            {label}
        </a>
    </div>
    """

    if "</body>" in body:
        body = body.replace(
            "</body>",
            entry + "</body>",
            1,
        )
    else:
        body += entry

    response.set_data(
        body
    )

    return response


# BEGIN TOWER HUMAN LOGIN CERT ROUTES

def _human_login_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2503 import (
        build_ir_cert_p2503_preview,
    )
    from tower.tower_ir_cert_p2504 import (
        build_ir_cert_p2504_preview,
    )
    from tower.tower_ir_cert_p2505 import (
        build_ir_cert_p2505_preview,
    )
    from tower.tower_ir_cert_p2506 import (
        build_ir_cert_p2506_preview,
    )
    from tower.tower_ir_cert_p2507 import (
        build_ir_cert_p2507_preview,
    )
    from tower.tower_ir_cert_p2508 import (
        build_ir_cert_p2508_preview,
    )
    from tower.tower_ir_cert_p2509 import (
        build_ir_cert_p2509_preview,
    )
    from tower.tower_ir_cert_p2510 import (
        build_ir_cert_p2510_preview,
    )
    from tower.tower_ir_cert_p2511 import (
        build_ir_cert_p2511_preview,
    )
    from tower.tower_ir_cert_p2512 import (
        build_ir_cert_p2512_preview,
    )

    builders = {
        2503: build_ir_cert_p2503_preview,
        2504: build_ir_cert_p2504_preview,
        2505: build_ir_cert_p2505_preview,
        2506: build_ir_cert_p2506_preview,
        2507: build_ir_cert_p2507_preview,
        2508: build_ir_cert_p2508_preview,
        2509: build_ir_cert_p2509_preview,
        2510: build_ir_cert_p2510_preview,
        2511: build_ir_cert_p2511_preview,
        2512: build_ir_cert_p2512_preview,
    }

    builder = builders.get(
        pack
    )

    if builder is None:
        return {
            "status": "not_found",
            "pack": str(pack),
        }

    return builder()


def _human_login_cert_response(
    pack: int,
):
    if not owner_session_active():
        return jsonify({
            "allowed": False,
            "reason_code": (
                "tower_owner_session_required"
            ),
            "pack": str(pack),
        }), 403

    return jsonify(
        _human_login_cert_payload(
            pack
        )
    )


def _register_human_login_cert_routes():
    for pack in range(
        2503,
        2513,
    ):
        tower_human_login_bp.add_url_rule(
            f"/tower/ir-cert-v{pack}.json",
            endpoint=(
                f"human_login_cert_pack_{pack}"
            ),
            view_func=(
                lambda selected_pack=pack:
                _human_login_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_human_login_cert_routes()

# END TOWER HUMAN LOGIN CERT ROUTES


def register_tower_human_login(
    app,
) -> None:
    if (
        "tower_human_login"
        not in app.blueprints
    ):
        configure_tower_session_secret(
            app
        )

        app.register_blueprint(
            tower_human_login_bp
        )

        app.after_request(
            inject_tower_login_link
        )
