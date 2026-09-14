
from __future__ import annotations

from pathlib import Path

from flask import Flask, session

from tower.access_home_owner_launches import (
    access_home_owner_launch_summary,
    access_home_owner_launches,
)
from tower.app_registry import registered_apps
from tower.owner_dashboard_service import (
    build_tower_owner_dashboard,
)
from tower.owner_people_registry import (
    owner_people_authority_snapshot,
    owner_people_records,
    person_by_id,
)
from tower.tower_access_home_ui_v2 import (
    APP_CARDS,
    record_ob_return_receipt,
    render_access_home_v2,
)
from tower.truth_surface_audit import (
    DEFERRED_TRUTH_DEBT_SURFACES,
    RETIREMENT_FOCUS_SURFACES,
    audit_product_surfaces,
)


REPO = Path("/content/SimpleeMrkTrade")


def test_twr126_no_sample_humans_remain_in_owner_people_truth():
    authority = owner_people_authority_snapshot()

    assert authority["verification_state"] == "NOT_CONFIGURED"
    assert authority["authoritative_provider_configured"] is False

    assert owner_people_records() == []
    assert person_by_id("owner-solice") is None

    source = (
        REPO
        / "tower/owner_people_registry.py"
    ).read_text(encoding="utf-8")

    assert "Future Manager Seat" not in source
    assert "Future Family / Friend Seat" not in source
    assert "Solice Bowdre" not in source


def test_twr126_missing_people_authority_does_not_become_zero():
    dashboard = build_tower_owner_dashboard()
    summary = dashboard["summary"]

    assert summary["people_count"] is None
    assert summary["invitation_count"] is None
    assert summary["pending_access_count"] is None

    assert summary["people_authority_state"] == "NOT_CONFIGURED"
    assert summary["invitation_authority_state"] == "NOT_CONFIGURED"
    assert summary["access_authority_state"] == "NOT_CONFIGURED"


def test_twr127_owner_headquarters_keeps_real_danger_locks():
    dashboard = build_tower_owner_dashboard()

    locks = dashboard["danger_locks"]

    assert locks["live_auto"] == "LOCKED"
    assert locks["broker_execution"] is False
    assert locks["capital_action"] is False
    assert locks["release_execution"] is False


def test_twr127_owner_dashboard_source_no_longer_routes_to_walkthrough():
    source = (
        REPO
        / "tower/owner_dashboard_web.py"
    ).read_text(encoding="utf-8")

    assert (
        'href="/tower/owner/release-review/walkthrough"'
        not in source
    )

    assert (
        'href="/tower/owner/release-review"'
        in source
    )

    assert (
        'href="/tower/owner/release-review/prerequisites"'
        in source
    )


def test_twr128_access_home_product_cards_only_show_ob():
    assert [
        card["id"]
        for card in APP_CARDS
    ] == [
        "observatory",
    ]

    source = (
        REPO
        / "tower/tower_access_home_ui_v2.py"
    ).read_text(encoding="utf-8")

    for prohibited in (
        "#vault-preview",
        "#teller-preview",
        "#grounds-preview",
        "#clouds-preview",
        "Simulate return",
        "Open walkthrough",
        "Evidence drawers",
        'href="/tower/security-map"',
        "/tower/observatory-walkthrough",
    ):
        assert prohibited not in source


def test_twr128_access_home_does_not_claim_runtime_availability():
    card = APP_CARDS[0]

    assert card["status"] == "Protected entry"
    assert card["href"] == "/tower/launch/observatory"

    assert "ready" not in card["status"].lower()
    assert "healthy" not in card["status"].lower()
    assert "available" not in card["status"].lower()


def test_twr128_rendered_access_home_has_no_product_theater():
    app = Flask(__name__)
    app.secret_key = "truthful-access-home-test"

    with app.test_request_context(
        "/tower/access-home"
    ):
        session["tower_authenticated"] = True
        session["tower_role"] = "owner"
        session["owner_id"] = "owner-test"
        session["tower_username"] = "Owner"

        body = render_access_home_v2(
            step_up_active=False,
            username="Owner",
        )

    assert "The Observatory" in body
    assert "Additional verification required" in body

    for prohibited in (
        "The Teller",
        "The Grounds",
        "The Clouds",
        "Archive Vault",
        "Preview",
        "Simulate return",
        "Evidence drawers",
        "Security Map",
    ):
        assert prohibited not in body


def test_twr128_real_return_receipt_can_be_projected_without_fake_return():
    app = Flask(__name__)
    app.secret_key = "truthful-return-test"

    with app.test_request_context(
        "/tower/access-home"
    ):
        session["tower_authenticated"] = True
        session["tower_role"] = "owner"
        session["owner_id"] = "owner-test"

        receipt = record_ob_return_receipt(
            source="observatory",
            last_room="/ob/dashboard",
        )

        assert receipt["owner_session_preserved"] is True
        assert receipt["broker_submission"] is False
        assert receipt["capital_movement"] is False
        assert receipt["manual_live_authorized"] is False
        assert receipt["live_auto_authorized"] is False

        body = render_access_home_v2(
            step_up_active=True,
            username="Owner",
        )

    assert "Verified return receipt" in body


def test_twr129_security_map_removed_from_primary_shortcut_set():
    launches = access_home_owner_launches()

    assert {
        launch["href"]
        for launch in launches
    } == {
        "/tower/owner-dashboard",
    }

    summary = access_home_owner_launch_summary()

    assert summary["launch_count"] == 1
    assert summary["people_authority_state"] == "NOT_CONFIGURED"


def test_twr129_future_apps_remain_registered_but_not_rendered():
    apps = {
        app["app_id"]: app
        for app in registered_apps()
    }

    assert apps["teller"]["app_status"] == "registered_future_room"
    assert apps["vault"]["app_status"] == "registered_future_room"
    assert apps["clouds"]["app_status"] == "registered_future_room"
    assert apps["grounds"]["app_status"] == "registered_future_room"

    assert [
        card["id"]
        for card in APP_CARDS
    ] == [
        "observatory",
    ]


def test_twr130_retirement_focus_has_zero_retire_or_review_findings():
    report = audit_product_surfaces(
        REPO,
        relative_paths=RETIREMENT_FOCUS_SURFACES,
    )

    assert report["finding_count"] == 0
    assert report["findings"] == []


def test_twr130_remaining_non_registry_debt_is_only_in_deferred_machinery():
    report = audit_product_surfaces(
        REPO
    )

    for finding in report["findings"]:
        if finding["severity"] == "KEEP_REGISTRY_HIDE_PRODUCT":
            continue

        assert (
            finding["relative_path"]
            in DEFERRED_TRUTH_DEBT_SURFACES
        )


def test_twr130_deferred_launcher_and_release_backend_still_exist():
    for relative in DEFERRED_TRUTH_DEBT_SURFACES:
        assert (
            REPO / relative
        ).is_file()
