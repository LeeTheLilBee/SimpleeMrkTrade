"""OBSIM041–045: active local CLI is explicitly commanded, private and rehearsal-only."""
from datetime import timedelta
import json
from pathlib import Path

import pytest

from test_obsim016_020_on_demand_session import BASE
from test_obsim036_040_explicit_owner_rehearsal_input import payload
from scripts.ob_local_owner_rehearsal import (
    HELP, read_private_rehearsal_input, run_local_owner_rehearsal,
)
from web.ob_on_demand_simulation_session import LocalSimulationReportStore

ROOT = Path(__file__).resolve().parents[1]


def private_input(tmp_path, data):
    path = tmp_path / "owner-input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    path.chmod(0o600)
    return path


def clock_sequence(*instants):
    stream = iter(instants)
    return lambda: next(stream)


def commands(*lines):
    stream = iter(lines)
    return lambda _: next(stream)


def test_obsim041_active_owner_submits_explicit_private_historical_input(tmp_path):
    path = private_input(tmp_path, payload())
    messages = []
    archive = tmp_path / "archive"
    result = run_local_owner_rehearsal(
        ["--archive", str(archive), "--session-id", "OWNER-TEST",
         "--source-kind", "HISTORICAL"],
        input_fn=commands("status", "tick " + str(path), "stop"),
        clock=clock_sequence(
            BASE, BASE + timedelta(seconds=29),
            BASE + timedelta(seconds=30), BASE + timedelta(seconds=31),
        ), output=messages.append,
    )
    assert result == 0
    assert any("Tower owner identity NOT authenticated here" in line for line in messages)
    assert any("WAIT_INTERVAL" in line for line in messages)
    assert any("Accepted simulated tick 1" in line for line in messages)
    assert any("FINALIZED_REPORT_ONLY" in line for line in messages)
    saved = LocalSimulationReportStore(archive).inspect_archive("OWNER-TEST")
    assert saved["tick_count"] == 1
    assert saved["reports"][0]["source_kind"] == "HISTORICAL"
    assert saved["reports"][0]["simulation_only"] is True
    assert saved["broker_submission"] is False
    assert saved["tower_owner_authenticated"] is False


def test_obsim042_early_manual_command_never_writes_and_later_explicit_due_does(tmp_path):
    path = private_input(tmp_path, payload())
    archive = tmp_path / "archive"
    messages = []
    run_local_owner_rehearsal(
        ["--archive", str(archive), "--source-kind", "HISTORICAL"],
        input_fn=commands("tick " + str(path), "tick " + str(path), "stop"),
        clock=clock_sequence(
            BASE, BASE + timedelta(seconds=29),
            BASE + timedelta(seconds=30), BASE + timedelta(seconds=31),
        ), output=messages.append,
    )
    assert sum("Input rejected" in m for m in messages) == 1
    assert sum("Accepted simulated tick 1" in m for m in messages) == 1
    assert len(LocalSimulationReportStore(archive).load_ticks("LOCAL-OWNER-REHEARSAL")) == 1


def test_obsim043_untrusted_local_input_refused_without_leaking_it(tmp_path):
    sample = private_input(tmp_path, payload())
    assert read_private_rehearsal_input(sample)["account_key"] == "PROOF-DEMO"
    sample.chmod(0o644)
    with pytest.raises(ValueError, match="private regular"):
        read_private_rehearsal_input(sample)
    sample.chmod(0o600)
    alias = tmp_path / "symlink.json"
    alias.symlink_to(sample)
    with pytest.raises(ValueError, match="symlinked"):
        read_private_rehearsal_input(alias)
    sample.write_text('{"account_key":"PROOF-DEMO","account_key":"trust"}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        read_private_rehearsal_input(sample)
    sample.write_bytes(b' ' * 65537)
    with pytest.raises(ValueError, match="bounded local size"):
        read_private_rehearsal_input(sample)


def test_obsim044_static_example_requires_private_copy_and_is_labelled_synthetic(tmp_path):
    original = ROOT / "examples/obsim_owner_synthetic_hold_example.json"
    data = json.loads(original.read_text())
    assert data["source_kind"] == "SYNTHETIC"
    assert data["account_key"] == "PROOF-DEMO"
    assert data["calendar"]["calendar_authority"].startswith("OWNER_DECLARED_")
    assert "NOT-A-MARKET-FEED" in data["frame"]["source_reference"]
    copy = private_input(tmp_path, data)
    archive = tmp_path / "archive"
    messages = []
    run_local_owner_rehearsal(
        ["--archive", str(archive)],
        input_fn=commands("tick " + str(copy), "stop"),
        clock=clock_sequence(
            BASE, BASE + timedelta(seconds=30), BASE + timedelta(seconds=31),
        ), output=messages.append,
    )
    assert any("Accepted simulated tick 1" in m for m in messages)
    assert LocalSimulationReportStore(archive).load_ticks(
        "LOCAL-OWNER-REHEARSAL",
    )[0]["source_kind"] == "SYNTHETIC"


def test_obsim045_exit_is_report_only_not_a_scheduled_background_job(tmp_path):
    archive = tmp_path / "no-reports"
    output = []
    assert run_local_owner_rehearsal(
        ["--archive", str(archive)],
        input_fn=commands("exit"), clock=clock_sequence(BASE),
        output=output.append,
    ) == 0
    assert not archive.exists()
    assert any("incomplete" in line.lower() for line in output)
    source = (ROOT / "scripts/ob_local_owner_rehearsal.py").read_text()
    assert "time.sleep(" not in source
    assert "@app.route(" not in source
    assert "broker.place_order(" not in source
    assert "Commands: status" in HELP
