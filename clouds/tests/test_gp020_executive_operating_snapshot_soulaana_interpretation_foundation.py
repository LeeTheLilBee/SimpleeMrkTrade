import ast
from pathlib import Path

from clouds.executive_operating_snapshot_service import (
    get_clouds_gp020_status_payload,
    get_executive_operating_snapshot,
    get_executive_operating_snapshot_payload,
    get_executive_operating_source_cards,
)


def test_gp020_six_cards():
    assert len(
        get_executive_operating_source_cards()
    ) == 6


def test_gp020_soulaana_leads_with_explanation():
    snapshot = (
        get_executive_operating_snapshot()
    )

    assert snapshot.brief.headline
    assert snapshot.brief.explanation


def test_gp020_observatory_needs_owner():
    snapshot = (
        get_executive_operating_snapshot()
    )

    assert snapshot.brief.needs_you_now == (
        "The Observatory",
    )


def test_gp020_atm_is_watch():
    snapshot = (
        get_executive_operating_snapshot()
    )

    assert snapshot.brief.keep_watching == (
        "ATM Operations",
    )


def test_gp020_four_can_stay_background():
    snapshot = (
        get_executive_operating_snapshot()
    )

    assert snapshot.no_action_count == 4


def test_gp020_each_card_explains_everything():
    for card in (
        get_executive_operating_source_cards()
    ):
        assert card.what_it_means
        assert card.why_it_matters
        assert card.what_needs_attention
        assert card.what_can_wait
        assert card.owner_next_step


def test_gp020_no_raw_access():
    assert (
        get_executive_operating_snapshot()
        .raw_source_access_performed
        is False
    )


def test_gp020_no_execution():
    assert (
        get_executive_operating_snapshot()
        .downstream_execution_performed
        is False
    )


def test_gp020_payload():
    payload = (
        get_executive_operating_snapshot_payload()
    )

    assert payload["source_count"] == 6
    assert len(payload["source_cards"]) == 6


def test_gp020_status():
    status = get_clouds_gp020_status_payload()

    assert status["pack"] == "GP020"
    assert status["status"] == "ready"
    assert status["safe_to_continue"] is True
    assert status["source_count"] == 6
    assert status["action_required_count"] == 1
    assert status["watch_count"] == 1
    assert status["no_action_count"] == 4
    assert status["top_owner_focus"] == "observatory"
    assert status["watch_source"] == "atm_operations"


def test_gp020_no_cross_app_imports():
    root = Path(__file__).resolve().parents[2]

    files = (
        root / "clouds" / "executive_operating_snapshot.py",
        root / "clouds" / "executive_operating_snapshot_service.py",
    )

    forbidden = {
        "tower",
        "observatory",
        "vault",
        "teller",
        "grounds",
    }

    for path in files:
        tree = ast.parse(
            path.read_text(
                encoding="utf-8"
            )
        )

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert (
                        alias.name.split(".")[0].lower()
                        not in forbidden
                    )

            if isinstance(node, ast.ImportFrom):
                module = node.module or ""

                assert (
                    module.lstrip(".")
                    .split(".")[0]
                    .lower()
                    not in forbidden
                )
