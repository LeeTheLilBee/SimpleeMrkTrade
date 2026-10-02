"""OBSIM076–080: explicit owner export is guarded, final-only, and offline verifiable."""
from __future__ import annotations

from copy import deepcopy
from datetime import timedelta
import json

import pytest

import test_obsim056_060_hosted_owner_rehearsal as prior
from tower.ob_hosted_owner_evidence import (
    build_finalized_owner_evidence_packet, verify_downloaded_owner_evidence_packet,
)
from tower.ob_hosted_owner_rehearsal import ENTRY, API, _Workspace
from tower.ob_web_route_enforcement import is_approved_ob_web_room
from scripts.ob_verify_owner_evidence import main, read_and_verify
from web.ob_multi_simulation_harness import stable_hash


def ready_finalized(monkeypatch):
    app, client, state = prior.build_app(monkeypatch)
    token = prior.setup_page(client)
    state["now"] += timedelta(seconds=30)
    first = prior.post(client, "tick", token, prior.SAMPLE)
    assert first.status_code == 200, first.get_data(as_text=True)
    result = prior.post(client, "stop", token)
    assert result.status_code == 200, result.get_data(as_text=True)
    return app, client, state, token


def test_076_final_export_is_not_public_and_cannot_export_active_session(monkeypatch):
    _, client, state = prior.build_app(monkeypatch)
    token = prior.setup_page(client)
    path = API + "evidence.json"
    assert is_approved_ob_web_room(path)
    assert not is_approved_ob_web_room(API + "evidence.json/raw")
    assert prior.get(client, path).status_code == 403
    assert prior.get(client, path, "guess").status_code == 403
    assert prior.get(client, path, token, origin="https://wrong-host.example").status_code == 403
    before = prior.get(client, path, token)
    assert before.status_code == 409 and before.json["manual_live_unlock"] is False
    state["now"] += timedelta(seconds=30)
    assert prior.post(client, "tick", token, prior.SAMPLE).status_code == 200
    assert prior.get(client, path, token).status_code == 409


def test_077_finalized_export_round_trip_and_no_private_tower_capability(monkeypatch, tmp_path):
    _, client, state, token = ready_finalized(monkeypatch)
    response = prior.get(client, API + "evidence.json", token)
    assert response.status_code == 200
    assert response.headers["Cache-Control"] == "no-store, private"
    packet = response.json
    assert packet["schema_version"] == "OBSIM_OWNER_EPHEMERAL_FINAL_EVIDENCE_V1"
    assert packet["tick_count"] == 1
    assert packet["reports"][0]["sequence"] == 1
    assert packet["final"]["last_report_hash"] == packet["reports"][0]["report_hash"]
    assert packet["source_kind"] == "SYNTHETIC"
    assert packet["account_key"] == "PROOF-DEMO"
    for field in (
        "source_provider_authenticated", "tower_issuer_receipt_exported",
        "broker_or_capital_authenticated", "manual_live_authorized",
        "broker_submission", "capital_movement", "durable_server_archive",
        "server_restart_recovery", "this_is_a_third_party_attestation",
    ):
        assert packet[field] is False
    for secret in ("csrf", "tower_session", "new_rehearsal_token", "password", "authorization"):
        assert secret not in json.dumps(packet).lower()
    assert packet["packet_hash"] == stable_hash(
        {key: value for key, value in packet.items() if key != "packet_hash"}
    )
    verification = verify_downloaded_owner_evidence_packet(packet)
    assert verification["state"] == "VALID_LOCAL_INTEGRITY_ONLY"
    assert verification["tick_count"] == 1 and verification["manual_live_authorized"] is False

    path = tmp_path / "owner-proof-demo.json"
    path.write_text(json.dumps(packet))
    assert read_and_verify(path)["packet_hash"] == packet["packet_hash"]
    assert main(["--file", str(path)]) == 0


