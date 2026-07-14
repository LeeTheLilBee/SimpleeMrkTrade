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
                <button type="submit">
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
