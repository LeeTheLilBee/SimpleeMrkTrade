from __future__ import annotations

import pytest

from tower.ob_route_guard import should_block_ob_request


@pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS"])
def test_owner_can_view_unmapped_ob_surface(method):
    decision = should_block_ob_request(
        path="/ob/future-owner-room",
        user_id="tower-owner-solice-001",
        role="owner",
        user_clearance_level="critical",
        metadata={"method": method},
    )
    assert decision["allowed"] is True
    assert decision["block"] is False
    assert decision["reason_code"] == "ob_owner_blanket_view_allowed"
    assert decision["metadata"]["read_only_visibility"] is True


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_owner_blanket_visibility_does_not_bypass_mutation_gates(method):
    decision = should_block_ob_request(
        path="/ob/future-owner-room",
        user_id="tower-owner-solice-001",
        role="owner",
        user_clearance_level="critical",
        metadata={"method": method},
    )
    assert decision["allowed"] is False
    assert decision["block"] is True
    assert decision["reason_code"] == "ob_route_unmapped_default_deny"


def test_anonymous_user_remains_denied_on_mapped_surface():
    decision = should_block_ob_request(
        path="/market-map",
        user_id="anonymous",
        role="",
        user_clearance_level="",
        metadata={"method": "GET"},
    )
    assert decision["allowed"] is False
    assert decision["block"] is True


def test_non_owner_remains_subject_to_clearance_policy():
    decision = should_block_ob_request(
        path="/ob/owner-console",
        user_id="admin-1",
        role="admin",
        user_clearance_level="restricted",
        metadata={"method": "GET"},
    )
    assert decision["allowed"] is False
    assert decision["reason_code"] == "ob_clearance_level_too_low"


def test_web_identity_source_bridges_native_owner_session_keys():
    from pathlib import Path

    source = Path("web/app.py").read_text(encoding="utf-8")
    assert "# TOWER_OB_NATIVE_OWNER_IDENTITY_BRIDGE_V1" in source
    assert 'session.get("owner_id")' in source
    assert 'session.get("tower_role")' in source
    assert "owner_session_active" in source
    assert 'role = "owner"' in source
    assert 'clearance = "critical"' in source


def test_web_identity_source_disables_hosted_query_owner_spoofing():
    from pathlib import Path

    source = Path("web/app.py").read_text(encoding="utf-8")
    assert 'testing = bool(current_app.config.get("TESTING"))' in source
    assert ') if testing else None' in source
    assert 'native_owner_active' in source