def test_078_tampered_report_terminal_and_downloaded_envelope_denied(monkeypatch, tmp_path):
    _, client, _, token = ready_finalized(monkeypatch)
    packet = prior.get(client, API + "evidence.json", token).json
    for modifier in (
        lambda p: p["reports"][0]["lanes"]["CONTROL"].update(equity=123456),
        lambda p: p["reports"][0].update(sequence=2),
        lambda p: p["reports"][0].update(source_kind="LIVE_OBSERVED"),
        lambda p: p["reports"][0].update(broker_submission=True),
        lambda p: p["final"].update(last_report_hash="0" * 64),
        lambda p: p.update(tick_count=999),
        lambda p: p.update(tower_issuer_receipt_exported=True),
        lambda p: p.update(packet_hash="f" * 64),
        lambda p: p.update(extra_secret="unaccepted"),
    ):
        modified = deepcopy(packet)
        modifier(modified)
        with pytest.raises((ValueError, TypeError, KeyError)):
            verify_downloaded_owner_evidence_packet(modified)

    file = tmp_path / "owner.json"
    file.write_text('{"x":1,"x":2}')
    assert main(["--file", str(file)]) == 1
    file.write_text('{"x":NaN}')
    assert main(["--file", str(file)]) == 1


def test_079_source_tamper_can_never_bypass_chain_verifier(monkeypatch):
    _, client, _, token = ready_finalized(monkeypatch)
    packet = prior.get(client, API + "evidence.json", token).json
    reports = deepcopy(packet["reports"])
    final = deepcopy(packet["final"])
    assert build_finalized_owner_evidence_packet(packet["session_id"], reports, final)["packet_hash"] == packet["packet_hash"]
    reports[0]["source_claim_verified"] = True
    with pytest.raises(ValueError):
        build_finalized_owner_evidence_packet(packet["session_id"], reports, final)
    reports = deepcopy(packet["reports"])
    final["last_report_hash"] = "fake"
    with pytest.raises(ValueError):
        build_finalized_owner_evidence_packet(packet["session_id"], reports, final)
    with pytest.raises(ValueError):
        build_finalized_owner_evidence_packet("OB-WEB-not-this-session", packet["reports"], packet["final"])
    with pytest.raises(ValueError):
        build_finalized_owner_evidence_packet(packet["session_id"], packet["reports"], None)


def test_080_owner_logout_and_reset_revokes_previous_download_token(monkeypatch):
    _, client, state, token = ready_finalized(monkeypatch)
    path = API + "evidence.json"
    assert prior.get(client, path, token).status_code == 200
    state["owner"] = False
    assert prior.get(client, path, token).status_code != 200
    state["owner"] = True
    next_session = prior.post(client, "new", token)
    assert next_session.status_code == 200
    new_token = next_session.json["new_rehearsal_token"]
    assert prior.get(client, path, token).status_code == 403
    assert prior.get(client, path, new_token).status_code == 409
    state["now"] += timedelta(seconds=31)
    assert prior.post(client, "tick", new_token, prior.SAMPLE).status_code == 200
    assert prior.post(client, "stop", new_token).status_code == 200
    assert prior.get(client, path, new_token).status_code == 200

    # Independent new Python worker has no session/report archive to offer.
    app2, client2, _ = prior.build_app(monkeypatch)
    assert client2.get(path, base_url=prior.ORIGIN, headers={
        "X-OB-Rehearsal-Token": new_token,
    }).status_code != 200


def test_080_browser_and_route_retain_false_authentication_guards():
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    page = (root / "web/templates/hosted_owner_rehearsal.html").read_text()
    js = (root / "web/static/ob/ob_hosted_owner_rehearsal.js").read_text()
    assert "Save finalized Proof/Demo evidence" in page
    assert "not authenticated broker/market proof" in page
    assert '"/ob/owner-rehearsal/evidence.json"' in js
    assert 'last.state !== "STOPPED"' in js
    assert 'credentials: "same-origin"' in js
    assert "URL.createObjectURL" in js and "URL.revokeObjectURL" in js
    assert "localStorage" not in js and "innerHTML" not in js
