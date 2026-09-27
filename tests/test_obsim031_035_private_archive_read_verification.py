"""OBSIM031–035: private report-only recovery and complete terminal-chain denial."""
from datetime import timedelta
import json
from pathlib import Path

import pytest

from test_obsim016_020_on_demand_session import BASE, start, step
from web.ob_on_demand_simulation_session import (
    LocalSimulationReportStore, stop_session, tick_session,
)
from web.ob_multi_simulation_harness import stable_hash


def run_one(tmp_path):
    store = LocalSimulationReportStore(tmp_path / "owner-archive")
    session = tick_session(
        start(), step("F1"), now=BASE + timedelta(seconds=30), store=store,
    )
    return store, session


def test_obsim031_complete_archive_verifies_final_and_never_restores_a_live_session(tmp_path):
    store, active = run_one(tmp_path)
    pending = store.inspect_archive(active.session_id)
    assert pending["status"] == "INCOMPLETE_REPORT_ONLY"
    assert pending["tick_count"] == 1 and pending["final_report"] is None
    stopped = stop_session(active, now=BASE + timedelta(seconds=31), store=store)
    final = store.load_final(stopped.session_id)
    view = store.inspect_archive(stopped.session_id)
    assert view["status"] == "FINALIZED_REPORT_ONLY"
    assert view["final_report"] == final
    assert final["total_ticks"] == 1
    assert final["last_report_hash"] == view["reports"][0]["report_hash"]
    assert not view["in_memory_session_restored"]
    for flag in ("market_source_authenticated", "tower_owner_authenticated",
                 "broker_submission", "manual_live_unlock", "capital_movement"):
        assert view[flag] is False


def test_obsim032_refuse_report_symlink_and_private_file_permission_loss(tmp_path):
    store, active = run_one(tmp_path)
    report = store.root / active.session_id / "0001.json"
    outside = tmp_path / "outside.json"
    outside.write_bytes(report.read_bytes())
    report.unlink()
    report.symlink_to(outside)
    with pytest.raises(ValueError, match="symlinked"):
        store.load_ticks(active.session_id)
    report.unlink()
    report.write_bytes(outside.read_bytes())
    report.chmod(0o644)
    with pytest.raises(ValueError, match="private regular"):
        store.load_ticks(active.session_id)


def test_obsim032_refuse_root_or_session_symlink_and_permission_loss(tmp_path):
    store, active = run_one(tmp_path)
    store.root.chmod(0o755)
    with pytest.raises(ValueError, match="private"):
        store.load_ticks(active.session_id)
    store.root.chmod(0o700)
    directory = store.root / active.session_id
    directory.chmod(0o750)
    with pytest.raises(ValueError, match="private"):
        store.inspect_archive(active.session_id)
    directory.chmod(0o700)
    moved = store.root / "backup"
    directory.rename(moved)
    directory.symlink_to(moved, target_is_directory=True)
    with pytest.raises(ValueError, match="symlinked"):
        store.load_ticks(active.session_id)


def test_obsim033_wrong_final_tick_count_and_hash_chain_denied_even_with_rehash(tmp_path):
    store, active = run_one(tmp_path)
    stop_session(active, now=BASE + timedelta(seconds=31), store=store)
    terminal = store.root / active.session_id / "_final.json"
    original = json.loads(terminal.read_text())
    for mutation in (
        {"total_ticks": 0},
        {"last_report_hash": "0" * 64},
        {"lanes": {}},
        {"capital_movement": True},
    ):
        final = {**original, **mutation}
        final.pop("report_hash", None)
        final["report_hash"] = stable_hash(final)
        terminal.write_text(json.dumps(final))
        with pytest.raises(ValueError, match="final report integrity/chain"):
            store.load_final(active.session_id)
    terminal.write_text(json.dumps(original))
    assert store.load_final(active.session_id) == original


def test_obsim034_reject_duplicate_json_key_and_missing_sequence(tmp_path):
    store, active = run_one(tmp_path)
    report = store.root / active.session_id / "0001.json"
    original = report.read_text()
    report.write_text(original.replace('"sequence":1', '"sequence":1,"sequence":1'))
    with pytest.raises(ValueError, match="duplicate JSON key"):
        store.load_ticks(active.session_id)
    report.write_text(original)
    second = tick_session(
        active, step("F2", minute=1),
        now=BASE + timedelta(seconds=60), store=store,
    )
    assert len(store.load_ticks(second.session_id)) == 2
    report.unlink()
    with pytest.raises(ValueError, match="integrity/sequence"):
        store.load_ticks(second.session_id)


def test_obsim035_rehash_cannot_turn_simulation_receipt_into_execution(tmp_path):
    store, active = run_one(tmp_path)
    path = store.root / active.session_id / "0001.json"
    original = json.loads(path.read_text())
    for flag in ("broker_submission", "capital_movement", "manual_live_unlock",
                 "hybrid_unlock", "automated_unlock", "winner_selected"):
        changed = {**original, flag: True}
        changed.pop("report_hash", None)
        changed["report_hash"] = stable_hash(changed)
        path.write_text(json.dumps(changed))
        with pytest.raises(ValueError, match="integrity/sequence"):
            store.load_ticks(active.session_id)
        path.write_text(json.dumps(original))


def test_archive_missing_is_not_a_synthetic_empty_success(tmp_path):
    store = LocalSimulationReportStore(tmp_path / "missing")
    with pytest.raises(ValueError, match="archive missing"):
        store.inspect_archive("ABSENT")
