"""TWR-TEST006–010: dormant OB clearance must compile under hosted Python 3.11."""
from __future__ import annotations

import ast
from pathlib import Path

from tower import ob_mode_clearance as clearance

SOURCE = Path(clearance.__file__)


def test_ob_mode_clearance_parses_with_python_311_grammar():
    ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE), feature_version=(3, 11))


def test_unknown_mode_and_default_manual_live_remain_denied():
    unknown = clearance.evaluate_ob_mode_clearance(
        user_id="synthetic-owner", mode_name="unsupported", role="owner",
        user_clearance_level="critical",
    )
    assert unknown["allowed"] is False
    assert unknown["reason_code"] == "unknown_ob_mode"

    manual = clearance.evaluate_ob_mode_clearance(
        user_id="synthetic-owner", mode_name="manual", role="owner",
        user_clearance_level="critical", broker_connected=False,
        broker_healthy=False, live_authorized=False,
    )
    assert manual["allowed"] is False
    assert manual["reason_code"] in {
        "ob_mode_broker_not_ready", "ob_mode_live_authorization_missing",
    }


def test_soulaana_denied_action_and_low_clearance_strings_render_without_exception():
    denied_action = clearance.evaluate_ob_mode_clearance(
        user_id="synthetic-owner", mode_name="survey", role="owner",
        user_clearance_level="critical", action="execute",
    )
    assert denied_action["allowed"] is False
    assert "Survey Mode" in denied_action["soulaana_translation"]

    low = clearance.evaluate_ob_mode_clearance(
        user_id="synthetic-owner", mode_name="survey", role="owner",
        user_clearance_level="none",
    )
    assert low["allowed"] is False
    assert "Survey Mode" in low["soulaana_translation"]


def test_soulaana_allowed_mode_string_renders_but_does_not_grant_live(monkeypatch):
    monkeypatch.setattr(
        clearance, "evaluate_ob_route_clearance",
        lambda **kwargs: {"allowed": True, "decision": "allow"},
    )
    monkeypatch.setattr(
        clearance, "evaluate_ob_object_clearance",
        lambda **kwargs: {"allowed": True, "decision": "allow"},
    )
    result = clearance.evaluate_ob_mode_clearance(
        user_id="synthetic-owner", mode_name="survey", role="owner",
        user_clearance_level="critical", broker_connected=False,
        broker_healthy=False, live_authorized=False,
    )
    assert result["allowed"] is True
    assert "Survey Mode" in result["soulaana_translation"]
    assert clearance.MODE_CLEARANCE_POLICIES["survey"]["live_money_allowed"] is False
    assert clearance.MODE_CLEARANCE_POLICIES["paper"]["live_money_allowed"] is False
