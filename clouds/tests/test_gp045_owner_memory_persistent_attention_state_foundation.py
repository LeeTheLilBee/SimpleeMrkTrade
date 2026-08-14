from pathlib import Path

import pytest

from clouds.owner_attention_memory_service import (
    OwnerAttentionMemoryStore,
    fingerprint_agenda_item,
    get_clouds_gp045_status_payload,
)

from clouds.executive_owner_agenda_service import (
    get_owner_agenda_items,
)


def test_gp045_fingerprint_is_deterministic():
    item = (
        get_owner_agenda_items()[0]
    )

    assert (
        fingerprint_agenda_item(item)
        == fingerprint_agenda_item(item)
    )

    assert (
        len(
            fingerprint_agenda_item(
                item
            )
        )
        == 64
    )


def test_gp045_persists_across_store_instances(
    tmp_path,
):
    path = (
        tmp_path
        / "memory.json"
    )

    item = (
        get_owner_agenda_items()[0]
    )

    first = (
        OwnerAttentionMemoryStore(
            path
        )
    )

    created = first.get_or_create(
        item,
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    second = (
        OwnerAttentionMemoryStore(
            path
        )
    )

    restored = second.get(
        item.agenda_item_id
    )

    assert restored == created


def test_gp045_corruption_fails_closed(
    tmp_path,
):
    path = (
        tmp_path
        / "memory.json"
    )

    item = (
        get_owner_agenda_items()[0]
    )

    store = (
        OwnerAttentionMemoryStore(
            path
        )
    )

    store.get_or_create(
        item,
        now_iso=(
            "2026-08-14T12:00:00Z"
        ),
    )

    text = path.read_text(
        encoding="utf-8"
    )

    path.write_text(
        text.replace(
            '"ledger_integrity_hash": "',
            '"ledger_integrity_hash": "tampered-',
            1,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        store.read_ledger()


def test_gp045_status_ready():
    status = (
        get_clouds_gp045_status_payload()
    )

    assert status["pack"] == "GP045"
    assert status["status"] == "ready"

    assert (
        status[
            "process_restart_roundtrip_verified"
        ]
        is True
    )

    assert (
        status[
            "corruption_rejection_verified"
        ]
        is True
    )

    assert (
        status[
            "hosted_persistent_storage_verified"
        ]
        is False
    )
