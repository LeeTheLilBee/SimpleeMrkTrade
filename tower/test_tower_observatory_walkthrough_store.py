from pathlib import Path

from tower.tower_observatory_walkthrough_store import (
    list_owner_runs,
    load_guided_run,
    load_run_evidence,
    save_guided_progress,
    verify_owner_run,
)


def sample_progress(
    *,
    completed: bool = False,
):
    room_receipt = {
        "room_completion_receipt_id": (
            "obroomcomplete_test001"
        ),
        "room_id": "ob_room_dashboard",
        "display_name": "Dashboard",
        "position": 1,
        "completed_at": (
            "2026-07-14T12:00:00+00:00"
        ),
        "default_deny_restored": True,
        "preview_only": True,
        "writes_state": False,
    }

    progress = {
        "walkthrough_id": "obwalk_store_test",
        "guided_mode": True,
        "status": (
            "completed"
            if completed
            else "in_progress"
        ),
        "started_at": (
            "2026-07-14T11:00:00+00:00"
        ),
        "updated_at": (
            "2026-07-14T12:00:00+00:00"
        ),
        "completed_room_ids": [
            "ob_room_dashboard",
        ],
        "room_receipts": {
            "ob_room_dashboard": (
                room_receipt
            ),
        },
        "next_room_id": (
            None
            if completed
            else "ob_room_market_map"
        ),
        "completed_count": 1,
        "total_room_count": 6,
        "final_receipt": None,
        "preview_only": True,
        "contract_only": True,
        "writes_state": False,
    }

    if completed:
        progress["completed_room_ids"] = [
            "ob_room_dashboard",
            "ob_room_market_map",
            "ob_room_symbol_page",
            "ob_room_trade_center",
            "ob_room_review_center",
            "ob_room_owner_console",
        ]

        progress["completed_count"] = 6

        progress["room_receipts"] = {}

        for index, room_id in enumerate(
            progress[
                "completed_room_ids"
            ],
            start=1,
        ):
            progress["room_receipts"][
                room_id
            ] = {
                "room_completion_receipt_id": (
                    f"obroomcomplete_test{index:03d}"
                ),
                "room_id": room_id,
                "display_name": room_id,
                "position": index,
                "completed_at": (
                    "2026-07-14T12:00:00+00:00"
                ),
                "default_deny_restored": True,
                "preview_only": True,
                "writes_state": False,
            }

        progress["final_receipt"] = {
            "final_completion_receipt_id": (
                "obguidedcomplete_test001"
            ),
            "status": "completed",
            "completed_at": (
                "2026-07-14T13:00:00+00:00"
            ),
            "room_count": 6,
            "all_default_deny_restored": True,
            "preview_only": True,
            "contract_only": True,
            "writes_state": False,
        }

    return progress


def test_save_and_load_progress(tmp_path):
    database = (
        tmp_path / "walkthrough.sqlite3"
    )

    progress = sample_progress()

    saved = save_guided_progress(
        owner_id="owner_test",
        progress=progress,
        override=database,
    )

    assert saved["saved"] is True

    loaded = load_guided_run(
        owner_id="owner_test",
        walkthrough_id=(
            progress["walkthrough_id"]
        ),
        override=database,
    )

    assert loaded is not None
    assert loaded["status"] == "in_progress"
    assert loaded["completed_count"] == 1
    assert loaded["integrity_valid"] is True


def test_owner_history(tmp_path):
    database = (
        tmp_path / "walkthrough.sqlite3"
    )

    progress = sample_progress()

    save_guided_progress(
        owner_id="owner_test",
        progress=progress,
        override=database,
    )

    runs = list_owner_runs(
        owner_id="owner_test",
        override=database,
    )

    assert len(runs) == 1

    assert runs[0]["walkthrough_id"] == (
        "obwalk_store_test"
    )


def test_completed_evidence_and_verification(
    tmp_path,
):
    database = (
        tmp_path / "walkthrough.sqlite3"
    )

    progress = sample_progress(
        completed=True
    )

    save_guided_progress(
        owner_id="owner_test",
        progress=progress,
        override=database,
    )

    evidence = load_run_evidence(
        owner_id="owner_test",
        walkthrough_id=(
            progress["walkthrough_id"]
        ),
        override=database,
    )

    assert evidence is not None
    assert len(
        evidence["room_receipts"]
    ) == 6

    assert evidence[
        "final_receipt"
    ] is not None

    assert evidence[
        "integrity_valid"
    ] is True

    verification = verify_owner_run(
        owner_id="owner_test",
        walkthrough_id=(
            progress["walkthrough_id"]
        ),
        override=database,
    )

    assert verification["verified"] is True

    assert verification[
        "room_receipt_count"
    ] == 6

    assert verification[
        "final_receipt_present"
    ] is True
