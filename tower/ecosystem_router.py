"""Tower-owned Simplee World ecosystem routing fabric.

Clouds recommends where the owner should go. Tower validates every protected
crossing. Receiving apps keep their own business authority.

This module authorizes navigation only. It never authorizes trades, payroll,
payments, capital movement, Vault mutation, property operations, or ATM actions.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from datetime import timedelta
from html import escape
from urllib.parse import urlencode

from flask import Blueprint, Response, jsonify, redirect, request, session

from tower.ecosystem_destination_registry import (
    RUNTIME_CONTRACT_READY,
    RUNTIME_OPEN,
    RUNTIME_SUMMARY_ONLY,
    build_line_matrix,
    validate_launch_intent,
)
from tower.tower_clouds_native_launch import (
    CLOUDS_HOME_PATH,
    SESSION_OWNER_ID,
    SESSION_STEP_UP_UNTIL,
    TOWER_ACCESS_HOME_PATH,
    TOWER_LOGIN_PATH,
    _persist_tower_clouds_handoff,
    configured_step_up_minutes,
    owner_session_active,
    step_up_active,
    utc_now,
    utc_now_iso,
    verify_owner_credentials_from_session_password,
)


tower_ecosystem_bp = Blueprint(
    "tower_ecosystem_router",
    __name__,
)

SESSION_ECOSYSTEM_HANDOFF = "tower_ecosystem_handoff"
SESSION_ECOSYSTEM_RETURN = "tower_ecosystem_return_context"
SESSION_ECOSYSTEM_RETURN_RECEIPT = "tower_ecosystem_return_receipt"


def _owner_gate():
    if owner_session_active():
        return None
    return redirect(TOWER_LOGIN_PATH)


def _handoff_receipt(intent: dict) -> dict:
    owner_id = str(session.get(SESSION_OWNER_ID) or "").strip()
    nonce = secrets.token_urlsafe(18)
    created_at = utc_now_iso()

    material = "|".join(
        [
            owner_id,
            intent["app_id"],
            intent["destination"],
            intent.get("item", ""),
            intent.get("return_context", ""),
            nonce,
            created_at,
        ]
    )
    receipt_hash = hashlib.sha256(material.encode("utf-8")).hexdigest()

    return {
        "contract_type": "TowerEcosystemNavigationHandoff",
        "contract_version": intent["contract_version"],
        "handoff_id": "eco_" + receipt_hash[:24],
        "nonce": nonce,
        "owner_id": owner_id,
        "app_id": intent["app_id"],
        "app_label": intent["app_label"],
        "destination": intent["destination"],
        "destination_label": intent["destination_label"],
        "item": intent.get("item", ""),
        "target_route": intent.get("target_route"),
        "return_context": intent.get("return_context", ""),
        "created_at": created_at,
        "expires_at": (
            utc_now() + timedelta(minutes=10)
        ).isoformat(),
        "tower_authority_required": True,
        "owner_permission_verified": True,
        "step_up_verified": (
            True if intent["requires_step_up"] else None
        ),
        "one_time_crossing": True,
        "bearer_token_issued": False,
        "clouds_direct_bypass": False,
        "business_action_authorized": False,
        "capital_movement_authorized": False,
        "downstream_execution_performed": False,
    }


def _remember_return(intent: dict, receipt: dict) -> None:
    session[SESSION_ECOSYSTEM_HANDOFF] = receipt
    session[SESSION_ECOSYSTEM_RETURN] = {
        "origin_app": "clouds",
        "opened_app": intent["app_id"],
        "opened_destination": intent["destination"],
        "item": intent.get("item", ""),
        "return_context": intent.get("return_context", ""),
        "handoff_id": receipt["handoff_id"],
        "created_at": receipt["created_at"],
        "return_to": "clouds",
    }
    session.modified = True


def _panel_page(
    *,
    title: str,
    eyebrow: str,
    message: str,
    body: str = "",
    status: int = 200,
):
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title>
<style>
:root {{
  color-scheme:dark;
  --bg:#070711;
  --panel:rgba(23,19,39,.94);
  --line:rgba(255,255,255,.12);
  --text:#f8f4ff;
  --muted:#c9c0db;
  --violet:#b891ff;
  --gold:#f5cf7a;
  --good:#9ef0c0;
}}
* {{ box-sizing:border-box }}
body {{
  margin:0;
  min-height:100vh;
  background:
    radial-gradient(circle at 15% 10%,rgba(184,145,255,.25),transparent 34%),
    radial-gradient(circle at 82% 18%,rgba(245,207,122,.12),transparent 28%),
    var(--bg);
  font-family:Inter,system-ui,sans-serif;
  color:var(--text);
}}
.shell {{
  width:min(860px,calc(100% - 28px));
  margin:0 auto;
  padding:42px 0 80px;
}}
.eyebrow {{
  font-size:.75rem;
  letter-spacing:.16em;
  text-transform:uppercase;
  color:var(--gold);
  font-weight:900;
}}
.card {{
  margin-top:14px;
  border:1px solid var(--line);
  border-radius:26px;
  background:var(--panel);
  padding:28px;
  box-shadow:0 28px 90px rgba(0,0,0,.38);
}}
h1 {{
  font-size:clamp(2.1rem,7vw,4.5rem);
  line-height:.95;
  margin:10px 0 16px;
}}
p {{ color:var(--muted); line-height:1.6 }}
.actions {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:22px }}
a,.button,button {{
  display:inline-flex;
  min-height:46px;
  align-items:center;
  justify-content:center;
  padding:0 17px;
  border-radius:14px;
  border:1px solid var(--line);
  text-decoration:none;
  color:var(--text);
  font-weight:850;
  background:rgba(255,255,255,.07);
}}
.primary {{
  background:linear-gradient(135deg,var(--gold),var(--violet));
  color:#1a1028;
}}
.note {{
  margin-top:18px;
  padding:14px 16px;
  border:1px solid var(--line);
  border-radius:16px;
  background:rgba(255,255,255,.045);
}}
pre {{
  max-height:330px;
  overflow:auto;
  white-space:pre-wrap;
  color:var(--muted);
  background:#090812;
  padding:14px;
  border-radius:14px;
}}
</style>
</head>
<body>
<main class="shell">
<div class="eyebrow">{escape(eyebrow)}</div>
<section class="card">
<h1>{escape(title)}</h1>
<p>{escape(message)}</p>
{body}
<div class="actions">
<a class="primary" href="/clouds">Back to Clouds</a>
<a href="/tower/ecosystem/lines">Ecosystem lines</a>
<a href="/tower/access-home">Tower home</a>
</div>
</section>
</main>
</body>
</html>"""
    return Response(html, status=status, mimetype="text/html")


