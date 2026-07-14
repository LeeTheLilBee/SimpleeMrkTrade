"""
Tower → Observatory owner walkthrough.

This is a preview-only owner interface over the certified
Tower/OB protected-launch contract.

It does not submit orders, move capital, authorize production
Manual Live, activate Live Auto, or write to Vault.
"""

from __future__ import annotations

import secrets
from copy import deepcopy
from typing import Any, Dict

from flask import (
    Blueprint,
    abort,
    jsonify,
    redirect,
    render_template_string,
    request,
    session,
    url_for,
)

from tower.tower_ir_cert_p2372 import (
    ROOMS,
)
from tower.tower_ir_cert_p2389 import (
    run_protected_room_integration,
)


tower_ob_walkthrough_bp = Blueprint(
    "tower_ob_walkthrough",
    __name__,
)


OWNER_ROLE_VALUES = {
    "owner",
    "tower_owner",
    "system_owner",
    "primary_owner",
}


def _session_role() -> str:
    for key in (
        "tower_role",
        "user_role",
        "role",
        "account_role",
    ):
        value = session.get(key)

        if value:
            return str(value).strip().lower()

    if session.get("is_owner") is True:
        return "owner"

    return ""


def _owner_id() -> str:
    for key in (
        "owner_id",
        "user_id",
        "account_id",
        "subject_id",
    ):
        value = session.get(key)

        if value:
            return str(value)

    return ""


def owner_access_allowed() -> bool:
    return (
        _session_role() in OWNER_ROLE_VALUES
        and bool(_owner_id())
    )


def require_owner_access():
    if not owner_access_allowed():
        abort(403)


def room_by_id(room_id: str) -> Dict[str, Any] | None:
    for room in ROOMS:
        if room["room_id"] == room_id:
            return deepcopy(room)

    return None


def room_request_context(
    room: Dict[str, Any],
    form: Dict[str, Any],
) -> Dict[str, Any]:
    room_id = room["room_id"]

    if room_id == "ob_room_symbol_page":
        symbol = str(
            form.get("symbol", "AMD")
        ).strip().upper()

        if not symbol:
            symbol = "AMD"

        return {
            "path": f"/symbol/{symbol}",
            "object_context": {
                "symbol": symbol,
            },
        }

    if room["object_guard"]["required"]:
        mission_account_id = str(
            form.get(
                "mission_account_id",
                "proof_demo",
            )
        ).strip()

        if not mission_account_id:
            mission_account_id = "proof_demo"

        return {
            "path": room["canonical_route"],
            "object_context": {
                "mission_account_id": (
                    mission_account_id
                ),
            },
        }

    return {
        "path": room["canonical_route"],
        "object_context": {},
    }


def start_walkthrough_state() -> Dict[str, Any]:
    state = {
        "walkthrough_id": (
            "obwalk_" + secrets.token_hex(8)
        ),
        "owner_id": _owner_id(),
        "stage": "room_selection",
        "mode": "paper",
        "active_room_id": None,
        "launch_receipt": None,
        "close_receipt": None,
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
    }

    session["tower_ob_walkthrough"] = state

    return state


def walkthrough_state() -> Dict[str, Any]:
    state = session.get(
        "tower_ob_walkthrough"
    )

    if not isinstance(state, dict):
        state = start_walkthrough_state()

    return state


def save_walkthrough_state(
    state: Dict[str, Any],
):
    session["tower_ob_walkthrough"] = state
    session.modified = True


BASE_STYLE = """
<style>
:root {
    color-scheme: dark;
    --bg: #070814;
    --panel: rgba(19, 21, 42, .82);
    --panel-strong: rgba(25, 28, 56, .96);
    --line: rgba(201, 196, 255, .18);
    --text: #f5f3ff;
    --muted: #b8b3cf;
    --accent: #d8b4fe;
    --accent-2: #8b5cf6;
    --good: #86efac;
    --warn: #fde68a;
    --bad: #fda4af;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    color: var(--text);
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
    background:
        radial-gradient(
            circle at 20% 5%,
            rgba(124, 58, 237, .24),
            transparent 34%
        ),
        radial-gradient(
            circle at 80% 0%,
            rgba(59, 130, 246, .14),
            transparent 30%
        ),
        linear-gradient(
            180deg,
            #080916,
            #03040b
        );
}

.shell {
    width: min(1180px, calc(100% - 32px));
    margin: 0 auto;
    padding: 34px 0 70px;
}

.topline {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin-bottom: 24px;
}

.brand {
    font-size: 13px;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: var(--accent);
}

.mode-chip {
    padding: 8px 12px;
    border: 1px solid var(--line);
    border-radius: 999px;
    background: rgba(8, 10, 24, .76);
    color: var(--muted);
    font-size: 12px;
}

.hero {
    padding: 28px;
    border: 1px solid var(--line);
    border-radius: 24px;
    background:
        linear-gradient(
            140deg,
            rgba(39, 32, 73, .94),
            rgba(13, 15, 31, .92)
        );
    box-shadow: 0 24px 80px rgba(0, 0, 0, .38);
}

.hero h1 {
    margin: 0 0 12px;
    font-size: clamp(30px, 5vw, 56px);
    line-height: 1;
}

.hero p {
    max-width: 760px;
    margin: 0;
    color: var(--muted);
    line-height: 1.65;
}

.status-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

.status {
    padding: 8px 11px;
    border-radius: 12px;
    background: rgba(7, 8, 20, .64);
    border: 1px solid var(--line);
    color: var(--muted);
    font-size: 12px;
}

.status.good {
    color: var(--good);
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
    margin-top: 22px;
}

.card {
    padding: 20px;
    border: 1px solid var(--line);
    border-radius: 19px;
    background: var(--panel);
    backdrop-filter: blur(18px);
}

.card h2,
.card h3 {
    margin-top: 0;
}

.card p,
.small {
    color: var(--muted);
    line-height: 1.55;
}

.meta {
    display: grid;
    gap: 7px;
    margin: 18px 0;
    font-size: 13px;
    color: var(--muted);
}

.meta strong {
    color: var(--text);
}

.button,
button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 44px;
    padding: 0 16px;
    border: 0;
    border-radius: 13px;
    background:
        linear-gradient(
            135deg,
            var(--accent-2),
            #6d28d9
        );
    color: white;
    font-weight: 700;
    text-decoration: none;
    cursor: pointer;
}

.button.secondary {
    border: 1px solid var(--line);
    background: rgba(8, 10, 24, .72);
    color: var(--text);
}

.actions {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 20px;
}

label {
    display: grid;
    gap: 8px;
    margin-top: 15px;
    color: var(--muted);
    font-size: 13px;
}

input,
select {
    width: 100%;
    min-height: 44px;
    padding: 0 13px;
    border: 1px solid var(--line);
    border-radius: 12px;
    color: var(--text);
    background: rgba(5, 6, 16, .78);
}

.receipt {
    overflow-wrap: anywhere;
}

.reason {
    color: var(--warn);
}

.danger {
    color: var(--bad);
}

footer {
    margin-top: 28px;
    color: var(--muted);
    font-size: 12px;
}
</style>
"""


PAGE_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1"
    >
    <title>{{ title }}</title>
    {{ style|safe }}
</head>
<body>
    <main class="shell">
        <div class="topline">
            <div class="brand">
                The Tower → The Observatory
            </div>

            <div class="mode-chip">
                Protected Preview • Paper Mode
            </div>
        </div>

        {{ content|safe }}

        <footer>
            Default deny remains active. No broker submission,
            capital movement, production Manual Live authorization,
            Live Auto activation, or Vault upload occurs here.
        </footer>
    </main>
