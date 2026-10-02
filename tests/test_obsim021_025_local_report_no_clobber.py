"""OBSIM021–025: local report publication must be private and never clobber."""
import json
import os
from pathlib import Path

import pytest

from web.ob_on_demand_simulation_session import LocalSimulationReportStore
from web.ob_multi_simulation_harness import stable_hash


def _report():
    base = {
        "session_id": "SOURCE-ONLY-001", "sequence": 1,
        "simulation_only": True, "broker_submission": False,
        "capital_movement": False, "lanes": {"CONTROL": {"equity": 10000}},
    }
    return {**base, "report_hash": stable_hash(base)}


def test_one_report_published_and_duplicate_never_replaced(tmp_path):
    root = tmp_path / "owner-private"
    store = LocalSimulationReportStore(root)
    report = _report()
    store.save_tick(report)
    target = root / report["session_id"] / "0001.json"
    original = target.read_bytes()
    assert store.load_ticks(report["session_id"]) == (report,)
    with pytest.raises(FileExistsError):
        store.save_tick({**report, "report_hash": "different"})
    assert target.read_bytes() == original
    assert not list(target.parent.glob(".pending-*.json"))


def test_racing_writer_cannot_replace_an_existing_report(tmp_path, monkeypatch):
    store = LocalSimulationReportStore(tmp_path)
    original_link = os.link
    marker = b'{"session":"already-published"}'

    def racing_link(source, destination, *args, **kwargs):
        Path(destination).write_bytes(marker)
        return original_link(source, destination, *args, **kwargs)

    monkeypatch.setattr(os, "link", racing_link)
    with pytest.raises(FileExistsError):
        store.save_tick(_report())
    destination = tmp_path / "SOURCE-ONLY-001" / "0001.json"
    assert destination.read_bytes() == marker
    assert not list(destination.parent.glob(".pending-*.json"))


def test_rejects_world_readable_archive_without_changing_permissions(tmp_path):
    root = tmp_path / "readable"
    root.mkdir(mode=0o700)
    root.chmod(0o755)
    store = LocalSimulationReportStore(root)
    with pytest.raises(ValueError, match="private"):
        store.save_tick(_report())
    assert not (root / "SOURCE-ONLY-001" / "0001.json").exists()
    assert root.stat().st_mode & 0o077


def test_rejects_symlinked_session_directory(tmp_path):
    root = tmp_path / "archive"
    root.mkdir(mode=0o700)
    outside = tmp_path / "outside"
    outside.mkdir(mode=0o700)
    (root / "SOURCE-ONLY-001").symlink_to(outside, target_is_directory=True)
    store = LocalSimulationReportStore(root)
    with pytest.raises(ValueError, match="symlinked"):
        store.save_tick(_report())
    assert not list(outside.glob("*.json"))


def test_no_background_timer_broker_or_public_host_added():
    import web.ob_on_demand_simulation_session as module
    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "os.replace(temporary, path)" not in source
    assert "os.link(temporary, path" in source
    assert "broker.place_order(" not in source
    assert "@app.route(" not in source
