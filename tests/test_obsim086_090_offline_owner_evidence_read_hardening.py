"""OBSIM086–090: owner-downloaded proof reader must not race into another file."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scripts import ob_verify_owner_evidence as verification


@pytest.fixture
def fake_integrity_verifier(monkeypatch):
    observed = []
    def accepted(value):
        observed.append(value)
        return {"state": "VALID_LOCAL_INTEGRITY_ONLY", "packet_hash": "local-only"}
    monkeypatch.setattr(verification, "verify_downloaded_owner_evidence_packet", accepted)
    return observed


def test_086_exact_regular_file_is_strictly_read_once(tmp_path, fake_integrity_verifier):
    file = tmp_path / "owner-proof.json"
    file.write_text('{"source_kind":"SYNTHETIC","labels":["PROOF-DEMO"]}')
    result = verification.read_and_verify(file)
    assert result["state"] == "VALID_LOCAL_INTEGRITY_ONLY"
    assert fake_integrity_verifier == [{"source_kind": "SYNTHETIC", "labels": ["PROOF-DEMO"]}]


def test_087_leaf_symlink_and_nonregular_file_denied_before_read(tmp_path, fake_integrity_verifier):
    file = tmp_path / "source.json"
    file.write_text('{"secret":"not-an-owner-proof"}')
    link = tmp_path / "link.json"
    link.symlink_to(file)
    with pytest.raises((ValueError, OSError)):
        verification.read_and_verify(link)
    with pytest.raises((ValueError, OSError)):
        verification.read_and_verify(tmp_path)
    with pytest.raises((ValueError, OSError)):
        verification.read_and_verify(tmp_path / "missing.json")
    if hasattr(os, "mkfifo"):
        fifo = tmp_path / "not-a-file.json"
        os.mkfifo(fifo)
        with pytest.raises((ValueError, OSError)):
            verification.read_and_verify(fifo)
    assert fake_integrity_verifier == []


def test_088_file_swapped_for_symlink_between_stat_and_open_is_denied(
    tmp_path, monkeypatch, fake_integrity_verifier,
):
    file = tmp_path / "downloaded.json"
    other = tmp_path / "other.json"
    file.write_text('{"source_kind":"SYNTHETIC"}')
    other.write_text('{"source_kind":"LIVE_OBSERVED","secret":"not-for-use"}')
    original_open = verification.os.open
    attempted = [False]

    def swapped_open(path, flags, *args, **kwargs):
        if Path(path) == file and not attempted[0]:
            attempted[0] = True
            file.unlink()
            file.symlink_to(other)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(verification.os, "open", swapped_open)
    with pytest.raises((ValueError, OSError)):
        verification.read_and_verify(file)
    assert attempted == [True]
    assert fake_integrity_verifier == []


def test_089_bound_read_rejects_oversize_empty_and_corrupt_json(
    tmp_path, fake_integrity_verifier,
):
    file = tmp_path / "downloaded.json"
    file.write_bytes(b"")
    with pytest.raises(ValueError):
        verification.read_and_verify(file)
    with file.open("wb") as output:
        output.truncate(verification.MAX_FILE_BYTES + 1)
    with pytest.raises(ValueError):
        verification.read_and_verify(file)
    for raw in (
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b'{"a":Infinity}',
        b'{"a":1',  # truncated JSON
        b'\xff\xfe',  # invalid UTF-8
    ):
        file.write_bytes(raw)
        with pytest.raises((ValueError, UnicodeError)):
            verification.read_and_verify(file)
    assert fake_integrity_verifier == []


def test_090_cli_does_not_reveal_rejected_payload_or_grant_approval(
    tmp_path, capsys,
):
    file = tmp_path / "owner-proof.json"
    file.write_text(json.dumps({
        "source_kind": "LIVE_OBSERVED",
        "secret": "HIGHLY_SENSITIVE_NOT_FOR_LOGS",
    }))
    assert verification.main(["--file", str(file)]) == 1
    output = capsys.readouterr().out
    assert "REJECTED" in output
    assert "HIGHLY_SENSITIVE_NOT_FOR_LOGS" not in output
    assert "Not broker/Tower proof" in output
    assert "AUTHORIZED" not in output
