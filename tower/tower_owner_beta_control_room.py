"""
Tower Owner-Beta Control Room / Packs 2553–2562.

This module creates the owner-beta command surface after the final
Tower–OB hosted staging readiness decision.

It is intentionally read-only and decision-support only.

It does not authorize:
- production deployment
- broker submission
- capital movement
- Manual Live
- Live Auto
- direct Vault write
- destructive action
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List


OWNER_BETA_CONTROL_ROOM_VERSION = "tower_owner_beta_control_room_v1"
OWNER_BETA_ROUTE = "/tower/owner-beta"
OWNER_BETA_JSON_ROUTE = "/tower/owner-beta.json"

CURRENT_STAGING_READY_DECISION = "STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH"
FINAL_STAGING_DECISION_COMMIT = "a9c72637822f644f1e6dd2b69d12638a37ec117d"
HOSTED_OWNER_WALKTHROUGH_COMMIT = "f97669c8b1dd9f2bfdb060c65eaa0a4f5f7d93cb"
CURRENT_MAIN_COMMIT = "bbd998e41668113b2a7cf722158e24855fe84915"

PRODUCTION_DEPLOYMENT = False
BROKER_SUBMISSION = False
CAPITAL_MOVEMENT = False
MANUAL_LIVE_AUTHORIZED = False
LIVE_AUTO_AUTHORIZED = False
DIRECT_VAULT_WRITE = False
DESTRUCTIVE_ACTION_UNLOCKED = False
PUBLIC_LAUNCH_AUTHORIZED = False

STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH = True
OWNER_BETA_CONTROL_ROOM_READY = True


@dataclass(frozen=True)
class BetaCard:
    card_id: str
    title: str
    status: str
    summary: str
    owner_action: str
    locked: bool = False


@dataclass(frozen=True)
class WalkthroughReceipt:
    receipt_id: str
    title: str
    commit: str
    status: str
    verified_items: List[str]


@dataclass(frozen=True)
class BetaBlocker:
    blocker_id: str
    title: str
    severity: str
    status: str
    owner_safe_summary: str
    next_action: str


@dataclass(frozen=True)
class ReadinessMatrixRow:
    app_id: str
    app_name: str
    tower_status: str
    beta_status: str
    owner_surface: str
    dangerous_controls_locked: bool


@dataclass(frozen=True)
class TesterAccessStatus:
    tester_group: str
    access_status: str
    mode_allowed: str
    notes: str
    owner_approval_required: bool


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dangerous_controls() -> Dict[str, bool]:
    return {
        "production_deployment": PRODUCTION_DEPLOYMENT,
        "broker_submission": BROKER_SUBMISSION,
        "capital_movement": CAPITAL_MOVEMENT,
        "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
        "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
        "direct_vault_write": DIRECT_VAULT_WRITE,
        "destructive_action_unlocked": DESTRUCTIVE_ACTION_UNLOCKED,
        "public_launch_authorized": PUBLIC_LAUNCH_AUTHORIZED,
    }


def hosted_staging_readiness_card() -> BetaCard:
    return BetaCard(
        card_id="hosted_staging_readiness",
        title="Hosted Staging Readiness",
        status="ready_for_owner_beta_walkthrough",
        summary=(
            "Tower–OB hosted staging has passed owner login, Access Home, "
            "Owner Console, App Registry, OB handoff, six-room acceptance, "
            "Tower return, session continuity, clearance continuity, and "
            "anonymous/default-deny checks."
        ),
        owner_action="Use hosted staging for owner beta walkthrough only.",
    )


def walkthrough_receipts() -> List[WalkthroughReceipt]:
    return [
        WalkthroughReceipt(
            receipt_id="final_staging_readiness_decision",
            title="Final Tower–OB Staging Readiness Decision",
            commit=FINAL_STAGING_DECISION_COMMIT,
            status="passed",
            verified_items=[
                "staging_ready_for_owner_beta_walkthrough",
                "dangerous_controls_locked",
                "no_production_deployment",
                "no_manual_live_authorization",
                "no_live_auto_authorization",
            ],
        ),
        WalkthroughReceipt(
            receipt_id="hosted_owner_walkthrough",
            title="Hosted Owner Walkthrough Verification",
            commit=HOSTED_OWNER_WALKTHROUGH_COMMIT,
            status="passed",
            verified_items=[
                "hosted_login",
                "anonymous_default_deny",
                "access_home",
                "owner_console",
                "app_registry",
                "ob_six_room_handoff",
                "tower_return",
                "owner_session_preservation",
                "clearance_preservation",
            ],
        ),
    ]


def beta_blockers() -> List[BetaBlocker]:
    return [
        BetaBlocker(
            blocker_id="manual_live_not_authorized",
            title="Manual Live Not Authorized",
            severity="critical_safety_hold",
            status="locked",
            owner_safe_summary=(
                "Owner beta/walkthrough is allowed, but Manual Live remains closed."
            ),
            next_action="Run separate Manual Live preparation gates only when owner explicitly requests.",
        ),
        BetaBlocker(
            blocker_id="production_not_authorized",
            title="Production Not Authorized",
            severity="critical_safety_hold",
            status="locked",
            owner_safe_summary=(
                "Hosted staging is ready for owner beta; production remains closed."
            ),
            next_action="Do not deploy production from this lane.",
        ),
        BetaBlocker(
            blocker_id="broker_capital_locked",
            title="Broker and Capital Actions Locked",
            severity="critical_safety_hold",
            status="locked",
            owner_safe_summary=(
                "Broker submission, capital movement, and Live Auto remain false."
            ),
            next_action="Keep all broker/capital controls gated behind future explicit owner authorization.",
        ),
    ]


def app_readiness_matrix() -> List[ReadinessMatrixRow]:
    return [
        ReadinessMatrixRow(
            app_id="tower",
            app_name="The Tower",
            tower_status="owner_beta_control_room_ready",
            beta_status="active_staging_owner_beta",
            owner_surface="Owner Beta Control Room",
            dangerous_controls_locked=True,
        ),
        ReadinessMatrixRow(
            app_id="observatory",
            app_name="The Observatory",
            tower_status="tower_front_door_verified",
            beta_status="survey_paper_owner_walkthrough_ready",
            owner_surface="OB six-room acceptance through Tower",
            dangerous_controls_locked=True,
        ),
        ReadinessMatrixRow(
            app_id="vault",
            app_name="Archive Vault",
            tower_status="sealed_infrastructure_only",
            beta_status="not_public_not_direct",
            owner_surface="Tower-controlled future surface only",
            dangerous_controls_locked=True,
        ),
        ReadinessMatrixRow(
            app_id="teller",
            app_name="The Teller",
            tower_status="future_workflow_integration",
            beta_status="not_active_in_this_pack",
            owner_surface="Future Tower/Teller workflow request surface",
            dangerous_controls_locked=True,
        ),
        ReadinessMatrixRow(
            app_id="clouds",
            app_name="The Clouds",
            tower_status="future_owner_summary_integration",
            beta_status="not_active_in_this_pack",
            owner_surface="Future owner command summary",
            dangerous_controls_locked=True,
        ),
        ReadinessMatrixRow(
            app_id="grounds",
            app_name="The Grounds",
            tower_status="future_real_estate_ops_integration",
            beta_status="not_active_in_this_pack",
            owner_surface="Future property operations lane",
            dangerous_controls_locked=True,
        ),
    ]


def ob_beta_gate_summary() -> List[BetaCard]:
    return [
        BetaCard(
            card_id="ob_mode_scope",
            title="OB Mode Scope",
            status="survey_paper_only",
            summary="Owner beta may review Survey/Paper surfaces only.",
            owner_action="Keep Manual Live closed until separate preparation gate.",
            locked=True,
        ),
        BetaCard(
            card_id="ob_six_rooms",
            title="OB Six-Room Acceptance",
            status="verified",
            summary="Dashboard, Market Map, Symbol Page, Trade Center, Review Center, and Owner Console are recognized through Tower.",
            owner_action="Use Tower walkthrough receipts to inspect beta quality.",
        ),
        BetaCard(
            card_id="soulaana_interpretation",
            title="Soulaana Interpretation Layer",
            status="owner_review_needed",
            summary="Soulaana should explain page meaning, beta blockers, and owner next actions without clutter.",
            owner_action="Review whether Soulaana feels clear enough for beta use.",
        ),
        BetaCard(
            card_id="market_map_deep_dives",
            title="Market Map Deep Dives",
            status="owner_review_needed",
            summary="Market Map should stay simple at top level and move detail into deep-dive drawers.",
            owner_action="Inspect whether the Market Map feels simpler than the old proof-heavy view.",
        ),
    ]


def tester_access_statuses() -> List[TesterAccessStatus]:
    return [
        TesterAccessStatus(
            tester_group="owner",
            access_status="allowed",
            mode_allowed="hosted_staging_owner_beta_walkthrough",
            notes="Owner may use Tower-hosted staging walkthrough surfaces.",
            owner_approval_required=False,
        ),
        TesterAccessStatus(
            tester_group="private_beta_testers",
            access_status="not_opened",
            mode_allowed="survey_paper_only_when_opened",
            notes="Tester access still requires explicit owner approval and Tower credential setup.",
            owner_approval_required=True,
        ),
        TesterAccessStatus(
            tester_group="anonymous_users",
            access_status="denied",
            mode_allowed="none",
            notes="Anonymous/default-deny remains required.",
            owner_approval_required=False,
        ),
        TesterAccessStatus(
            tester_group="non_owner_users",
            access_status="denied_until_invited",
            mode_allowed="none_without_tower_approval",
            notes="Non-owner beta access remains closed until owner opens tester lane.",
            owner_approval_required=True,
        ),
    ]


def owner_next_action_panel() -> List[BetaCard]:
    return [
        BetaCard(
            card_id="review_hosted_owner_beta",
            title="Review Hosted Owner Beta",
            status="next",
            summary="Walk through Tower Access Home, Owner Console, App Registry, and OB six-room acceptance.",
            owner_action="Use staging as owner and record anything confusing.",
        ),
        BetaCard(
            card_id="open_issue_intake",
            title="Open Issue Intake",
            status="ready",
            summary="Owner can record beta blockers, confusing surfaces, missing interpretation, or route/session issues.",
            owner_action="Add issue intake route in the next Tower beta pack if needed.",
        ),
        BetaCard(
            card_id="prepare_ob_manual_live_later",
            title="Prepare OB Manual Live Later",
            status="hold",
            summary="Manual Live prep is a future lane after owner beta review, not authorized here.",
            owner_action="Do not open Manual Live until separate owner decision gate.",
            locked=True,
        ),
    ]


def owner_issue_intake_schema() -> Dict[str, Any]:
    return {
        "schema_id": "tower_owner_beta_issue_intake_v1",
        "accepted_issue_types": [
            "confusing_surface",
            "missing_owner_context",
            "soulaana_interpretation_gap",
            "market_map_too_cluttered",
            "owner_console_control_location",
            "tower_ob_return_issue",
            "session_or_clearance_issue",
            "tester_access_question",
            "visual_polish",
        ],
        "required_fields": [
            "issue_type",
            "surface",
            "owner_summary",
            "severity",
            "desired_outcome",
        ],
        "storage_mode": "in_memory_contract_until_next_persistence_pack",
        "dangerous_actions_allowed": False,
    }


def owner_beta_payload() -> Dict[str, Any]:
    payload = {
        "version": OWNER_BETA_CONTROL_ROOM_VERSION,
        "generated_at": utc_now(),
        "routes": {
            "html": OWNER_BETA_ROUTE,
            "json": OWNER_BETA_JSON_ROUTE,
        },
        "decision": CURRENT_STAGING_READY_DECISION,
        "staging_ready_for_owner_beta_walkthrough": STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH,
        "owner_beta_control_room_ready": OWNER_BETA_CONTROL_ROOM_READY,
        "source_commits": {
            "main": CURRENT_MAIN_COMMIT,
            "hosted_owner_walkthrough": HOSTED_OWNER_WALKTHROUGH_COMMIT,
            "final_staging_readiness_decision": FINAL_STAGING_DECISION_COMMIT,
        },
        "cards": [
            asdict(hosted_staging_readiness_card()),
            *[asdict(card) for card in ob_beta_gate_summary()],
            *[asdict(card) for card in owner_next_action_panel()],
        ],
        "walkthrough_receipts": [
            asdict(receipt) for receipt in walkthrough_receipts()
        ],
        "owner_issue_intake_schema": owner_issue_intake_schema(),
        "beta_blockers": [
            asdict(blocker) for blocker in beta_blockers()
        ],
        "app_readiness_matrix": [
            asdict(row) for row in app_readiness_matrix()
        ],
        "tester_access_statuses": [
            asdict(status) for status in tester_access_statuses()
        ],
        "dangerous_controls": dangerous_controls(),
        "safety": {
            "production_deployment": PRODUCTION_DEPLOYMENT,
            "broker_submission": BROKER_SUBMISSION,
            "capital_movement": CAPITAL_MOVEMENT,
            "manual_live_authorized": MANUAL_LIVE_AUTHORIZED,
            "live_auto_authorized": LIVE_AUTO_AUTHORIZED,
            "direct_vault_write": DIRECT_VAULT_WRITE,
            "destructive_action_unlocked": DESTRUCTIVE_ACTION_UNLOCKED,
            "public_launch_authorized": PUBLIC_LAUNCH_AUTHORIZED,
        },
        "next_recommended_action": (
            "Use Owner Beta Control Room to review hosted staging, record blockers, "
            "and decide whether to open a private tester lane or prepare OB Manual Live gates."
        ),
    }

    return payload


def render_owner_beta_html() -> str:
    payload = owner_beta_payload()

    cards_html = "\n".join(
        f"""
        <section class="card">
          <div class="eyebrow">{card['status']}</div>
          <h2>{card['title']}</h2>
          <p>{card['summary']}</p>
          <div class="action">{card['owner_action']}</div>
        </section>
        """
        for card in payload["cards"]
    )

    blockers_html = "\n".join(
        f"""
        <li>
          <strong>{blocker['title']}</strong>
          <span>{blocker['severity']} · {blocker['status']}</span>
          <p>{blocker['owner_safe_summary']}</p>
        </li>
        """
        for blocker in payload["beta_blockers"]
    )

    matrix_html = "\n".join(
        f"""
        <tr>
          <td>{row['app_name']}</td>
          <td>{row['tower_status']}</td>
          <td>{row['beta_status']}</td>
          <td>{row['owner_surface']}</td>
        </tr>
        """
        for row in payload["app_readiness_matrix"]
    )

    # Keep this as a plain template, not an f-string. CSS braces must remain literal.
    template = """
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Tower Owner-Beta Control Room</title>
      <style>
        :root {
          color-scheme: dark;
          --bg: #06040d;
          --panel: rgba(24, 16, 48, 0.82);
          --panel2: rgba(11, 10, 24, 0.92);
          --gold: #f7d88a;
          --violet: #8f6cff;
          --text: #f8f2ff;
          --muted: #c7badf;
          --safe: #8ff7c0;
          --danger: #ff9ca8;
        }
        * { box-sizing: border-box; }
        body {
          margin: 0;
          min-height: 100vh;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background:
            radial-gradient(circle at top left, rgba(143,108,255,.22), transparent 32rem),
            radial-gradient(circle at bottom right, rgba(247,216,138,.12), transparent 28rem),
            var(--bg);
          color: var(--text);
        }
        main {
          width: min(1180px, calc(100vw - 32px));
          margin: 0 auto;
          padding: 40px 0 64px;
        }
        .hero {
          border: 1px solid rgba(247,216,138,.28);
          background: linear-gradient(135deg, rgba(24,16,48,.92), rgba(6,4,13,.94));
          border-radius: 28px;
          padding: 28px;
          box-shadow: 0 24px 80px rgba(0,0,0,.45);
        }
        .eyebrow {
          color: var(--gold);
          letter-spacing: .16em;
          text-transform: uppercase;
          font-size: .74rem;
          font-weight: 800;
        }
        h1 {
          margin: 10px 0 10px;
          font-size: clamp(2rem, 4vw, 4rem);
          line-height: .94;
        }
        h2 { margin: 8px 0 8px; }
        p {
          color: var(--muted);
          line-height: 1.55;
        }
        .status-row {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin-top: 20px;
        }
        .chip {
          border: 1px solid rgba(255,255,255,.14);
          background: rgba(255,255,255,.06);
          border-radius: 999px;
          padding: 9px 12px;
          color: var(--muted);
          font-size: .88rem;
        }
        .chip.ready {
          border-color: rgba(143,247,192,.42);
          color: var(--safe);
        }
        .grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 16px;
          margin-top: 18px;
        }
        .card {
          border: 1px solid rgba(255,255,255,.12);
          background: var(--panel);
          border-radius: 22px;
          padding: 20px;
        }
        .action {
          margin-top: 14px;
          border-top: 1px solid rgba(255,255,255,.1);
          padding-top: 12px;
          color: var(--gold);
          font-weight: 700;
        }
        .section {
          margin-top: 22px;
          border: 1px solid rgba(255,255,255,.1);
          background: var(--panel2);
          border-radius: 24px;
          padding: 22px;
        }
        ul { padding-left: 20px; }
        li {
          margin: 12px 0;
          color: var(--muted);
        }
        li strong {
          color: var(--text);
          display: block;
        }
        li span {
          color: var(--gold);
          font-size: .86rem;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          overflow: hidden;
          border-radius: 16px;
        }
        th, td {
          border-bottom: 1px solid rgba(255,255,255,.08);
          padding: 12px;
          text-align: left;
          color: var(--muted);
          vertical-align: top;
        }
        th {
          color: var(--gold);
          font-size: .8rem;
          letter-spacing: .08em;
          text-transform: uppercase;
        }
        code { color: var(--gold); }
      </style>
    </head>
    <body>
      <main>
        <section class="hero">
          <div class="eyebrow">Tower Owner-Beta Control Room</div>
          <h1>Owner beta is ready for walkthrough.</h1>
          <p>
            Hosted staging is cleared for owner beta/walkthrough use only.
            Manual Live, Live Auto, broker submission, capital movement,
            production deployment, direct Vault write, public launch, and
            destructive actions remain locked.
          </p>
          <div class="status-row">
            <div class="chip ready">Decision: __DECISION__</div>
            <div class="chip ready">Owner beta walkthrough ready</div>
            <div class="chip">Manual Live locked</div>
            <div class="chip">Production locked</div>
            <div class="chip">Capital locked</div>
          </div>
        </section>

        <section class="grid">
          __CARDS_HTML__
        </section>

        <section class="section">
          <div class="eyebrow">Beta blockers</div>
          <h2>Locked safety holds</h2>
          <ul>__BLOCKERS_HTML__</ul>
        </section>

        <section class="section">
          <div class="eyebrow">App readiness matrix</div>
          <h2>Ecosystem beta status</h2>
          <table>
            <thead>
              <tr>
                <th>App</th>
                <th>Tower status</th>
                <th>Beta status</th>
                <th>Owner surface</th>
              </tr>
            </thead>
            <tbody>__MATRIX_HTML__</tbody>
          </table>
        </section>

        <section class="section">
          <div class="eyebrow">Receipts</div>
          <h2>Source proof</h2>
          <p>Main: <code>__MAIN_COMMIT__</code></p>
          <p>Hosted walkthrough: <code>__HOSTED_WALKTHROUGH_COMMIT__</code></p>
          <p>Final readiness: <code>__FINAL_READINESS_COMMIT__</code></p>
        </section>
      </main>
    </body>
    </html>
    """

    return (
        template
        .replace("__DECISION__", payload["decision"])
        .replace("__CARDS_HTML__", cards_html)
        .replace("__BLOCKERS_HTML__", blockers_html)
        .replace("__MATRIX_HTML__", matrix_html)
        .replace("__MAIN_COMMIT__", payload["source_commits"]["main"])
        .replace("__HOSTED_WALKTHROUGH_COMMIT__", payload["source_commits"]["hosted_owner_walkthrough"])
        .replace("__FINAL_READINESS_COMMIT__", payload["source_commits"]["final_staging_readiness_decision"])
    )


def owner_beta_cert(pack_number: int) -> Dict[str, Any]:
    pack_titles = {
        2553: "Owner Beta Dashboard contract",
        2554: "Hosted staging readiness card",
        2555: "Walkthrough receipt viewer",
        2556: "Owner issue intake",
        2557: "Beta blocker tracker",
        2558: "App readiness matrix",
        2559: "OB beta gate summary",
        2560: "Tester access status surface",
        2561: "Owner next-action command panel",
        2562: "Safety certs and route/API integration",
    }

    payload = owner_beta_payload()

    return {
        "pack": pack_number,
        "title": pack_titles[pack_number],
        "status": "passed",
        "version": OWNER_BETA_CONTROL_ROOM_VERSION,
        "route": OWNER_BETA_ROUTE,
        "json_route": OWNER_BETA_JSON_ROUTE,
        "owner_beta_control_room_ready": OWNER_BETA_CONTROL_ROOM_READY,
        "staging_ready_for_owner_beta_walkthrough": STAGING_READY_FOR_OWNER_BETA_WALKTHROUGH,
        "dangerous_controls": dangerous_controls(),
        "dangerous_controls_locked": all(value is False for value in dangerous_controls().values()),
        "main_commit": CURRENT_MAIN_COMMIT,
        "final_staging_readiness_decision_commit": FINAL_STAGING_DECISION_COMMIT,
        "hosted_owner_walkthrough_commit": HOSTED_OWNER_WALKTHROUGH_COMMIT,
        "card_count": len(payload["cards"]),
        "blocker_count": len(payload["beta_blockers"]),
        "readiness_matrix_count": len(payload["app_readiness_matrix"]),
        "tester_status_count": len(payload["tester_access_statuses"]),
    }