</body>
</html>
"""


def render_page(
    *,
    title: str,
    content: str,
):
    return render_template_string(
        PAGE_TEMPLATE,
        title=title,
        style=BASE_STYLE,
        content=content,
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough"
)
def walkthrough_home():
    require_owner_access()

    state = walkthrough_state()

    cards = []

    for room in ROOMS:
        badges = [
            (
                "Step-up required"
                if room["step_up_required"]
                else "Standard protected entry"
            ),
            (
                "Owner only"
                if room["owner_only"]
                else "Authorized role"
            ),
            room["required_clearance_value"],
        ]

        cards.append(f"""
        <section class="card">
            <h2>{room["display_name"]}</h2>

            <p>
                Protected Observatory room controlled by
                Tower-issued identity, clearance, scope,
                handoff, and lockback contracts.
            </p>

            <div class="meta">
                <div>
                    <strong>Room ID:</strong>
                    {room["room_id"]}
                </div>

                <div>
                    <strong>Route:</strong>
                    {room["canonical_route"]}
                </div>

                <div>
                    <strong>Clearance:</strong>
                    {room["required_clearance_value"]}
                    / rank {room["required_clearance_rank"]}
                </div>

                <div>
                    <strong>Access:</strong>
                    {" • ".join(badges)}
                </div>
            </div>

            <a
                class="button"
                href="{url_for(
                    "tower_ob_walkthrough.walkthrough_room",
                    room_id=room["room_id"],
                )}"
            >
                Review protected launch
            </a>
        </section>
        """)

    content = f"""
    <section class="hero">
        <h1>Observatory Run-Through</h1>

        <p>
            Walk through the certified Tower-to-OB owner
            launch sequence. Choose a room, review its access
            requirements, issue a protected preview handoff,
            inspect the receipts, and close back into Tower.
        </p>

        <div class="status-row">
            <span class="status good">
                Owner verified
            </span>

            <span class="status good">
                ob_owner_command / rank 900
            </span>

            <span class="status">
                Walkthrough {state["walkthrough_id"]}
            </span>

            <span class="status">
                Default deny active
            </span>
        </div>
    </section>

    <div class="grid">
        {"".join(cards)}
    </div>
    """

    return render_page(
        title="Tower → Observatory Walkthrough",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/restart"
)
def walkthrough_restart():
    require_owner_access()
    start_walkthrough_state()

    return redirect(
        url_for(
            "tower_ob_walkthrough.walkthrough_home"
        )
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/room/<room_id>"
)
def walkthrough_room(room_id: str):
    require_owner_access()

    room = room_by_id(room_id)

    if room is None:
        abort(404)

    extra_fields = ""

    if room_id == "ob_room_symbol_page":
        extra_fields = """
        <label>
            Symbol
            <input
                name="symbol"
                value="AMD"
                maxlength="12"
                autocomplete="off"
            >
        </label>
        """

    elif room["object_guard"]["required"]:
        extra_fields = """
        <label>
            Mission account
            <select name="mission_account_id">
                <option value="proof_demo">
                    Proof / Demo
                </option>
                <option value="personal">
                    Personal
                </option>
                <option value="trust">
                    Trust
                </option>
                <option value="simplee_world">
                    Simplee World
                </option>
            </select>
        </label>
        """

    content = f"""
    <section class="hero">
        <h1>{room["display_name"]}</h1>

        <p>
            Review the Tower-controlled room contract before
            issuing a preview handoff.
        </p>

        <div class="status-row">
            <span class="status">
                {room["room_id"]}
            </span>

            <span class="status">
                {room["canonical_route"]}
            </span>

            <span class="status good">
                {room["required_clearance_value"]}
                / {room["required_clearance_rank"]}
            </span>
        </div>
    </section>

    <section class="card" style="margin-top:22px">
        <h2>Protected launch requirements</h2>

        <div class="meta">
            <div>
                <strong>Tower session clearance:</strong>
                ob_owner_command / rank 900
            </div>

            <div>
                <strong>Room minimum clearance:</strong>
                {room["required_clearance_value"]}
                / rank {room["required_clearance_rank"]}
            </div>

            <div>
                <strong>Required role:</strong>
                {room["required_role"]}
            </div>

            <div>
                <strong>Owner only:</strong>
                {room["owner_only"]}
            </div>

            <div>
                <strong>Step-up required:</strong>
                {room["step_up_required"]}
            </div>

            <div>
                <strong>Supported modes:</strong>
                {", ".join(room["allowed_modes"])}
            </div>

            <div>
                <strong>Object guard:</strong>
                {room["object_guard"]["required"]}
            </div>

            <div>
                <strong>Allow reason:</strong>
                {room["allow_reason_code"]}
            </div>
        </div>

        <form
            method="post"
            action="{url_for(
                "tower_ob_walkthrough.walkthrough_launch",
                room_id=room_id,
            )}"
        >
            {extra_fields}

            <div class="actions">
                <button type="submit">
                    Launch protected preview
                </button>

                <a
                    class="button secondary"
                    href="{url_for(
                        "tower_ob_walkthrough.walkthrough_home"
                    )}"
                >
                    Back to rooms
                </a>
            </div>
        </form>
    </section>
    """

    return render_page(
        title=f"Review {room['display_name']}",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/room/<room_id>/launch"
)
def walkthrough_launch(room_id: str):
    require_owner_access()

    room = room_by_id(room_id)

    if room is None:
        abort(404)

    state = walkthrough_state()

    context = room_request_context(
        room,
        request.form,
    )

    rehearsal_index = secrets.randbelow(
        900000
    ) + 100000

    result = run_protected_room_integration(
        requested_path=context["path"],
        mode="paper",
        object_context=context["object_context"],
        rehearsal_index=rehearsal_index,
    )

    if result["status"] != "passed":
        state["stage"] = "denied"
        state["active_room_id"] = room_id
        state["denial_reason"] = (
            result.get("decision_envelope", {})
            .get(
                "reason_code",
                "tower_ob_walkthrough_launch_denied",
            )
        )

        save_walkthrough_state(state)

        return redirect(
            url_for(
                "tower_ob_walkthrough.walkthrough_denied"
            )
        )

    state.update({
        "stage": "receipt_review",
        "active_room_id": room_id,
        "launch_receipt": {
            "room_id": room_id,
            "display_name": room["display_name"],
            "canonical_path": result[
                "route_decision"
            ]["canonical_path"],
            "handoff_id": result[
                "handoff"
            ]["handoff_id"],
            "access_receipt_id": result[
                "access_receipt"
            ]["receipt_id"],
            "close_receipt_id": result[
                "close_receipt"
            ]["close_receipt_id"],
            "clearance_value": result[
                "clearance_decision"
            ]["canonical_clearance_value"],
            "clearance_rank": result[
                "clearance_decision"
            ]["canonical_clearance_rank"],
            "step_up_state": result[
                "access_receipt"
            ]["step_up_state"],
            "completion_accepted": result[
                "completion_intake"
            ]["accepted"],
            "lockback_verified": result[
                "lockback_verification"
            ]["verified"],
            "final_access_state": result[
                "close_receipt"
            ]["ob_access_state"],
            "default_deny_restored": result[
                "close_receipt"
            ]["default_deny_restored"],
            "preview_only": True,
        },
    })

    save_walkthrough_state(state)

    return redirect(
        url_for(
            "tower_ob_walkthrough.walkthrough_receipt"
        )
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/receipt"
)
def walkthrough_receipt():
    require_owner_access()

    state = walkthrough_state()
    receipt = state.get("launch_receipt")

    if not isinstance(receipt, dict):
        return redirect(
            url_for(
                "tower_ob_walkthrough.walkthrough_home"
            )
        )

    content = f"""
    <section class="hero">
        <h1>Protected launch passed</h1>

        <p>
            Tower issued the preview handoff, validated the
            room scope, accepted the completion receipt, and
            returned the Observatory to locked-back default
            deny.
        </p>

        <div class="status-row">
            <span class="status good">
                Launch allowed
            </span>

            <span class="status good">
                Completion accepted
            </span>

            <span class="status good">
                Lockback verified
            </span>
        </div>
    </section>

    <section class="card receipt" style="margin-top:22px">
        <h2>{receipt["display_name"]}</h2>

        <div class="meta">
            <div>
                <strong>Room ID:</strong>
                {receipt["room_id"]}
            </div>

            <div>
                <strong>Approved path:</strong>
                {receipt["canonical_path"]}
            </div>

            <div>
                <strong>Clearance:</strong>
                {receipt["clearance_value"]}
                / rank {receipt["clearance_rank"]}
            </div>

            <div>
                <strong>Step-up:</strong>
                {receipt["step_up_state"]}
            </div>

            <div>
                <strong>Handoff:</strong>
                {receipt["handoff_id"]}
            </div>

            <div>
                <strong>Access receipt:</strong>
                {receipt["access_receipt_id"]}
            </div>

            <div>
                <strong>Close receipt:</strong>
                {receipt["close_receipt_id"]}
            </div>

            <div>
                <strong>Final access state:</strong>
                {receipt["final_access_state"]}
            </div>

            <div>
                <strong>Default deny restored:</strong>
                {receipt["default_deny_restored"]}
            </div>
        </div>

        <form
            method="post"
            action="{url_for(
                "tower_ob_walkthrough.walkthrough_close"
            )}"
        >
            <div class="actions">
                <a
                    class="button"
                    href="{_walkthrough_real_surface_url(
                        room_id=receipt["room_id"],
                        walkthrough_id=state["walkthrough_id"],
                    )}"
                >
                    Open the real room surface
                </a>

                <button
                    class="button secondary"
                    type="submit"
                >
                    Close and return to Tower
                </button>

                <a
                    class="button secondary"
                    href="{url_for(
                        "tower_ob_walkthrough.walkthrough_home"
                    )}"
                >
                    Run another room
                </a>
            </div>
        </form>
    </section>
    """

    return render_page(
        title="Observatory Walkthrough Receipt",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/close"
)
def walkthrough_close():
    require_owner_access()

    previous = walkthrough_state()

    closed = {
        "walkthrough_id": previous.get(
            "walkthrough_id"
        ),
        "owner_id": _owner_id(),
        "stage": "closed",
        "active_room_id": None,
        "launch_receipt": None,
        "close_receipt": {
            "ob_access_state": "locked_back",
            "default_deny_restored": True,
            "handoff_replay_state": "blocked",
            "step_up_state": "revoked_or_not_required",
        },
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
    }

    save_walkthrough_state(closed)

    content = f"""
    <section class="hero">
        <h1>Returned to Tower</h1>

        <p>
            The walkthrough session is closed. The launch
            handoff cannot be replayed, step-up authority is
            closed, and the Observatory is locked behind
            Tower again.
        </p>

        <div class="status-row">
            <span class="status good">
                Locked back
            </span>

            <span class="status good">
                Replay blocked
            </span>

            <span class="status good">
                Default deny restored
            </span>
        </div>

        <div class="actions">
            <form
                method="post"
                action="{url_for(
                    "tower_ob_walkthrough.walkthrough_restart"
                )}"
            >
                <button type="submit">
                    Start another walkthrough
                </button>
            </form>
        </div>
    </section>
    """

    return render_page(
        title="Returned to Tower",
        content=content,
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/denied"
)
def walkthrough_denied():
    require_owner_access()

    state = walkthrough_state()

    reason = state.get(
        "denial_reason",
        "tower_ob_walkthrough_launch_denied",
    )

    content = f"""
    <section class="hero">
        <h1>Protected launch denied</h1>

        <p>
            Tower did not issue an Observatory launch
            authorization. The room remains locked.
        </p>

        <div class="status-row">
            <span class="status danger">
                Access denied
            </span>

            <span class="status">
                Default deny preserved
            </span>
        </div>
    </section>

    <section class="card" style="margin-top:22px">
        <h2>Decision</h2>

        <p class="reason">
            {reason}
        </p>

        <div class="actions">
            <a
                class="button secondary"
                href="{url_for(
                    "tower_ob_walkthrough.walkthrough_home"
                )}"
            >
                Return to room selection
            </a>
        </div>
    </section>
    """

    return render_page(
        title="Observatory Launch Denied",
        content=content,
    )

# BEGIN TOWER OB WALKTHROUGH CERTIFICATION ROUTES

def _build_walkthrough_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    builders = {}

    from tower.tower_ir_cert_p2423 import (
        build_ir_cert_p2423_preview,
    )
    from tower.tower_ir_cert_p2424 import (
        build_ir_cert_p2424_preview,
    )
    from tower.tower_ir_cert_p2425 import (
        build_ir_cert_p2425_preview,
    )
    from tower.tower_ir_cert_p2426 import (
        build_ir_cert_p2426_preview,
    )
    from tower.tower_ir_cert_p2427 import (
        build_ir_cert_p2427_preview,
    )
    from tower.tower_ir_cert_p2428 import (
        build_ir_cert_p2428_preview,
    )
    from tower.tower_ir_cert_p2429 import (
        build_ir_cert_p2429_preview,
    )
    from tower.tower_ir_cert_p2430 import (
        build_ir_cert_p2430_preview,
    )
    from tower.tower_ir_cert_p2431 import (
        build_ir_cert_p2431_preview,
    )
    from tower.tower_ir_cert_p2432 import (
        build_ir_cert_p2432_preview,
    )

    builders.update({
        2423: build_ir_cert_p2423_preview,
        2424: build_ir_cert_p2424_preview,
        2425: build_ir_cert_p2425_preview,
        2426: build_ir_cert_p2426_preview,
        2427: build_ir_cert_p2427_preview,
        2428: build_ir_cert_p2428_preview,
        2429: build_ir_cert_p2429_preview,
        2430: build_ir_cert_p2430_preview,
        2431: build_ir_cert_p2431_preview,
        2432: build_ir_cert_p2432_preview,
    })

    builder = builders.get(pack)

    if builder is None:
        abort(404)

    return builder()


def _walkthrough_cert_response(
    pack: int,
):
    require_owner_access()

    payload = _build_walkthrough_cert_payload(
        pack
    )

    return jsonify(payload)


def _register_walkthrough_cert_routes():
    for pack in range(2423, 2433):
        endpoint_name = (
            f"walkthrough_cert_pack_{pack}"
        )

        route = (
            f"/tower/ir-cert-v{pack}.json"
        )

        tower_ob_walkthrough_bp.add_url_rule(
            route,
            endpoint=endpoint_name,
            view_func=(
                lambda selected_pack=pack:
                _walkthrough_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_walkthrough_cert_routes()

# END TOWER OB WALKTHROUGH CERTIFICATION ROUTES

# BEGIN TOWER OB REAL SURFACE WALKTHROUGH INTEGRATION

from html import escape as _html_escape
from urllib.parse import urlencode as _urlencode

from tower.tower_ir_cert_p2433 import (
    REAL_ROOM_REGISTRY,
    real_room_by_id,
)


_REAL_SURFACE_QUERY_FLAG = (
    "tower_walkthrough"
)

_REAL_SURFACE_OPEN_ROUTE = (
    "/tower/observatory-walkthrough/"
    "open/<room_id>"
)


def _real_surface_room_for_path(
    path: str,
) -> Dict[str, Any] | None:
    normalized = (
        "/" + path.strip("/")
    )

    if normalized == "/dashboard":
        return real_room_by_id(
            "ob_room_dashboard"
        )

    if normalized == "/market-map":
        return real_room_by_id(
            "ob_room_market_map"
        )

    if normalized.startswith(
        "/ob/symbol/"
    ):
        return real_room_by_id(
            "ob_room_symbol_page"
        )

    if normalized == "/ob/trade-center":
        return real_room_by_id(
            "ob_room_trade_center"
        )

    if normalized == "/ob/review-center":
        return real_room_by_id(
            "ob_room_review_center"
        )

    if normalized == "/ob/owner-console":
        return real_room_by_id(
            "ob_room_owner_console"
        )

    return None


def _real_surface_path_for_room(
    room: Dict[str, Any],
    state: Dict[str, Any],
) -> str:
    if (
        room["room_id"]
        == "ob_room_symbol_page"
    ):
        receipt = state.get(
            "launch_receipt"
        )

        canonical_path = (
            receipt.get("canonical_path")
            if isinstance(
                receipt,
                dict,
            )
            else None
        )

        if (
            isinstance(
                canonical_path,
                str,
            )
            and canonical_path.startswith(
                "/symbol/"
            )
        ):
            symbol = canonical_path.rsplit(
                "/",
                1,
            )[-1]

            symbol = (
                symbol.strip().upper()
                or "AMD"
            )

            return (
                "/ob/symbol/"
                + symbol
            )

        return "/ob/symbol/AMD"

    return room["real_route"]


def _walkthrough_real_surface_url(
    *,
    room_id: str,
    walkthrough_id: str,
) -> str:
    return (
        "/tower/"
        "observatory-walkthrough/"
        f"open/{room_id}?"
        + _urlencode({
            "walkthrough_id": (
                walkthrough_id
            ),
        })
    )


def _walkthrough_room_position(
    room_id: str,
) -> int:
    for index, room in enumerate(
        REAL_ROOM_REGISTRY
    ):
        if room["room_id"] == room_id:
            return index

    return -1


def _walkthrough_next_room(
    room_id: str,
) -> Dict[str, Any] | None:
    position = (
        _walkthrough_room_position(
            room_id
        )
    )

    if position < 0:
        return None

    next_position = position + 1

    if next_position >= len(
        REAL_ROOM_REGISTRY
    ):
        return None

    return deepcopy(
        REAL_ROOM_REGISTRY[
            next_position
        ]
    )


def _real_surface_walkthrough_active(
    room: Dict[str, Any],
) -> bool:
    if not owner_access_allowed():
        return False

    if request.args.get(
        _REAL_SURFACE_QUERY_FLAG
    ) != "1":
        return False

    state = session.get(
        "tower_ob_walkthrough"
    )

    if not isinstance(
        state,
        dict,
    ):
        return False

    if state.get("stage") not in {
        "real_surface",
        "receipt_review",
    }:
        return False

    if (
        state.get("active_room_id")
        != room["room_id"]
    ):
        return False

    requested_walkthrough_id = (
        request.args.get(
            "walkthrough_id"
        )
    )

    if (
        requested_walkthrough_id
        and requested_walkthrough_id
        != state.get("walkthrough_id")
    ):
        return False

    receipt = state.get(
        "launch_receipt"
    )

    if not isinstance(
        receipt,
        dict,
    ):
        return False

    if (
        receipt.get("room_id")
        != room["room_id"]
    ):
        return False

    return True


def _tower_walkthrough_entry_html() -> str:
    return """
    <style id="tower-ob-walkthrough-entry-style">
    .tower-ob-walkthrough-entry {
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 2147483000;
        width: min(350px, calc(100vw - 32px));
        padding: 18px;
        border: 1px solid rgba(216,180,254,.28);
        border-radius: 18px;
        background:
            linear-gradient(
                145deg,
                rgba(36,27,66,.97),
                rgba(8,10,24,.98)
            );
        color: #f7f4ff;
        box-shadow: 0 24px 80px rgba(0,0,0,.48);
        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            sans-serif;
    }

    .tower-ob-walkthrough-entry strong {
        display: block;
        margin-bottom: 7px;
        font-size: 16px;
    }

    .tower-ob-walkthrough-entry p {
        margin: 0 0 14px;
        color: #c9c3dc;
        font-size: 13px;
        line-height: 1.45;
    }

    .tower-ob-walkthrough-entry a {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 42px;
        padding: 0 14px;
        border-radius: 12px;
        color: white;
        background:
            linear-gradient(
                135deg,
                #8b5cf6,
                #6d28d9
            );
        text-decoration: none;
        font-weight: 750;
        font-size: 13px;
    }
    </style>

    <aside
        class="tower-ob-walkthrough-entry"
        id="towerObWalkthroughEntry"
        aria-label="Observatory walkthrough"
    >
        <strong>
            Observatory protected run-through
        </strong>

        <p>
            Review and enter the six real OB rooms through
            Tower’s preview-only owner walkthrough.
        </p>

        <a href="/tower/observatory-walkthrough">
            Start Observatory walkthrough
        </a>
    </aside>
    """


def _real_surface_overlay_html(
    *,
    room: Dict[str, Any],
    state: Dict[str, Any],
) -> str:
    next_room = _walkthrough_next_room(
        room["room_id"]
    )

    walkthrough_id = str(
        state.get(
            "walkthrough_id",
            "",
        )
    )

    position = (
        _walkthrough_room_position(
            room["room_id"]
        )
        + 1
    )

    next_action = ""

    if next_room is not None:
        next_action = f"""
        <a
            class="tower-ob-guide-button"
            href="/tower/observatory-walkthrough/room/{_html_escape(next_room['room_id'])}"
        >
            Review next room:
            {_html_escape(next_room['display_name'])}
        </a>
        """

    else:
        next_action = """
        <a
            class="tower-ob-guide-button"
            href="/tower/observatory-walkthrough"
        >
            Return to walkthrough room list
        </a>
        """

    return f"""
    <style id="tower-ob-real-surface-guide-style">
    .tower-ob-real-surface-guide {{
        position: fixed;
        left: 18px;
        right: 18px;
        bottom: 18px;
        z-index: 2147483001;
        display: grid;
        grid-template-columns:
            minmax(0, 1fr) auto;
        gap: 18px;
        align-items: center;
        padding: 16px 18px;
        border: 1px solid rgba(216,180,254,.30);
        border-radius: 18px;
        background:
            linear-gradient(
                140deg,
                rgba(31,24,58,.98),
                rgba(7,9,21,.98)
            );
        box-shadow: 0 26px 90px rgba(0,0,0,.55);
        color: #f8f5ff;
        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            sans-serif;
    }}

    .tower-ob-guide-copy {{
        min-width: 0;
    }}

    .tower-ob-guide-eyebrow {{
        margin-bottom: 5px;
        color: #d8b4fe;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .14em;
        text-transform: uppercase;
    }}

    .tower-ob-guide-title {{
        font-size: 16px;
        font-weight: 850;
    }}

    .tower-ob-guide-detail {{
        margin-top: 4px;
        color: #c9c3dc;
        font-size: 12px;
        line-height: 1.4;
    }}

    .tower-ob-guide-actions {{
        display: flex;
        flex-wrap: wrap;
        justify-content: flex-end;
        gap: 9px;
    }}

    .tower-ob-guide-button {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 40px;
        padding: 0 13px;
        border: 1px solid rgba(216,180,254,.24);
        border-radius: 11px;
        color: white;
        background:
            linear-gradient(
                135deg,
                #8b5cf6,
                #6d28d9
            );
        text-decoration: none;
        font-size: 12px;
        font-weight: 780;
    }}

    .tower-ob-guide-button.secondary {{
        background: rgba(8,10,24,.88);
    }}

    @media (max-width: 760px) {{
        .tower-ob-real-surface-guide {{
            grid-template-columns: 1fr;
        }}

        .tower-ob-guide-actions {{
            justify-content: flex-start;
        }}
    }}
    </style>

    <aside
        class="tower-ob-real-surface-guide"
        id="towerObRealSurfaceGuide"
        data-room-id="{_html_escape(room['room_id'])}"
        data-walkthrough-id="{_html_escape(walkthrough_id)}"
        aria-label="Tower Observatory walkthrough guide"
    >
        <div class="tower-ob-guide-copy">
            <div class="tower-ob-guide-eyebrow">
                Tower protected walkthrough
            </div>

            <div class="tower-ob-guide-title">
                Room {position} of 6 ·
                {_html_escape(room['display_name'])}
            </div>

            <div class="tower-ob-guide-detail">
                You are viewing the real Observatory surface.
                Preview authority only. Existing OB safeguards
                remain active.
            </div>
        </div>

        <div class="tower-ob-guide-actions">
            <a
                class="tower-ob-guide-button secondary"
                href="/tower/observatory-walkthrough/receipt"
            >
                View launch receipt
            </a>

            {next_action}

            <form
                method="post"
                action="/tower/observatory-walkthrough/close"
                style="margin:0"
            >
                <button
                    class="tower-ob-guide-button secondary"
                    type="submit"
                    style="cursor:pointer"
                >
                    Close and lock back
                </button>
            </form>
        </div>
    </aside>
    """


def _inject_before_body_close(
    html: str,
    fragment: str,
) -> str:
    lower = html.lower()
    marker = "</body>"
    position = lower.rfind(marker)

    if position >= 0:
        return (
            html[:position]
            + fragment
            + html[position:]
        )

    return html + fragment


@tower_ob_walkthrough_bp.get(
    _REAL_SURFACE_OPEN_ROUTE
)
def walkthrough_open_real_surface(
    room_id: str,
):
    require_owner_access()

    room = real_room_by_id(
        room_id
    )

    if room is None:
        abort(404)

    state = walkthrough_state()

    receipt = state.get(
        "launch_receipt"
    )

    if not isinstance(
        receipt,
        dict,
    ):
        state["stage"] = "denied"
        state["denial_reason"] = (
            "tower_ob_real_surface_"
            "launch_receipt_missing"
        )
        save_walkthrough_state(
            state
        )

        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_denied"
            )
        )

    if (
        receipt.get("room_id")
        != room_id
    ):
        state["stage"] = "denied"
        state["denial_reason"] = (
            "tower_ob_real_surface_"
            "room_scope_mismatch"
        )
        save_walkthrough_state(
            state
        )

        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_denied"
            )
        )

    if (
        receipt.get(
            "default_deny_restored"
        )
        is not True
    ):
        state["stage"] = "denied"
        state["denial_reason"] = (
            "tower_ob_real_surface_"
            "lockback_not_verified"
        )
        save_walkthrough_state(
            state
        )

        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_denied"
            )
        )

    state["stage"] = "real_surface"
    state["real_surface_path"] = (
        _real_surface_path_for_room(
            room,
            state,
        )
    )
    state["real_surface_room_id"] = (
        room_id
    )
    state["real_surface_preview_only"] = (
        True
    )

    save_walkthrough_state(
        state
    )

    query = _urlencode({
        _REAL_SURFACE_QUERY_FLAG: "1",
        "walkthrough_id": state[
            "walkthrough_id"
        ],
        "tower_source": "walkthrough",
    })

    return redirect(
        state["real_surface_path"]
        + "?"
        + query
    )


@tower_ob_walkthrough_bp.after_app_request
def _inject_real_surface_walkthrough_ui(
    response,
):
    if response.status_code != 200:
        return response

    content_type = (
        response.headers.get(
            "Content-Type",
            "",
        )
    )

    if "text/html" not in content_type:
        return response

    try:
        html = response.get_data(
            as_text=True
        )
    except Exception:
        return response

    if request.path in {
        "/tower",
        "/tower/",
    }:
        if (
            "towerObWalkthroughEntry"
            not in html
        ):
            html = _inject_before_body_close(
                html,
                _tower_walkthrough_entry_html(),
            )

            response.set_data(
                html
            )

        return response

    room = _real_surface_room_for_path(
        request.path
    )

    if room is None:
        return response

    if not _real_surface_walkthrough_active(
        room
    ):
        return response

    if (
        "towerObRealSurfaceGuide"
        in html
    ):
        return response

    state = session.get(
        "tower_ob_walkthrough"
    )

    html = _inject_before_body_close(
        html,
        _real_surface_overlay_html(
            room=room,
            state=state,
        ),
    )

    response.set_data(html)

    return response


# Real-surface JSON certification routes

def _build_real_surface_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2433 import (
        build_ir_cert_p2433_preview,
    )
    from tower.tower_ir_cert_p2434 import (
        build_ir_cert_p2434_preview,
    )
    from tower.tower_ir_cert_p2435 import (
        build_ir_cert_p2435_preview,
    )
    from tower.tower_ir_cert_p2436 import (
        build_ir_cert_p2436_preview,
    )
    from tower.tower_ir_cert_p2437 import (
        build_ir_cert_p2437_preview,
    )
    from tower.tower_ir_cert_p2438 import (
        build_ir_cert_p2438_preview,
    )
    from tower.tower_ir_cert_p2439 import (
        build_ir_cert_p2439_preview,
    )
    from tower.tower_ir_cert_p2440 import (
        build_ir_cert_p2440_preview,
    )
    from tower.tower_ir_cert_p2441 import (
        build_ir_cert_p2441_preview,
    )
    from tower.tower_ir_cert_p2442 import (
        build_ir_cert_p2442_preview,
    )

    builders = {
        2433: build_ir_cert_p2433_preview,
        2434: build_ir_cert_p2434_preview,
        2435: build_ir_cert_p2435_preview,
        2436: build_ir_cert_p2436_preview,
        2437: build_ir_cert_p2437_preview,
        2438: build_ir_cert_p2438_preview,
        2439: build_ir_cert_p2439_preview,
        2440: build_ir_cert_p2440_preview,
        2441: build_ir_cert_p2441_preview,
        2442: build_ir_cert_p2442_preview,
    }

    builder = builders.get(pack)

    if builder is None:
        abort(404)

    return builder()


def _real_surface_cert_response(
    pack: int,
):
    require_owner_access()

    return jsonify(
        _build_real_surface_cert_payload(
            pack
        )
    )


def _register_real_surface_cert_routes():
    for pack in range(2433, 2443):
        tower_ob_walkthrough_bp.add_url_rule(
            f"/tower/ir-cert-v{pack}.json",
            endpoint=(
                f"real_surface_cert_pack_{pack}"
            ),
            view_func=(
                lambda selected_pack=pack:
                _real_surface_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_real_surface_cert_routes()

# END TOWER OB REAL SURFACE WALKTHROUGH INTEGRATION

# BEGIN TOWER OB GUIDED SIX ROOM RUN

import hashlib as _guided_hashlib
import json as _guided_json
from datetime import datetime as _guided_datetime
from datetime import timezone as _guided_timezone


_GUIDED_PROGRESS_KEY = (
    "tower_ob_guided_progress"
)

_GUIDED_ROOM_ORDER = [
    room["room_id"]
    for room in REAL_ROOM_REGISTRY
]


def _guided_now() -> str:
    return _guided_datetime.now(
        _guided_timezone.utc
    ).isoformat()


def _guided_hash(
    payload: Dict[str, Any],
) -> str:
    encoded = _guided_json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")

    return _guided_hashlib.sha256(
        encoded
    ).hexdigest()


def _new_guided_progress(
    walkthrough_id: str,
) -> Dict[str, Any]:
    return {
        "walkthrough_id": walkthrough_id,
        "guided_mode": True,
        "status": "in_progress",
        "started_at": _guided_now(),
        "updated_at": _guided_now(),
        "completed_room_ids": [],
        "room_receipts": {},
        "next_room_id": (
            _GUIDED_ROOM_ORDER[0]
        ),
        "completed_count": 0,
        "total_room_count": len(
            _GUIDED_ROOM_ORDER
        ),
        "final_receipt": None,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }


def _guided_progress(
    *,
    create: bool = False,
) -> Dict[str, Any] | None:
    progress = session.get(
        _GUIDED_PROGRESS_KEY
    )

    if isinstance(progress, dict):
        return progress

    if not create:
        return None

    state = walkthrough_state()

    progress = _new_guided_progress(
        state["walkthrough_id"]
    )

    _save_guided_progress(
        progress
    )

    return progress


def _save_guided_progress(
    progress: Dict[str, Any],
):
    progress["updated_at"] = (
        _guided_now()
    )

    progress["completed_count"] = len(
        progress.get(
            "completed_room_ids",
            [],
        )
    )

    session[
        _GUIDED_PROGRESS_KEY
    ] = progress

    session.modified = True

    _persist_guided_progress(
        progress
    )


def _guided_expected_room_id(
    progress: Dict[str, Any],
) -> str | None:
    completed = set(
        progress.get(
            "completed_room_ids",
            [],
        )
    )

    for room_id in (
        _GUIDED_ROOM_ORDER
    ):
        if room_id not in completed:
            return room_id

    return None


def _guided_room_receipt(
    *,
    room: Dict[str, Any],
    walkthrough_state_payload: Dict[str, Any],
    progress: Dict[str, Any],
) -> Dict[str, Any]:
    launch_receipt = (
        walkthrough_state_payload.get(
            "launch_receipt"
        )
    )

    receipt_source = {
        "walkthrough_id": (
            progress["walkthrough_id"]
        ),
        "room_id": room["room_id"],
        "display_name": (
            room["display_name"]
        ),
        "position": (
            _GUIDED_ROOM_ORDER.index(
                room["room_id"]
            )
            + 1
        ),
        "canonical_route": (
            room["real_route"]
        ),
        "completed_at": _guided_now(),
        "handoff_id": (
            launch_receipt.get(
                "handoff_id"
            )
            if isinstance(
                launch_receipt,
                dict,
            )
            else None
        ),
        "access_receipt_id": (
            launch_receipt.get(
                "access_receipt_id"
            )
            if isinstance(
                launch_receipt,
                dict,
            )
            else None
        ),
        "close_receipt_id": (
            launch_receipt.get(
                "close_receipt_id"
            )
            if isinstance(
                launch_receipt,
                dict,
            )
            else None
        ),
        "default_deny_restored": (
            launch_receipt.get(
                "default_deny_restored"
            )
            if isinstance(
                launch_receipt,
                dict,
            )
            else False
        ),
        "preview_only": True,
        "writes_state": False,
    }

    receipt_source[
        "room_completion_receipt_id"
    ] = (
        "obroomcomplete_"
        + _guided_hash(
            receipt_source
        )[:24]
    )

    return receipt_source


def _guided_final_receipt(
    progress: Dict[str, Any],
) -> Dict[str, Any]:
    ordered_receipts = [
        progress["room_receipts"][
            room_id
        ]
        for room_id in (
            _GUIDED_ROOM_ORDER
        )
    ]

    source = {
        "walkthrough_id": (
            progress["walkthrough_id"]
        ),
        "status": "completed",
        "completed_at": _guided_now(),
        "room_count": len(
            ordered_receipts
        ),
        "room_order": list(
            _GUIDED_ROOM_ORDER
        ),
        "room_completion_receipt_ids": [
            receipt[
                "room_completion_receipt_id"
            ]
            for receipt in ordered_receipts
        ],
        "all_default_deny_restored": all(
            receipt[
                "default_deny_restored"
            ]
            for receipt in ordered_receipts
        ),
        "broker_order_submission": False,
        "real_capital_movement": False,
        "production_manual_live_authorization": False,
        "live_auto_activation": False,
        "direct_vault_upload": False,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    source[
        "final_completion_receipt_id"
    ] = (
        "obguidedcomplete_"
        + _guided_hash(
            source
        )[:24]
    )

    source["integrity_hash"] = (
        _guided_hash(
            source
        )
    )

    return source


def _guided_progress_fragment(
    progress: Dict[str, Any],
) -> str:
    completed_count = len(
        progress.get(
            "completed_room_ids",
            [],
        )
    )

    total = len(
        _GUIDED_ROOM_ORDER
    )

    percent = int(
        completed_count
        / total
        * 100
    )

    status = progress.get(
        "status",
        "in_progress",
    )

    if status == "completed":
        action_url = (
            "/tower/"
            "observatory-walkthrough/"
            "final-receipt"
        )

        action_label = (
            "View final run receipt"
        )

    else:
        action_url = (
            "/tower/"
            "observatory-walkthrough/"
            "progress"
        )

        action_label = (
            "Resume guided run"
        )

    return f"""
    <style id="tower-ob-guided-progress-style">
    .tower-ob-guided-progress {{
        position: fixed;
        left: 24px;
        bottom: 24px;
        z-index: 2147482999;
        width: min(360px, calc(100vw - 32px));
        padding: 16px;
        border: 1px solid rgba(134,239,172,.25);
        border-radius: 17px;
        background:
            linear-gradient(
                145deg,
                rgba(12,37,29,.97),
                rgba(7,10,22,.98)
            );
        color: #f6fff9;
        box-shadow: 0 24px 80px rgba(0,0,0,.46);
        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            sans-serif;
    }}

    .tower-ob-guided-progress strong {{
        display: block;
        margin-bottom: 7px;
        font-size: 15px;
    }}

    .tower-ob-guided-progress p {{
        margin: 0 0 12px;
        color: #bfd6c7;
        font-size: 12px;
        line-height: 1.45;
    }}

    .tower-ob-guided-track {{
        height: 7px;
        overflow: hidden;
        margin-bottom: 13px;
        border-radius: 999px;
        background: rgba(255,255,255,.10);
    }}

    .tower-ob-guided-fill {{
        width: {percent}%;
        height: 100%;
        border-radius: inherit;
        background:
            linear-gradient(
                90deg,
                #22c55e,
                #86efac
            );
    }}

    .tower-ob-guided-progress a {{
        display: inline-flex;
        min-height: 39px;
        padding: 0 13px;
        align-items: center;
        justify-content: center;
        border-radius: 11px;
        background: #166534;
        color: white;
        font-size: 12px;
        font-weight: 800;
        text-decoration: none;
    }}
    </style>

    <aside
        class="tower-ob-guided-progress"
        id="towerObGuidedProgress"
    >
        <strong>
            Observatory guided run:
            {completed_count} of {total}
        </strong>

        <p>
            Status: {status.replace("_", " ")}.
            Preview-only owner walkthrough.
        </p>

        <div class="tower-ob-guided-track">
            <div
                class="tower-ob-guided-fill"
            ></div>
        </div>

        <a href="{action_url}">
            {action_label}
        </a>
    </aside>
    """


def _guided_room_action_fragment(
    *,
    room: Dict[str, Any],
    progress: Dict[str, Any],
) -> str:
    completed = set(
        progress.get(
            "completed_room_ids",
            [],
        )
    )

    expected_room_id = (
        _guided_expected_room_id(
            progress
        )
    )

    if room["room_id"] in completed:
        label = "Room already completed"
        disabled = "disabled"
        detail = (
            "This room already has a "
            "completion receipt."
        )

    elif (
        expected_room_id
        != room["room_id"]
    ):
        label = "Complete earlier rooms first"
        disabled = "disabled"
        detail = (
            "Guided sequence requires "
            "the next scheduled room."
        )

    else:
        label = "Mark room complete"
        disabled = ""
        detail = (
            "Create the room completion receipt "
            "and continue to the next room."
        )

    return f"""
    <style id="tower-ob-guided-room-action-style">
    .tower-ob-guided-room-action {{
        position: fixed;
        right: 18px;
        top: 18px;
        z-index: 2147483002;
        width: min(330px, calc(100vw - 36px));
        padding: 15px;
        border: 1px solid rgba(134,239,172,.28);
        border-radius: 16px;
        background: rgba(7,23,18,.97);
        color: #f3fff7;
        box-shadow: 0 20px 70px rgba(0,0,0,.48);
        font-family:
            Inter,
            ui-sans-serif,
            system-ui,
            sans-serif;
    }}

    .tower-ob-guided-room-action strong {{
        display: block;
        margin-bottom: 5px;
    }}

    .tower-ob-guided-room-action p {{
        margin: 0 0 11px;
        color: #bcd3c4;
        font-size: 12px;
        line-height: 1.4;
    }}

    .tower-ob-guided-room-action button {{
        min-height: 39px;
        padding: 0 13px;
        border: 0;
        border-radius: 11px;
        background: #15803d;
        color: white;
        font-weight: 800;
        cursor: pointer;
    }}

    .tower-ob-guided-room-action button:disabled {{
        opacity: .48;
        cursor: not-allowed;
    }}
    </style>

    <aside
        class="tower-ob-guided-room-action"
        id="towerObGuidedRoomAction"
    >
        <strong>
            Guided room {room["position"]} of 6
        </strong>

        <p>
            {detail}
        </p>

        <form
            method="post"
            action="/tower/observatory-walkthrough/progress/complete/{room['room_id']}"
        >
            <button
                type="submit"
                {disabled}
            >
                {label}
            </button>
        </form>
    </aside>
    """


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/guided-start"
)
def walkthrough_guided_start():
    require_owner_access()

    state = start_walkthrough_state()

    progress = _new_guided_progress(
        state["walkthrough_id"]
    )

    _save_guided_progress(
        progress
    )

    return redirect(
        url_for(
            "tower_ob_walkthrough."
            "walkthrough_room",
            room_id=(
                _GUIDED_ROOM_ORDER[0]
            ),
        )
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/progress"
)
def walkthrough_guided_progress():
    require_owner_access()

    progress = _guided_progress()

    if not isinstance(
        progress,
        dict,
    ):
        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_home"
            )
        )

    room_rows = []

    completed = set(
        progress.get(
            "completed_room_ids",
            [],
        )
    )

    expected = _guided_expected_room_id(
        progress
    )

    for room in REAL_ROOM_REGISTRY:
        if room["room_id"] in completed:
            status = "Completed"
            action = (
                "<span class='status good'>"
                "Receipt saved"
                "</span>"
            )

        elif room["room_id"] == expected:
            status = "Next room"
            action = f"""
            <a
                class="button"
                href="/tower/observatory-walkthrough/room/{room['room_id']}"
            >
                Continue
            </a>
            """

        else:
            status = "Locked in sequence"
            action = (
                "<span class='status'>"
                "Waiting"
                "</span>"
            )

        room_rows.append(f"""
        <section class="card">
            <h3>
                {room["position"]}.
                {room["display_name"]}
            </h3>

            <p>{status}</p>

            {action}
        </section>
        """)

    content = f"""
    <section class="hero">
        <h1>Guided Run Progress</h1>

        <p>
            Complete the six real Observatory rooms in
            sequence. Each room creates its own completion
            receipt before the next room opens.
        </p>

        <div class="status-row">
            <span class="status good">
                {progress["completed_count"]}
                of
                {progress["total_room_count"]}
                complete
            </span>

            <span class="status">
                {progress["status"]}
            </span>
        </div>
    </section>

    <div class="grid">
        {"".join(room_rows)}
    </div>

    <section class="card" style="margin-top:22px">
        <form
            method="post"
            action="/tower/observatory-walkthrough/progress/reset"
        >
            <button
                class="button secondary"
                type="submit"
            >
                Reset and start a new run
            </button>
        </form>
    </section>
    """

    return render_page(
        title="Observatory Guided Run Progress",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/"
    "progress/complete/<room_id>"
)
def walkthrough_guided_complete_room(
    room_id: str,
):
    require_owner_access()

    room = real_room_by_id(
        room_id
    )

    if room is None:
        abort(404)

    progress = _guided_progress()

    state = walkthrough_state()

    if not isinstance(
        progress,
        dict,
    ):
        abort(409)

    if progress.get(
        "status"
    ) == "completed":
        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_guided_final_receipt"
            )
        )

    expected_room_id = (
        _guided_expected_room_id(
            progress
        )
    )

    if expected_room_id != room_id:
        abort(409)

    if (
        state.get(
            "active_room_id"
        )
        != room_id
    ):
        abort(409)

    launch_receipt = state.get(
        "launch_receipt"
    )

    if not isinstance(
        launch_receipt,
        dict,
    ):
        abort(409)

    if (
        launch_receipt.get(
            "room_id"
        )
        != room_id
    ):
        abort(409)

    if (
        launch_receipt.get(
            "lockback_verified"
        )
        is not True
    ):
        abort(409)

    receipt = _guided_room_receipt(
        room=room,
        walkthrough_state_payload=state,
        progress=progress,
    )

    completed_room_ids = list(
        progress.get(
            "completed_room_ids",
            [],
        )
    )

    completed_room_ids.append(
        room_id
    )

    progress[
        "completed_room_ids"
    ] = completed_room_ids

    room_receipts = dict(
        progress.get(
            "room_receipts",
            {},
        )
    )

    room_receipts[room_id] = receipt

    progress["room_receipts"] = (
        room_receipts
    )

    next_room_id = (
        _guided_expected_room_id(
            progress
        )
    )

    progress["next_room_id"] = (
        next_room_id
    )

    if next_room_id is None:
        progress["status"] = "completed"

        progress["final_receipt"] = (
            _guided_final_receipt(
                progress
            )
        )

        _save_guided_progress(
            progress
        )

        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_guided_final_receipt"
            )
        )

    progress["status"] = "in_progress"

    _save_guided_progress(
        progress
    )

    state["stage"] = "room_selection"
    state["active_room_id"] = None
    state["launch_receipt"] = None

    save_walkthrough_state(
        state
    )

    return redirect(
        url_for(
            "tower_ob_walkthrough."
            "walkthrough_room",
            room_id=next_room_id,
        )
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/final-receipt"
)
def walkthrough_guided_final_receipt():
    require_owner_access()

    progress = _guided_progress()

    if not isinstance(
        progress,
        dict,
    ):
        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_home"
            )
        )

    final_receipt = progress.get(
        "final_receipt"
    )

    if not isinstance(
        final_receipt,
        dict,
    ):
        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_guided_progress"
            )
        )

    rows = []

    for room_id in (
        _GUIDED_ROOM_ORDER
    ):
        receipt = progress[
            "room_receipts"
        ][room_id]

        rows.append(f"""
        <section class="card receipt">
            <h3>
                {receipt["position"]}.
                {receipt["display_name"]}
            </h3>

            <div class="meta">
                <div>
                    <strong>Receipt:</strong>
                    {receipt["room_completion_receipt_id"]}
                </div>

                <div>
                    <strong>Completed:</strong>
                    {receipt["completed_at"]}
                </div>

                <div>
                    <strong>Default deny restored:</strong>
                    {receipt["default_deny_restored"]}
                </div>
            </div>
        </section>
        """)

    content = f"""
    <section class="hero">
        <h1>Six-Room Run Complete</h1>

        <p>
            The complete owner walkthrough passed across all
            six real Observatory surfaces. Every room has a
            completion receipt and the protected boundaries
            remained active.
        </p>

        <div class="status-row">
            <span class="status good">
                Six of six complete
            </span>

            <span class="status good">
                Default deny restored
            </span>

            <span class="status">
                Preview only
            </span>
        </div>
    </section>

    <section class="card receipt" style="margin-top:22px">
        <h2>Final completion receipt</h2>

        <div class="meta">
            <div>
                <strong>Receipt ID:</strong>
                {final_receipt["final_completion_receipt_id"]}
            </div>

            <div>
                <strong>Integrity hash:</strong>
                {final_receipt["integrity_hash"]}
            </div>

            <div>
                <strong>Completed:</strong>
                {final_receipt["completed_at"]}
            </div>

            <div>
                <strong>Room count:</strong>
                {final_receipt["room_count"]}
            </div>

            <div>
                <strong>All lockbacks verified:</strong>
                {final_receipt["all_default_deny_restored"]}
            </div>
        </div>
    </section>

    <div class="grid">
        {"".join(rows)}
    </div>

    <section class="card" style="margin-top:22px">
        <div class="actions">
            <a
                class="button"
                href="/tower"
            >
                Return to Tower
            </a>

            <form
                method="post"
                action="/tower/observatory-walkthrough/progress/reset"
            >
                <button
                    class="button secondary"
                    type="submit"
                >
                    Start a new run
                </button>
            </form>
        </div>
    </section>
    """

    return render_page(
        title="Observatory Six-Room Completion Receipt",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/progress/reset"
)
def walkthrough_guided_reset():
    require_owner_access()

    session.pop(
        _GUIDED_PROGRESS_KEY,
        None,
    )

    session.pop(
        "tower_ob_walkthrough",
        None,
    )

    session.modified = True

    return redirect(
        url_for(
            "tower_ob_walkthrough."
            "walkthrough_home"
        )
    )


@tower_ob_walkthrough_bp.after_app_request
def _inject_guided_run_controls(
    response,
):
    if response.status_code != 200:
        return response

    content_type = (
        response.headers.get(
            "Content-Type",
            "",
        )
    )

    if "text/html" not in content_type:
        return response

    try:
        html = response.get_data(
            as_text=True
        )
    except Exception:
        return response

    if not owner_access_allowed():
        return response

    progress = _guided_progress()

    if request.path in {
        "/tower",
        "/tower/",
    }:
        if (
            isinstance(
                progress,
                dict,
            )
            and "towerObGuidedProgress"
            not in html
        ):
            html = _inject_before_body_close(
                html,
                _guided_progress_fragment(
                    progress
                ),
            )

            response.set_data(
                html
            )

        return response

    if request.path == (
        "/tower/"
        "observatory-walkthrough"
    ):
        if (
            "towerObGuidedStart"
            not in html
        ):
            if isinstance(
                progress,
                dict,
            ):
                if progress.get(
                    "status"
                ) == "completed":
                    label = (
                        "View completed run"
                    )

                    action = (
                        "/tower/"
                        "observatory-walkthrough/"
                        "final-receipt"
                    )

                else:
                    label = (
                        "Resume guided six-room run"
                    )

                    action = (
                        "/tower/"
                        "observatory-walkthrough/"
                        "progress"
                    )

                fragment = f"""
                <section
                    class="card"
                    id="towerObGuidedStart"
                    style="margin-top:22px"
                >
                    <h2>Guided six-room owner run</h2>

                    <p>
                        Continue the ordered run with
                        room-by-room completion receipts.
                    </p>

                    <a
                        class="button"
                        href="{action}"
                    >
                        {label}
                    </a>
                </section>
                """

            else:
                fragment = """
                <section
                    class="card"
                    id="towerObGuidedStart"
                    style="margin-top:22px"
                >
                    <h2>Guided six-room owner run</h2>

                    <p>
                        Complete Dashboard, Market Map,
                        Symbol Page, Trade Center,
                        Review Center, and Owner Console
                        in order.
                    </p>

                    <form
                        method="post"
                        action="/tower/observatory-walkthrough/guided-start"
                    >
                        <button type="submit">
                            Start guided six-room run
                        </button>
                    </form>
                </section>
                """

            html = _inject_before_body_close(
                html,
                fragment,
            )

            response.set_data(
                html
            )

        return response

    if not isinstance(
        progress,
        dict,
    ):
        return response

    room = _real_surface_room_for_path(
        request.path
    )

    if room is None:
        return response

    if not _real_surface_walkthrough_active(
        room
    ):
        return response

    if (
        "towerObGuidedRoomAction"
        in html
    ):
        return response

    html = _inject_before_body_close(
        html,
        _guided_room_action_fragment(
            room=room,
            progress=progress,
        ),
    )

    response.set_data(
        html
    )

    return response


def _build_guided_run_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2443 import (
        build_ir_cert_p2443_preview,
    )
    from tower.tower_ir_cert_p2444 import (
        build_ir_cert_p2444_preview,
    )
    from tower.tower_ir_cert_p2445 import (
        build_ir_cert_p2445_preview,
    )
    from tower.tower_ir_cert_p2446 import (
        build_ir_cert_p2446_preview,
    )
    from tower.tower_ir_cert_p2447 import (
        build_ir_cert_p2447_preview,
    )
    from tower.tower_ir_cert_p2448 import (
        build_ir_cert_p2448_preview,
    )
    from tower.tower_ir_cert_p2449 import (
        build_ir_cert_p2449_preview,
    )
    from tower.tower_ir_cert_p2450 import (
        build_ir_cert_p2450_preview,
    )
    from tower.tower_ir_cert_p2451 import (
        build_ir_cert_p2451_preview,
    )
    from tower.tower_ir_cert_p2452 import (
        build_ir_cert_p2452_preview,
    )

    builders = {
        2443: build_ir_cert_p2443_preview,
        2444: build_ir_cert_p2444_preview,
        2445: build_ir_cert_p2445_preview,
        2446: build_ir_cert_p2446_preview,
        2447: build_ir_cert_p2447_preview,
        2448: build_ir_cert_p2448_preview,
        2449: build_ir_cert_p2449_preview,
        2450: build_ir_cert_p2450_preview,
        2451: build_ir_cert_p2451_preview,
        2452: build_ir_cert_p2452_preview,
    }

    builder = builders.get(pack)

    if builder is None:
        abort(404)

    return builder()


def _guided_run_cert_response(
    pack: int,
):
    require_owner_access()

    return jsonify(
        _build_guided_run_cert_payload(
            pack
        )
    )


def _register_guided_run_cert_routes():
    for pack in range(2443, 2453):
        tower_ob_walkthrough_bp.add_url_rule(
            f"/tower/ir-cert-v{pack}.json",
            endpoint=(
                f"guided_run_cert_pack_{pack}"
            ),
            view_func=(
                lambda selected_pack=pack:
                _guided_run_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_guided_run_cert_routes()

# END TOWER OB GUIDED SIX ROOM RUN

# BEGIN TOWER OB GUIDED RUN PERSISTENCE AND HISTORY

from tower.tower_observatory_walkthrough_store import (
    list_owner_runs as _store_list_owner_runs,
    load_guided_run as _store_load_guided_run,
    load_run_evidence as _store_load_run_evidence,
    save_guided_progress as _store_save_guided_progress,
    verify_owner_run as _store_verify_owner_run,
)


def _persist_guided_progress(
    progress: Dict[str, Any],
) -> Dict[str, Any] | None:
    owner_id = _owner_id()

    if not owner_id:
        return None

    return _store_save_guided_progress(
        owner_id=owner_id,
        progress=progress,
    )


def _history_status_label(
    status: str,
) -> str:
    return {
        "completed": "Completed",
        "in_progress": "In progress",
    }.get(
        status,
        status.replace("_", " ").title(),
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/history"
)
def walkthrough_guided_history():
    require_owner_access()

    runs = _store_list_owner_runs(
        owner_id=_owner_id(),
        limit=100,
    )

    cards = []

    for run in runs:
        action_label = (
            "View final evidence"
            if run["status"] == "completed"
            else "Resume run"
        )

        action_url = (
            "/tower/observatory-walkthrough/"
            f"history/{run['walkthrough_id']}"
        )

        cards.append(f"""
        <section class="card">
            <h3>
                {_history_status_label(run["status"])}
            </h3>

            <div class="meta">
                <div>
                    <strong>Run ID:</strong>
                    {run["walkthrough_id"]}
                </div>

                <div>
                    <strong>Progress:</strong>
                    {run["completed_count"]}
                    of
                    {run["total_room_count"]}
                </div>

                <div>
                    <strong>Updated:</strong>
                    {run["updated_at"]}
                </div>

                <div>
                    <strong>Next room:</strong>
                    {run["next_room_id"] or "Complete"}
                </div>
            </div>

            <div class="actions">
                <a
                    class="button"
                    href="{action_url}"
                >
                    {action_label}
                </a>
            </div>
        </section>
        """)

    empty_state = """
    <section class="card">
        <h2>No saved guided runs</h2>

        <p>
            Start a guided six-room run and Tower will
            preserve progress and completion receipts here.
        </p>
    </section>
    """

    content = f"""
    <section class="hero">
        <h1>Observatory Run History</h1>

        <p>
            Tower-owned walkthrough history with durable
            progress checkpoints, room receipts, final
            receipts, and integrity verification.
        </p>

        <div class="status-row">
            <span class="status good">
                {len(runs)} saved run{"s" if len(runs) != 1 else ""}
            </span>

            <span class="status">
                Owner only
            </span>

            <span class="status">
                No direct Vault write
            </span>
        </div>
    </section>

    <div class="grid">
        {"".join(cards) if cards else empty_state}
    </div>
    """

    return render_page(
        title="Observatory Guided Run History",
        content=content,
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "history/<walkthrough_id>"
)
def walkthrough_guided_history_detail(
    walkthrough_id: str,
):
    require_owner_access()

    evidence = _store_load_run_evidence(
        owner_id=_owner_id(),
        walkthrough_id=walkthrough_id,
    )

    if evidence is None:
        abort(404)

    run = evidence["run"]

    room_cards = []

    for receipt in evidence[
        "room_receipts"
    ]:
        payload = receipt["payload"]

        room_cards.append(f"""
        <section class="card receipt">
            <h3>
                {receipt["position"]}.
                {payload.get("display_name", receipt["room_id"])}
            </h3>

            <div class="meta">
                <div>
                    <strong>Receipt:</strong>
                    {receipt["receipt_id"]}
                </div>

                <div>
                    <strong>Completed:</strong>
                    {receipt["completed_at"]}
                </div>

                <div>
                    <strong>Integrity valid:</strong>
                    {receipt["integrity_valid"]}
                </div>
            </div>
        </section>
        """)

    verification = _store_verify_owner_run(
        owner_id=_owner_id(),
        walkthrough_id=walkthrough_id,
    )

    resume_action = ""

    if run["status"] != "completed":
        resume_action = f"""
        <form
            method="post"
            action="/tower/observatory-walkthrough/history/resume/{walkthrough_id}"
        >
            <button type="submit">
                Resume this run
            </button>
        </form>
        """

    final_detail = ""

    if evidence["final_receipt"]:
        final_detail = f"""
        <section class="card receipt" style="margin-top:22px">
            <h2>Final completion receipt</h2>

            <div class="meta">
                <div>
                    <strong>Receipt ID:</strong>
                    {evidence["final_receipt"]["receipt_id"]}
                </div>

                <div>
                    <strong>Completed:</strong>
                    {evidence["final_receipt"]["completed_at"]}
                </div>

                <div>
                    <strong>Integrity valid:</strong>
                    {evidence["final_receipt"]["integrity_valid"]}
                </div>
            </div>
        </section>
        """

    content = f"""
    <section class="hero">
        <h1>Guided Run Evidence</h1>

        <p>
            Durable Tower record for walkthrough
            {walkthrough_id}.
        </p>

        <div class="status-row">
            <span class="status good">
                {_history_status_label(run["status"])}
            </span>

            <span class="status good">
                Integrity verified:
                {verification["verified"]}
            </span>

            <span class="status">
                {run["completed_count"]}
                of
                {run["total_room_count"]}
            </span>
        </div>

        <div class="actions">
            {resume_action}

            <a
                class="button secondary"
                href="/tower/observatory-walkthrough/history"
            >
                Back to history
            </a>
        </div>
    </section>

    {final_detail}

    <div class="grid">
        {"".join(room_cards)}
    </div>
    """

    return render_page(
        title="Observatory Guided Run Evidence",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/"
    "history/resume/<walkthrough_id>"
)
def walkthrough_guided_history_resume(
    walkthrough_id: str,
):
    require_owner_access()

    stored = _store_load_guided_run(
        owner_id=_owner_id(),
        walkthrough_id=walkthrough_id,
    )

    if stored is None:
        abort(404)

    progress = stored["payload"]

    if progress.get(
        "status"
    ) == "completed":
        session[
            _GUIDED_PROGRESS_KEY
        ] = progress

        session[
            "tower_ob_walkthrough"
        ] = {
            "walkthrough_id": walkthrough_id,
            "owner_id": _owner_id(),
            "stage": "closed",
            "mode": "paper",
            "active_room_id": None,
            "launch_receipt": None,
            "close_receipt": None,
            "default_deny": True,
            "preview_only": True,
            "contract_only": True,
        }

        session.modified = True

        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_guided_final_receipt"
            )
        )

    next_room_id = (
        _guided_expected_room_id(
            progress
        )
    )

    progress["next_room_id"] = (
        next_room_id
    )

    session[
        _GUIDED_PROGRESS_KEY
    ] = progress

    session[
        "tower_ob_walkthrough"
    ] = {
        "walkthrough_id": walkthrough_id,
        "owner_id": _owner_id(),
        "stage": "room_selection",
        "mode": "paper",
        "active_room_id": None,
        "launch_receipt": None,
        "close_receipt": None,
        "default_deny": True,
        "preview_only": True,
        "contract_only": True,
    }

    session.modified = True

    if next_room_id is None:
        return redirect(
            url_for(
                "tower_ob_walkthrough."
                "walkthrough_guided_progress"
            )
        )

    return redirect(
        url_for(
            "tower_ob_walkthrough."
            "walkthrough_room",
            room_id=next_room_id,
        )
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "history/<walkthrough_id>/verify.json"
)
def walkthrough_guided_history_verify_json(
    walkthrough_id: str,
):
    require_owner_access()

    return jsonify(
        _store_verify_owner_run(
            owner_id=_owner_id(),
            walkthrough_id=walkthrough_id,
        )
    )


@tower_ob_walkthrough_bp.after_app_request
def _inject_guided_history_links(
    response,
):
    if response.status_code != 200:
        return response

    content_type = response.headers.get(
        "Content-Type",
        "",
    )

    if "text/html" not in content_type:
        return response

    if not owner_access_allowed():
        return response

    if request.path not in {
        "/tower",
        "/tower/",
        "/tower/observatory-walkthrough",
    }:
        return response

    try:
        html = response.get_data(
            as_text=True
        )
    except Exception:
        return response

    if "towerObGuidedHistoryLink" in html:
        return response

    fragment = """
    <aside
        id="towerObGuidedHistoryLink"
        style="
            position:fixed;
            right:24px;
            top:24px;
            z-index:2147483005;
            padding:12px;
            border:1px solid rgba(216,180,254,.24);
            border-radius:13px;
            background:rgba(8,10,24,.94);
            font-family:Inter,system-ui,sans-serif;
        "
    >
        <a
            href="/tower/observatory-walkthrough/history"
            style="
                color:#f5f3ff;
                text-decoration:none;
                font-size:12px;
                font-weight:800;
            "
        >
            Observatory run history
        </a>
    </aside>
    """

    response.set_data(
        _inject_before_body_close(
            html,
            fragment,
        )
    )

    return response


def _build_persistence_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2453 import (
        build_ir_cert_p2453_preview,
    )
    from tower.tower_ir_cert_p2454 import (
        build_ir_cert_p2454_preview,
    )
    from tower.tower_ir_cert_p2455 import (
        build_ir_cert_p2455_preview,
    )
    from tower.tower_ir_cert_p2456 import (
        build_ir_cert_p2456_preview,
    )
    from tower.tower_ir_cert_p2457 import (
        build_ir_cert_p2457_preview,
    )
    from tower.tower_ir_cert_p2458 import (
        build_ir_cert_p2458_preview,
    )
    from tower.tower_ir_cert_p2459 import (
        build_ir_cert_p2459_preview,
    )
    from tower.tower_ir_cert_p2460 import (
        build_ir_cert_p2460_preview,
    )
    from tower.tower_ir_cert_p2461 import (
        build_ir_cert_p2461_preview,
    )
    from tower.tower_ir_cert_p2462 import (
        build_ir_cert_p2462_preview,
    )

    builders = {
        2453: build_ir_cert_p2453_preview,
        2454: build_ir_cert_p2454_preview,
        2455: build_ir_cert_p2455_preview,
        2456: build_ir_cert_p2456_preview,
        2457: build_ir_cert_p2457_preview,
        2458: build_ir_cert_p2458_preview,
        2459: build_ir_cert_p2459_preview,
        2460: build_ir_cert_p2460_preview,
        2461: build_ir_cert_p2461_preview,
        2462: build_ir_cert_p2462_preview,
    }

    builder = builders.get(
        pack
    )

    if builder is None:
        abort(404)

    return builder()


def _persistence_cert_response(
    pack: int,
):
    require_owner_access()

    return jsonify(
        _build_persistence_cert_payload(
            pack
        )
    )


def _register_persistence_cert_routes():
    for pack in range(
        2453,
        2463,
    ):
        tower_ob_walkthrough_bp.add_url_rule(
            f"/tower/ir-cert-v{pack}.json",
            endpoint=(
                f"guided_persistence_cert_pack_{pack}"
            ),
            view_func=(
                lambda selected_pack=pack:
                _persistence_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_persistence_cert_routes()

# END TOWER OB GUIDED RUN PERSISTENCE AND HISTORY

# BEGIN TOWER OB PERSISTENCE OPERATIONS ROUTES

from tower.tower_observatory_walkthrough_store_ops import (
    corruption_recovery_assessment as _ops_corruption_assessment,
    create_backup_snapshot as _ops_create_backup_snapshot,
    ledger_health_check as _ops_ledger_health_check,
    owner_export_preview as _ops_owner_export_preview,
    retention_preview as _ops_retention_preview,
    validate_hosted_configuration as _ops_validate_configuration,
)


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "operations"
)
def walkthrough_persistence_operations():
    require_owner_access()

    configuration = (
        _ops_validate_configuration()
    )

    health = _ops_ledger_health_check()

    retention = _ops_retention_preview(
        owner_id=_owner_id()
    )

    recovery = (
        _ops_corruption_assessment()
    )

    content = f"""
    <section class="hero">
        <h1>Walkthrough Storage Operations</h1>

        <p>
            Tower-owned health, backup, retention, export,
            and recovery controls for Observatory guided-run
            evidence.
        </p>

        <div class="status-row">
            <span class="status {'good' if health['healthy'] else 'danger'}">
                Ledger healthy:
                {health["healthy"]}
            </span>

            <span class="status {'good' if configuration['ready'] else 'danger'}">
                Configuration ready:
                {configuration["ready"]}
            </span>

            <span class="status">
                No direct Vault write
            </span>
        </div>
    </section>

    <div class="grid">
        <section class="card">
            <h2>Ledger health</h2>

            <div class="meta">
                <div>
                    <strong>Database:</strong>
                    {health["database_path"]}
                </div>

                <div>
                    <strong>Runs:</strong>
                    {health["counts"]["runs"]}
                </div>

                <div>
                    <strong>Room receipts:</strong>
                    {health["counts"]["room_receipts"]}
                </div>

                <div>
                    <strong>Final receipts:</strong>
                    {health["counts"]["final_receipts"]}
                </div>
            </div>
        </section>

        <section class="card">
            <h2>Retention preview</h2>

            <div class="meta">
                <div>
                    <strong>Retention days:</strong>
                    {retention["retention_days"]}
                </div>

                <div>
                    <strong>Eligible completed runs:</strong>
                    {retention["eligible_count"]}
                </div>

                <div>
                    <strong>Automatic deletion:</strong>
                    False
                </div>
            </div>
        </section>

        <section class="card">
            <h2>Recovery status</h2>

            <div class="meta">
                <div>
                    <strong>Recommendation:</strong>
                    {recovery["recommendation"]}
                </div>

                <div>
                    <strong>Verified backups:</strong>
                    {recovery["verified_backup_count"]}
                </div>

                <div>
                    <strong>Automatic restore:</strong>
                    False
                </div>
            </div>
        </section>
    </div>

    <section class="card" style="margin-top:22px">
        <div class="actions">
            <form
                method="post"
                action="/tower/observatory-walkthrough/operations/backup"
            >
                <button type="submit">
                    Create verified backup
                </button>
            </form>

            <a
                class="button secondary"
                href="/tower/observatory-walkthrough/history"
            >
                View run history
            </a>
        </div>
    </section>
    """

    return render_page(
        title="Walkthrough Storage Operations",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/"
    "operations/backup"
)
def walkthrough_persistence_backup():
    require_owner_access()

    backup = _ops_create_backup_snapshot(
        label="owner"
    )

    content = f"""
    <section class="hero">
        <h1>Backup Created</h1>

        <p>
            Tower created a private SQLite snapshot and
            integrity manifest. Nothing was sent to Vault
            and no public link was created.
        </p>

        <div class="status-row">
            <span class="status good">
                Snapshot created
            </span>

            <span class="status good">
                SHA-256 recorded
            </span>
        </div>
    </section>

    <section class="card receipt" style="margin-top:22px">
        <div class="meta">
            <div>
                <strong>Backup path:</strong>
                {backup["backup_path"]}
            </div>

            <div>
                <strong>Manifest:</strong>
                {backup["manifest_path"]}
            </div>

            <div>
                <strong>SHA-256:</strong>
                {backup["manifest"]["sha256"]}
            </div>
        </div>

        <a
            class="button"
            href="/tower/observatory-walkthrough/operations"
        >
            Return to operations
        </a>
    </section>
    """

    return render_page(
        title="Walkthrough Backup Created",
        content=content,
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "history/<walkthrough_id>/export-preview.json"
)
def walkthrough_history_export_preview_json(
    walkthrough_id: str,
):
    require_owner_access()

    return jsonify(
        _ops_owner_export_preview(
            owner_id=_owner_id(),
            walkthrough_id=walkthrough_id,
        )
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "operations/health.json"
)
def walkthrough_operations_health_json():
    require_owner_access()

    return jsonify(
        _ops_ledger_health_check()
    )


def _build_persistence_ops_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2463 import (
        build_ir_cert_p2463_preview,
    )
    from tower.tower_ir_cert_p2464 import (
        build_ir_cert_p2464_preview,
    )
    from tower.tower_ir_cert_p2465 import (
        build_ir_cert_p2465_preview,
    )
    from tower.tower_ir_cert_p2466 import (
        build_ir_cert_p2466_preview,
    )
    from tower.tower_ir_cert_p2467 import (
        build_ir_cert_p2467_preview,
    )
    from tower.tower_ir_cert_p2468 import (
        build_ir_cert_p2468_preview,
    )
    from tower.tower_ir_cert_p2469 import (
        build_ir_cert_p2469_preview,
    )
    from tower.tower_ir_cert_p2470 import (
        build_ir_cert_p2470_preview,
    )
    from tower.tower_ir_cert_p2471 import (
        build_ir_cert_p2471_preview,
    )
    from tower.tower_ir_cert_p2472 import (
        build_ir_cert_p2472_preview,
    )

    builders = {
        2463: build_ir_cert_p2463_preview,
        2464: build_ir_cert_p2464_preview,
        2465: build_ir_cert_p2465_preview,
        2466: build_ir_cert_p2466_preview,
        2467: build_ir_cert_p2467_preview,
        2468: build_ir_cert_p2468_preview,
        2469: build_ir_cert_p2469_preview,
        2470: build_ir_cert_p2470_preview,
        2471: build_ir_cert_p2471_preview,
        2472: build_ir_cert_p2472_preview,
    }

    builder = builders.get(
        pack
    )

    if builder is None:
        abort(404)

    return builder()


def _persistence_ops_cert_response(
    pack: int,
):
    require_owner_access()

    return jsonify(
        _build_persistence_ops_cert_payload(
            pack
        )
    )


def _register_persistence_ops_cert_routes():
    for pack in range(
        2463,
        2473,
    ):
        tower_ob_walkthrough_bp.add_url_rule(
            f"/tower/ir-cert-v{pack}.json",
            endpoint=(
                f"persistence_ops_cert_pack_{pack}"
            ),
            view_func=(
                lambda selected_pack=pack:
                _persistence_ops_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_persistence_ops_cert_routes()

# END TOWER OB PERSISTENCE OPERATIONS ROUTES

# BEGIN TOWER OB HOSTED PERSISTENCE ASSURANCE ROUTES

from tower.tower_observatory_walkthrough_hosted_assurance import (
    backup_rotation_inventory as _assurance_backup_inventory,
    create_retention_approval_preview as _assurance_create_retention_approval,
    create_storage_incident_receipt as _assurance_create_incident,
    hosted_operations_readiness as _assurance_readiness,
    hosted_runtime_gate as _assurance_runtime_gate,
    startup_fail_closed_decision as _assurance_startup_decision,
)


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "operations/assurance"
)
def walkthrough_hosted_assurance_board():
    require_owner_access()

    runtime = _assurance_runtime_gate()

    startup = _assurance_startup_decision()

    backups = _assurance_backup_inventory()

    readiness = _assurance_readiness()

    blocker_rows = "".join(
        f"""
        <li>{blocker}</li>
        """
        for blocker in (
            readiness["blockers"]
        )
    )

    if not blocker_rows:
        blocker_rows = """
        <li>No current readiness blockers.</li>
        """

    content = f"""
    <section class="hero">
        <h1>Hosted Persistence Assurance</h1>

        <p>
            Owner view of runtime configuration, fail-closed
            startup, backup cadence, restore readiness,
            retention approval, and storage incidents.
        </p>

        <div class="status-row">
            <span class="status {'good' if readiness['ready'] else 'danger'}">
                {readiness["decision"]}
            </span>

            <span class="status {'good' if startup['allowed'] else 'danger'}">
                Startup allowed:
                {startup["allowed"]}
            </span>

            <span class="status">
                Fail closed
            </span>
        </div>
    </section>

    <div class="grid">
        <section class="card">
            <h2>Runtime gate</h2>

            <div class="meta">
                <div>
                    <strong>Ready:</strong>
                    {runtime["ready"]}
                </div>

                <div>
                    <strong>Hosted mode:</strong>
                    {runtime["hosted_mode"]}
                </div>

                <div>
                    <strong>Database environment:</strong>
                    {runtime["database_environment_present"]}
                </div>

                <div>
                    <strong>Backup environment:</strong>
                    {runtime["backup_environment_present"]}
                </div>
            </div>
        </section>

        <section class="card">
            <h2>Backup cadence</h2>

            <div class="meta">
                <div>
                    <strong>Backups:</strong>
                    {backups["backup_count"]}
                </div>

                <div>
                    <strong>Verified:</strong>
                    {backups["verified_backup_count"]}
                </div>

                <div>
                    <strong>Cadence ready:</strong>
                    {backups["cadence_ready"]}
                </div>

                <div>
                    <strong>Maximum age:</strong>
                    {backups["maximum_age_hours"]}
                    hours
                </div>
            </div>
        </section>

        <section class="card">
            <h2>Readiness blockers</h2>

            <ul>
                {blocker_rows}
            </ul>
        </section>
    </div>

    <section class="card" style="margin-top:22px">
        <div class="actions">
            <form
                method="post"
                action="/tower/observatory-walkthrough/operations/assurance/retention-preview"
            >
                <button type="submit">
                    Create retention approval preview
                </button>
            </form>

            <a
                class="button secondary"
                href="/tower/observatory-walkthrough/operations"
            >
                Storage operations
            </a>
        </div>
    </section>
    """

    return render_page(
        title="Hosted Persistence Assurance",
        content=content,
    )


@tower_ob_walkthrough_bp.get(
    "/tower/observatory-walkthrough/"
    "operations/assurance.json"
)
def walkthrough_hosted_assurance_json():
    require_owner_access()

    return jsonify(
        _assurance_readiness()
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/"
    "operations/assurance/retention-preview"
)
def walkthrough_retention_approval_preview():
    require_owner_access()

    approval = (
        _assurance_create_retention_approval(
            owner_id=_owner_id()
        )
    )

    content = f"""
    <section class="hero">
        <h1>Retention Approval Preview Created</h1>

        <p>
            Tower created an owner-decision record. No
            walkthrough runs were deleted.
        </p>

        <div class="status-row">
            <span class="status good">
                Preview saved
            </span>

            <span class="status">
                Cleanup performed:
                {approval["cleanup_performed"]}
            </span>
        </div>
    </section>

    <section class="card receipt" style="margin-top:22px">
        <div class="meta">
            <div>
                <strong>Approval ID:</strong>
                {approval["approval_id"]}
            </div>

            <div>
                <strong>Eligible count:</strong>
                {approval["record"]["eligible_count"]}
            </div>

            <div>
                <strong>Status:</strong>
                {approval["record"]["status"]}
            </div>

            <div>
                <strong>Record path:</strong>
                {approval["record_path"]}
            </div>
        </div>

        <a
            class="button"
            href="/tower/observatory-walkthrough/operations/assurance"
        >
            Return to assurance
        </a>
    </section>
    """

    return render_page(
        title="Retention Approval Preview",
        content=content,
    )


@tower_ob_walkthrough_bp.post(
    "/tower/observatory-walkthrough/"
    "operations/assurance/incident"
)
def walkthrough_storage_incident_create():
    require_owner_access()

    payload = request.get_json(
        silent=True
    ) or request.form.to_dict()

    incident = _assurance_create_incident(
        incident_type=payload.get(
            "incident_type",
            "storage_operations_review",
        ),
        severity=payload.get(
            "severity",
            "warning",
        ),
        summary=payload.get(
            "summary",
            "Owner-created storage operations incident.",
        ),
        evidence={
            "assurance": (
                _assurance_readiness()
            ),
        },
        owner_id=_owner_id(),
    )

    return jsonify(
        incident
    ), 201


def _build_hosted_assurance_cert_payload(
    pack: int,
) -> Dict[str, Any]:
    from tower.tower_ir_cert_p2473 import (
        build_ir_cert_p2473_preview,
    )
    from tower.tower_ir_cert_p2474 import (
        build_ir_cert_p2474_preview,
    )
    from tower.tower_ir_cert_p2475 import (
        build_ir_cert_p2475_preview,
    )
    from tower.tower_ir_cert_p2476 import (
        build_ir_cert_p2476_preview,
    )
    from tower.tower_ir_cert_p2477 import (
        build_ir_cert_p2477_preview,
    )
    from tower.tower_ir_cert_p2478 import (
        build_ir_cert_p2478_preview,
    )
    from tower.tower_ir_cert_p2479 import (
        build_ir_cert_p2479_preview,
    )
    from tower.tower_ir_cert_p2480 import (
        build_ir_cert_p2480_preview,
    )
    from tower.tower_ir_cert_p2481 import (
        build_ir_cert_p2481_preview,
    )
    from tower.tower_ir_cert_p2482 import (
        build_ir_cert_p2482_preview,
    )

    builders = {
        2473: build_ir_cert_p2473_preview,
        2474: build_ir_cert_p2474_preview,
        2475: build_ir_cert_p2475_preview,
        2476: build_ir_cert_p2476_preview,
        2477: build_ir_cert_p2477_preview,
        2478: build_ir_cert_p2478_preview,
        2479: build_ir_cert_p2479_preview,
        2480: build_ir_cert_p2480_preview,
        2481: build_ir_cert_p2481_preview,
        2482: build_ir_cert_p2482_preview,
    }

    builder = builders.get(
        pack
    )

    if builder is None:
        abort(404)

    return builder()


def _hosted_assurance_cert_response(
    pack: int,
):
    require_owner_access()

    return jsonify(
        _build_hosted_assurance_cert_payload(
            pack
        )
    )


def _register_hosted_assurance_cert_routes():
    for pack in range(
        2473,
        2483,
    ):
        tower_ob_walkthrough_bp.add_url_rule(
            f"/tower/ir-cert-v{pack}.json",
            endpoint=(
                f"hosted_assurance_cert_pack_{pack}"
            ),
            view_func=(
                lambda selected_pack=pack:
                _hosted_assurance_cert_response(
                    selected_pack
                )
            ),
            methods=["GET"],
        )


_register_hosted_assurance_cert_routes()

# END TOWER OB HOSTED PERSISTENCE ASSURANCE ROUTES