def _line_matrix_page() -> Response:
    rows = build_line_matrix()
    cards = []

    for row in rows:
        state = row["line_state"]

        if state == RUNTIME_OPEN:
            badge = "OPEN"
            badge_class = "good"
            explanation = "Launch, destination validation, and return corridor are available."
        elif state == RUNTIME_SUMMARY_ONLY:
            badge = "SUMMARY"
            badge_class = "watch"
            explanation = "A safe read line exists. The full operational owner room remains sealed."
        else:
            badge = "CONTRACT"
            badge_class = "wait"
            explanation = "Tower knows the destination contract. The receiving runtime is not connected yet."

        cards.append(
            f"""
            <article class="line-card">
              <div class="top">
                <div>
                  <div class="app">{escape(row['label'])}</div>
                  <div class="small">{escape(explanation)}</div>
                </div>
                <span class="badge {badge_class}">{badge}</span>
              </div>
              <div class="pills">
                <span>Feed · {escape(row['feed_state'])}</span>
                <span>Launch · {escape(row['launch_state'])}</span>
                <span>Deep link · {escape(row['deep_link_state'])}</span>
                <span>Return · {escape(row['return_state'])}</span>
              </div>
              <a class="open" href="{escape(row['launch_reference'])}">
                Open through Tower
              </a>
            </article>
            """
        )

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Simplee World Lines</title>
<style>
:root {{
  color-scheme:dark;
  --bg:#070711; --panel:#171327; --line:rgba(255,255,255,.12);
  --text:#f8f4ff; --muted:#c9c0db; --violet:#b891ff;
  --gold:#f5cf7a; --good:#9ef0c0; --wait:#ffd99a;
}}
* {{ box-sizing:border-box }}
body {{
  margin:0;
  background:
    radial-gradient(circle at 12% 8%,rgba(184,145,255,.20),transparent 34%),
    var(--bg);
  color:var(--text);
  font-family:Inter,system-ui,sans-serif;
}}
.shell {{ width:min(1100px,calc(100% - 28px)); margin:0 auto; padding:34px 0 70px }}
.hero {{
  padding:26px;
  border:1px solid var(--line);
  border-radius:26px;
  background:var(--panel);
}}
.eyebrow {{
  color:var(--gold);
  font-size:.74rem;
  font-weight:900;
  letter-spacing:.15em;
  text-transform:uppercase;
}}
h1 {{ font-size:clamp(2.3rem,6vw,4.6rem); line-height:.95; margin:10px 0 }}
p,.small {{ color:var(--muted); line-height:1.55 }}
.grid {{
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
  gap:14px;
  margin-top:16px;
}}
.line-card {{
  padding:18px;
  border:1px solid var(--line);
  border-radius:20px;
  background:rgba(23,19,39,.90);
}}
.top {{ display:flex; justify-content:space-between; gap:12px }}
.app {{ font-size:1.12rem; font-weight:900 }}
.badge {{
  height:max-content; padding:7px 9px; border-radius:999px;
  border:1px solid var(--line); font-size:.68rem; font-weight:950;
}}
.good {{ color:var(--good) }}
.watch {{ color:var(--violet) }}
.wait {{ color:var(--wait) }}
.pills {{ display:flex; flex-wrap:wrap; gap:7px; margin:15px 0 }}
.pills span {{
  padding:7px 9px; border-radius:999px; background:rgba(255,255,255,.055);
  font-size:.72rem; color:var(--muted);
}}
.open {{
  display:inline-flex; min-height:42px; align-items:center; padding:0 14px;
  border-radius:12px; background:linear-gradient(135deg,var(--gold),var(--violet));
  color:#1a1028; text-decoration:none; font-weight:900;
}}
.actions {{ display:flex; gap:10px; flex-wrap:wrap; margin-top:16px }}
.actions a {{ color:var(--text) }}
</style>
</head>
<body>
<main class="shell">
<section class="hero">
<div class="eyebrow">The Clouds × The Tower</div>
<h1>Ecosystem Lines</h1>
<p>
One glance: what Clouds can see, what Tower can launch,
and which receiving systems are still waiting on an operational runtime.
</p>
<div class="actions">
<a href="/clouds">← Clouds</a>
<a href="/tower/access-home">Tower home</a>
</div>
</section>
<section class="grid">{''.join(cards)}</section>
</main>
</body>
</html>"""
    return Response(html, mimetype="text/html")


@tower_ecosystem_bp.get("/tower/ecosystem/lines")
def ecosystem_lines():
    gate = _owner_gate()
    if gate is not None:
        return gate
    return _line_matrix_page()


@tower_ecosystem_bp.get("/tower/ecosystem/lines.json")
def ecosystem_lines_json():
    if not owner_session_active():
        return jsonify(
            {
                "allowed": False,
                "reason_code": "tower_owner_session_required",
                "default_deny": True,
            }
        ), 401

    rows = list(build_line_matrix())
    return jsonify(
        {
            "allowed": True,
            "contract_version": "tower-ecosystem-line-matrix-v1",
            "line_count": len(rows),
            "lines": rows,
            "clouds_direct_bypass_allowed": False,
            "downstream_execution_performed": False,
        }
    )


def _step_up_query(app_id: str) -> str:
    query = {}
    for key in ("destination", "item", "return_context"):
        value = request.args.get(key, "")
        if value:
            query[key] = value

    suffix = ("?" + urlencode(query)) if query else ""
    return f"/tower/ecosystem/step-up/{app_id}{suffix}"


@tower_ecosystem_bp.route(
    "/tower/ecosystem/step-up/<app_id>",
    methods=["GET", "POST"],
)
def ecosystem_step_up(app_id: str):
    gate = _owner_gate()
    if gate is not None:
        return gate

    intent = validate_launch_intent(
        app_id=app_id,
        destination=request.values.get("destination"),
        item=request.values.get("item"),
        return_context=request.values.get("return_context"),
    )

    if not intent.get("valid"):
        return jsonify(
            {
                "allowed": False,
                **intent,
                "default_deny": True,
                "downstream_execution_performed": False,
            }
        ), 403

    if request.method == "POST":
        password = str(request.form.get("password") or "")

        if not verify_owner_credentials_from_session_password(password):
            return _panel_page(
                title="Step-up did not pass",
                eyebrow="Tower protected crossing",
                message=(
                    "Your Tower session is still safe. "
                    "Re-enter the owner password to continue."
                ),
                status=403,
            )

        session[SESSION_STEP_UP_UNTIL] = (
            utc_now() + timedelta(minutes=configured_step_up_minutes())
        ).isoformat()
        session.modified = True

        query = {
            "destination": intent["destination"],
            "return_context": intent["return_context"],
        }
        if intent.get("item"):
            query["item"] = intent["item"]

        return redirect(
            f"/tower/ecosystem/launch/{intent['app_id']}?"
            + urlencode(query)
        )

    hidden = []
    for key in ("destination", "item", "return_context"):
        value = intent.get(key)
        if value:
            hidden.append(
                f'<input type="hidden" name="{escape(key)}" '
                f'value="{escape(str(value))}">'
            )

    body = f"""
    <form method="post">
      {''.join(hidden)}
      <div class="note">
        <strong>{escape(intent['app_label'])} · {escape(intent['destination_label'])}</strong>
        <p>Tower needs a fresh owner step-up before this crossing.</p>
      </div>
      <label style="display:grid;gap:8px;margin-top:18px">
        Owner password
        <input
          name="password"
          type="password"
          autocomplete="current-password"
          style="min-height:46px;border-radius:12px;border:1px solid rgba(255,255,255,.14);
          background:#090812;color:white;padding:0 12px"
        >
      </label>
      <div class="actions">
        <button class="button primary" type="submit">
          Authorize crossing
        </button>
      </div>
    </form>
    """

    return _panel_page(
        title="Tower step-up",
        eyebrow="Protected crossing",
        message=(
            "One quick check, then Tower will take you "
            "to the exact destination."
        ),
        body=body,
    )


def _launch_observatory(intent: dict):
    from tower import tower_observatory_walkthrough_web as ob

    room_id = intent.get("room_id")
    room = ob.room_by_id(room_id)

    if room is None:
        return _panel_page(
            title="Observatory destination unavailable",
            eyebrow="Tower default deny",
            message="Tower could not resolve that Observatory room.",
            status=403,
        )

    state = ob.start_walkthrough_state()
    form = {}

    if room_id == "ob_room_symbol_page" and intent.get("item"):
        form["symbol"] = intent["item"]

    context = ob.room_request_context(room, form)

    result = ob.run_protected_room_integration(
        requested_path=context["path"],
        mode="paper",
        object_context=context["object_context"],
        rehearsal_index=secrets.randbelow(900000) + 100000,
    )

    if result.get("status") != "passed":
        return _panel_page(
            title="Tower kept this room closed",
            eyebrow="Observatory protected crossing",
            message=str(
                result.get("decision_envelope", {}).get(
                    "reason_code",
                    "The Observatory launch gate did not pass.",
                )
            ),
            status=403,
        )

    state.update(
        {
            "stage": "receipt_review",
            "active_room_id": room_id,
            "ecosystem_return_context": intent.get("return_context", ""),
            "launch_receipt": {
                "room_id": room_id,
                "display_name": room["display_name"],
                "canonical_path": result["route_decision"]["canonical_path"],
                "handoff_id": result["handoff"]["handoff_id"],
                "access_receipt_id": result["access_receipt"]["receipt_id"],
                "close_receipt_id": result["close_receipt"]["close_receipt_id"],
                "clearance_value": result["clearance_decision"]["canonical_clearance_value"],
                "clearance_rank": result["clearance_decision"]["canonical_clearance_rank"],
                "step_up_state": result["access_receipt"]["step_up_state"],
                "completion_accepted": result["completion_intake"]["accepted"],
                "lockback_verified": result["lockback_verification"]["verified"],
                "final_access_state": result["close_receipt"]["ob_access_state"],
                "default_deny_restored": result["close_receipt"]["default_deny_restored"],
                "preview_only": True,
            },
        }
    )
    ob.save_walkthrough_state(state)

    return redirect(
        ob._walkthrough_real_surface_url(
            room_id=room_id,
            walkthrough_id=state["walkthrough_id"],
        )
    )


def _launch_vault_summary(intent: dict):
    try:
        from vault.headless_tower_status_bridge_layer_service import (
            get_headless_tower_status_bridge_home,
        )

        payload = get_headless_tower_status_bridge_home()
    except Exception as exc:
        return _panel_page(
            title="Vault summary line unavailable",
            eyebrow="Archive Vault",
            message=(
                "Tower kept Vault sealed because the safe summary "
                "adapter could not load."
            ),
            body=(
                '<div class="note">'
                + escape(type(exc).__name__)
                + "</div>"
            ),
            status=503,
        )

    safe_payload = json.dumps(payload, indent=2, sort_keys=True, default=str)

    return _panel_page(
        title="Vault summary line",
        eyebrow="Archive Vault · read-only",
        message=(
            "Tower opened only the narrow Vault status bridge. "
            "No raw evidence, upload, export approval, or Vault mutation is exposed."
        ),
        body=(
            '<details class="note">'
            '<summary>Safe status details</summary>'
            f'<pre>{escape(safe_payload)}</pre>'
            '</details>'
        ),
    )


@tower_ecosystem_bp.get("/tower/ecosystem/launch/<app_id>")
def ecosystem_launch(app_id: str):
    gate = _owner_gate()
    if gate is not None:
        return gate

    intent = validate_launch_intent(
        app_id=app_id,
        destination=request.args.get("destination"),
        item=request.args.get("item"),
        return_context=request.args.get("return_context"),
    )

    if not intent.get("valid"):
        return jsonify(
            {
                "allowed": False,
                **intent,
                "default_deny": True,
                "downstream_execution_performed": False,
            }
        ), 403

    if intent["requires_step_up"] and not step_up_active():
        return redirect(_step_up_query(intent["app_id"]))

    if intent["runtime_state"] == RUNTIME_CONTRACT_READY:
        return _panel_page(
            title="Connection contract is ready",
            eyebrow=intent["app_label"],
            message=(
                "Clouds knows where this work belongs and Tower knows "
                "how the crossing must work. The receiving runtime is "
                "not connected yet, so I did not fake a launch."
            ),
            status=409,
        )

    receipt = _handoff_receipt(intent)
    _remember_return(intent, receipt)

    if intent["runtime_state"] == RUNTIME_SUMMARY_ONLY:
        if intent["app_id"] == "archive_vault":
            return _launch_vault_summary(intent)

        return _panel_page(
            title="Summary line only",
            eyebrow=intent["app_label"],
            message=(
                "Tower has a narrow read line for this system, "
                "but the operational owner room is not open yet."
            ),
            status=409,
        )

    if intent["runtime_state"] != RUNTIME_OPEN:
        return _panel_page(
            title="Line unavailable",
            eyebrow="Tower default deny",
            message="This destination has no recognized runtime state.",
            status=503,
        )

    if intent["app_id"] == "tower":
        return redirect(TOWER_ACCESS_HOME_PATH)

    if intent["app_id"] == "clouds":
        _persist_tower_clouds_handoff()

        query = {}
        if intent.get("return_context"):
            query["resume"] = intent["return_context"]

        target = CLOUDS_HOME_PATH
        if query:
            target += "?" + urlencode(query)

        return redirect(target)

    if intent["app_id"] == "observatory":
        return _launch_observatory(intent)

    return _panel_page(
        title="Destination adapter missing",
        eyebrow="Tower default deny",
        message=(
            "The app is marked open, but Tower has no launch "
            "adapter for it. I kept the crossing closed."
        ),
        status=503,
    )


@tower_ecosystem_bp.get("/tower/ecosystem/handoff.json")
def ecosystem_handoff_json():
    if not owner_session_active():
        return jsonify(
            {
                "allowed": False,
                "reason_code": "tower_owner_session_required",
                "default_deny": True,
            }
        ), 401

    receipt = session.get(SESSION_ECOSYSTEM_HANDOFF)

    if not isinstance(receipt, dict):
        return jsonify(
            {
                "allowed": False,
                "reason_code": "ecosystem_handoff_missing",
                "default_deny": True,
            }
        ), 404

    return jsonify(
        {
            "allowed": True,
            "handoff": receipt,
            "default_deny": True,
            "downstream_execution_performed": False,
        }
    )


@tower_ecosystem_bp.get("/tower/ecosystem/return")
def ecosystem_return():
    gate = _owner_gate()
    if gate is not None:
        return gate

    context = session.pop(SESSION_ECOSYSTEM_RETURN, None)
    session.pop(SESSION_ECOSYSTEM_HANDOFF, None)

    if not isinstance(context, dict):
        return redirect(TOWER_ACCESS_HOME_PATH)

    receipt = {
        "receipt_type": "tower_ecosystem_return_receipt",
        "returned_from": context.get("opened_app"),
        "destination": context.get("opened_destination"),
        "return_context": context.get("return_context", ""),
        "handoff_id": context.get("handoff_id"),
        "returned_at": utc_now_iso(),
        "tower_session_preserved": True,
        "default_deny": True,
        "business_action_authorized": False,
        "downstream_execution_performed": False,
    }

    session[SESSION_ECOSYSTEM_RETURN_RECEIPT] = receipt
    session.modified = True

    _persist_tower_clouds_handoff()

    query = {
        "from": str(context.get("opened_app") or ""),
        "resume": str(context.get("return_context") or ""),
    }

    return redirect(
        CLOUDS_HOME_PATH + "?" + urlencode(query)
    )


@tower_ecosystem_bp.get("/tower/ecosystem/return-receipt.json")
def ecosystem_return_receipt_json():
    if not owner_session_active():
        return jsonify(
            {
                "allowed": False,
                "reason_code": "tower_owner_session_required",
                "default_deny": True,
            }
        ), 401

    receipt = session.get(SESSION_ECOSYSTEM_RETURN_RECEIPT)

    return jsonify(
        {
            "allowed": isinstance(receipt, dict),
            "receipt": receipt if isinstance(receipt, dict) else {},
            "default_deny": True,
            "downstream_execution_performed": False,
        }
    )


def _return_chip_html(context: dict) -> str:
    opened_app = str(context.get("opened_app") or "app")
    return_context = str(context.get("return_context") or "")

    return f"""
    <style id="tower-ecosystem-return-style">
    #towerEcosystemReturn {{
      position:fixed;
      right:18px;
      bottom:18px;
      z-index:2147483600;
      display:flex;
      gap:10px;
      align-items:center;
      max-width:min(460px,calc(100vw - 36px));
      padding:12px 14px;
      border-radius:16px;
      border:1px solid rgba(255,255,255,.16);
      background:rgba(9,8,18,.96);
      box-shadow:0 18px 60px rgba(0,0,0,.45);
      color:#f8f4ff;
      font-family:Inter,system-ui,sans-serif;
    }}
    #towerEcosystemReturn .copy {{ min-width:0 }}
    #towerEcosystemReturn .small {{ font-size:11px; color:#c9c0db }}
    #towerEcosystemReturn a {{
      white-space:nowrap;
      text-decoration:none;
      font-weight:900;
      color:#1a1028;
      background:linear-gradient(135deg,#f5cf7a,#b891ff);
      padding:10px 12px;
      border-radius:11px;
    }}
    </style>
    <aside
      id="towerEcosystemReturn"
      data-return-context="{escape(return_context)}"
    >
      <div class="copy">
        <strong>Opened from Clouds</strong>
        <div class="small">
          {escape(opened_app)} · Tower kept your place.
        </div>
      </div>
      <a href="/tower/ecosystem/return">Return to Clouds</a>
    </aside>
    """


@tower_ecosystem_bp.after_app_request
def inject_ecosystem_return(response: Response):
    try:
        context = session.get(SESSION_ECOSYSTEM_RETURN)

        if not isinstance(context, dict):
            return response

        if response.status_code != 200:
            return response

        if (
            request.path.startswith("/tower/")
            or request.path.startswith("/clouds")
        ):
            return response

        if "text/html" not in response.headers.get("Content-Type", ""):
            return response

        body = response.get_data(as_text=True)

        if 'id="towerEcosystemReturn"' in body:
            return response

        chip = _return_chip_html(context)
        position = body.lower().rfind("</body>")

        if position >= 0:
            body = body[:position] + chip + body[position:]
        else:
            body += chip

        response.set_data(body)
        response.headers["content-length"] = str(len(body.encode("utf-8")))

        return response

    except Exception:
        return response


def register_tower_ecosystem_router(app) -> None:
    if "tower_ecosystem_router" not in app.blueprints:
        app.register_blueprint(tower_ecosystem_bp)
