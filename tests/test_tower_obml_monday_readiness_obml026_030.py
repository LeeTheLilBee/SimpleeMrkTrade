"""OBML026–030: Monday status is owner-only and never a launch grant."""
from __future__ import annotations

import ast
from pathlib import Path

from flask import Blueprint, Flask

from tower import obml_monday_owner_readiness as desk
from tower.tower_human_login_ob_launch import (
    SESSION_AUTHENTICATED, SESSION_OWNER_ID, SESSION_ROLE,
)

ROOT = Path(__file__).resolve().parents[1]
PINNED = ROOT / "pinned-obml-phase-source" / "web" / "ob_manual_live_l1_phase_contract.py"


def app_for_test():
    app = Flask(__name__)
    app.secret_key = "synthetic-test-only-owner-readiness-key"
    login = Blueprint("tower_human_login", __name__)

    @login.get("/tower/login")
    def login_view():
        return "Login"

    app.register_blueprint(login)
    desk.register_obml_monday_readiness(app)
    return app


def test_exact_main_phase_gate_ids_without_copying_a_new_policy():
    assert PINNED.is_file()
    parsed = ast.parse(PINNED.read_text(encoding="utf-8"))
    fields = {}
    for node in parsed.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in {
                "BEFORE_L1_MODE_ACCESS", "BEFORE_EACH_HUMAN_ORDER", "AFTER_HUMAN_ORDER",
            }:
                fields[target.id] = ast.literal_eval(node.value)
    assert fields["BEFORE_L1_MODE_ACCESS"] == desk.PRE_ACCESS
    assert fields["BEFORE_EACH_HUMAN_ORDER"] == desk.BEFORE_EACH_ORDER
    assert fields["AFTER_HUMAN_ORDER"] == desk.AFTER_HUMAN_ORDER


def test_anonymous_owner_readiness_redirects_to_real_tower_login(monkeypatch):
    monkeypatch.setattr(desk, "inspect_current_obml_owner_review",
                        lambda: (_ for _ in ()).throw(AssertionError("must not inspect anonymously")))
    app = app_for_test()
    client = app.test_client()
    result = client.get(desk.READINESS_PATH)
    assert result.status_code == 302
    assert "/tower/login" in result.headers["Location"]
    assert result.get_json(silent=True) is None


def test_owner_can_read_blockers_but_not_promote_an_optimistic_source(monkeypatch):
    app = app_for_test()
    monkeypatch.setattr(desk, "inspect_current_obml_owner_review", lambda: {
        "state": "READY", "reason_codes": [], "review_clearance_issued": True,
    })
    client = app.test_client()
    with client.session_transaction() as session:
        session[SESSION_AUTHENTICATED] = True
        session[SESSION_ROLE] = "owner"
        session[SESSION_OWNER_ID] = "synthetic-owner-ref"
    response = client.get(desk.READINESS_PATH + "?verified=1&activate=1")
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store, private"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    payload = response.get_json()
    assert payload["status"] == "HOLD_EXTERNAL_PROOF"
    assert payload["source_preflight_state"] == "BLOCKED"
    assert payload["target_date"] == "2026-09-28"
    assert payload["post_order_fill_is_not_required_for_first_review_access"] is True
    for name in (
        "owner_review_access_granted", "per_order_permission_granted",
        "real_manual_live_activated", "broker_api_enabled",
        "automatic_selection_enabled", "hybrid_live_auto_enabled",
        "capital_movement_authorized", "protected_floor_released",
        "paid_resources_provisioned",
    ):
        assert payload[name] is False
    assert "verified" not in payload
    assert "activate" not in payload


def test_read_only_route_rejects_post_and_is_idempotent():
    app = app_for_test()
    desk.register_obml_monday_readiness(app)
    rules = [r.rule for r in app.url_map.iter_rules()]
    assert rules.count(desk.READINESS_PATH) == 1
    response = app.test_client().post(desk.READINESS_PATH)
    assert response.status_code == 405


def test_payload_is_redacted_and_preflight_blocks_remain_visible(monkeypatch):
    monkeypatch.setattr(desk, "inspect_current_obml_owner_review", lambda: {
        "state": "BLOCKED",
        "reason_codes": ["OBML_PURPOSE_BOUND_STEP_UP_UNIMPLEMENTED", "BROKER_PROVENANCE_UNVERIFIED"],
    })
    payload = desk.owner_monday_readiness_payload()
    assert payload["tower_preflight_reason_codes"] == [
        "OBML_PURPOSE_BOUND_STEP_UP_UNIMPLEMENTED", "BROKER_PROVENANCE_UNVERIFIED",
    ]
    assert payload["brokerage_account_id_included"] is False
    assert payload["bank_balance_included"] is False
    assert payload["credentials_included"] is False
    assert payload["issuer_receipt_included"] is False
    assert payload["fallback"].endswith("NO_REAL_ORDER")


def test_malformed_source_reason_is_not_echoed_back(monkeypatch):
    monkeypatch.setattr(desk, "inspect_current_obml_owner_review", lambda: {
        "state": "BLOCKED",
        "reason_codes": ["sensitive/path/broker-token"],
    })
    report = desk.owner_monday_readiness_payload()
    assert report["tower_preflight_reason_codes"] == [
        "CANONICAL_TOWER_PREFLIGHT_UNAVAILABLE"
    ]


def test_hosted_app_mounts_only_a_readiness_get_and_not_a_trade_endpoint():
    source = (ROOT / "web" / "hosted_tower.py").read_text(encoding="utf-8")
    assert "register_obml_monday_readiness(app)" in source
    module = Path(desk.__file__).read_text(encoding="utf-8")
    assert "issue_owner_observatory_handoff(" not in module
    assert "broker.place_order" not in module
    assert "requests.post(" not in module
    assert desk.READINESS_PATH != "/tower/launch/observatory"
