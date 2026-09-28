"""TWR-OBML031–035: a configured handoff ledger is not durable/release proof."""
from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path

import pytest

from tower import ob_owner_replay_storage_audit as audit
from tower.owner_observatory_handoff import handoff_configuration_status


@pytest.fixture
def private_source_paths():
    # /tmp is deliberately disallowed for an operational hosted ledger.
    with tempfile.TemporaryDirectory(dir=Path.home()) as directory:
        root = Path(directory)
        root.chmod(0o700)
        mount = root / "mount"
        mount.mkdir(mode=0o700)
        private = mount / "private"
        private.mkdir(mode=0o700)
        yield mount, private / "handoff.sqlite3"


def check(path, mount, **kwargs):
    return audit.inspect_owner_ob_replay_storage(str(path), str(mount), **kwargs)


def test_structurally_private_and_synthetic_mount_remain_source_only(private_source_paths):
    mount, path = private_source_paths
    report = check(path, mount, mount_probe=lambda _: True)
    assert report["path_structure_valid"] is True
    assert report["mount_observed"] is True
    assert report["state"] == "SOURCE_PATH_REVIEW_ONLY"
    for key in (
        "provider_durability_verified", "backup_restore_verified",
        "cross_deploy_replay_verified", "owner_walkthrough_verified",
        "manual_live_authorized", "source_checks_are_release_authority",
        "may_issue_manual_live_grant", "secrets_exposed", "private_paths_exposed",
    ):
        assert report[key] is False
    rendered = json.dumps(report)
    assert str(mount) not in rendered
    assert str(path) not in rendered


def test_absolute_ledger_and_strong_secret_are_not_proof(monkeypatch):
    monkeypatch.setenv("TOWER_SESSION_SECRET", "synthetic-strong-key-0123456789-abcdefghijkl")
    monkeypatch.setenv("TOWER_OB_HANDOFF_LEDGER_PATH", "/tmp/tower-owner-ob.sqlite3")
    assert handoff_configuration_status()["configured"] is True
    report = audit.inspect_owner_ob_replay_storage(
        os.environ["TOWER_OB_HANDOFF_LEDGER_PATH"], "/tmp",
        mount_probe=lambda _: True,
    )
    assert "EPHEMERAL_RUNTIME_PATH_REJECTED" in report["reason_codes"]
    assert report["provider_durability_verified"] is False
    assert report["cross_deploy_replay_verified"] is False


@pytest.mark.parametrize("path,mount,reason", [
    ("", "/mnt/durable", "LEDGER_PATH_NOT_CONFIGURED"),
    ("/mnt/durable/ledger.sqlite3", "", "APPROVED_DURABLE_MOUNT_NOT_PROVIDED"),
    ("relative/ledger.sqlite3", "/mnt/durable", "ABSOLUTE_UNAMBIGUOUS_PRIVATE_PATHS_REQUIRED"),
    ("/mnt/durable/../other.sqlite3", "/mnt/durable", "ABSOLUTE_UNAMBIGUOUS_PRIVATE_PATHS_REQUIRED"),
    ("/mnt/durable/ledger.sqlite3", "/", "ABSOLUTE_UNAMBIGUOUS_PRIVATE_PATHS_REQUIRED"),
    ("/dev/shm/ledger.sqlite3", "/dev/shm", "EPHEMERAL_RUNTIME_PATH_REJECTED"),
    ("/var/tmp/ledger.sqlite3", "/var/tmp", "EPHEMERAL_RUNTIME_PATH_REJECTED"),
    ("/tmp/ledger.sqlite3", "/tmp", "EPHEMERAL_RUNTIME_PATH_REJECTED"),
    ("/mnt/durable/ledger.json", "/mnt/durable", "DEDICATED_SQLITE_LEDGER_FILE_REQUIRED"),
])
def test_configuration_shortcuts_are_rejected(path, mount, reason):
    result = audit.inspect_owner_ob_replay_storage(
        path, mount, mount_probe=lambda _: True,
    )
    assert reason in result["reason_codes"]
    assert result["may_issue_manual_live_grant"] is False


def test_unmounted_private_source_is_not_durable_claim(private_source_paths):
    mount, path = private_source_paths
    result = check(path, mount, mount_probe=lambda _: False)
    assert result["path_structure_valid"] is True
    assert result["mount_observed"] is False
    assert "REAL_MOUNT_NOT_OBSERVED" in result["reason_codes"]


def test_missing_and_world_readable_paths_denied(private_source_paths):
    mount, path = private_source_paths
    path.parent.chmod(0o755)
    result = check(path, mount, mount_probe=lambda _: True)
    assert "PRIVATE_DIRECTORY_PERMISSIONS_REQUIRED" in result["reason_codes"]
    path.parent.chmod(0o700)
    path.touch(mode=0o600)
    path.chmod(0o644)
    result = check(path, mount, mount_probe=lambda _: True)
    assert "EXISTING_LEDGER_NOT_PRIVATE" in result["reason_codes"]


def test_symlinked_ledger_parent_fails_closed(private_source_paths):
    mount, path = private_source_paths
    alt = mount / "alternate"
    alt.mkdir(mode=0o700)
    alias = mount / "alias"
    alias.symlink_to(alt, target_is_directory=True)
    report = check(alias / "ledger.sqlite3", mount, mount_probe=lambda _: True)
    assert "SYMLINKED_STORAGE_PATH_REJECTED" in report["reason_codes"]


def test_file_not_under_mount_rejected(private_source_paths):
    mount, path = private_source_paths
    elsewhere = mount.parent / "elsewhere"
    elsewhere.mkdir(mode=0o700)
    report = check(elsewhere / "ledger.sqlite3", mount, mount_probe=lambda _: True)
    assert "LEDGER_OUTSIDE_APPROVED_MOUNT" in report["reason_codes"]


def test_no_secrets_routes_or_runtime_mutation():
    source = Path(audit.__file__).read_text(encoding="utf-8")
    for forbidden in (
        "app.add_url_rule(", "@app.route(", "issue_owner_observatory_handoff(",
        "consume_owner_observatory_handoff(", "broker.place_order(",
        "os.environ.get(", "requests.post(",
    ):
        assert forbidden not in source
