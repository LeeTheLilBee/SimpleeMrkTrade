"""OBSIM046–050: loopback owner UI is separate from hosted Tower and no trade grant."""
from copy import deepcopy
from datetime import timedelta
import json
from pathlib import Path
import re

import pytest

from test_obsim016_020_on_demand_session import BASE
from web.ob_local_owner_rehearsal_ui import create_local_owner_rehearsal_app
from web.ob_on_demand_simulation_session import LocalSimulationReportStore, SourceKind

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8765"
SAMPLE = json.loads((ROOT / "examples/obsim_owner_synthetic_hold_example.json").read_text())


def setup(tmp_path, *, kind=SourceKind.SYNTHETIC):
    current = [BASE]
    archive = tmp_path / "owner-private"
    app = create_local_owner_rehearsal_app(
        archive=archive, port=8765, session_id="LOCAL-WEB-TEST",
        source_kind=kind, clock=lambda: current[0],
    )
    app.testing = True
    client = app.test_client()
    html = client.get("/", base_url=BASE_URL)
    assert html.status_code == 200
    found = re.search(r'data-ob-csrf="([^"]+)"', html.get_data(as_text=True))
    assert found
    token = found.group(1)
    assert len(token) >= 32
    headers = {"Origin": BASE_URL, "X-OB-Rehearsal-Token": token}
    return app, client, archive, current, token, headers


def get(client, path, token):
    return client.get(
        path, base_url=BASE_URL, headers={"X-OB-Rehearsal-Token": token},
    )


def post(client, path, headers, obj=None):
    return client.post(
        path, base_url=BASE_URL, headers=headers, json={} if obj is None else obj,
    )


def test_obsim046_local_surface_is_actual_dark_glass_and_not_hosted_entrypoint(tmp_path):
    app, client, archive, _, token, _ = setup(tmp_path)
    html = client.get("/", base_url=BASE_URL)
    content = html.get_data(as_text=True)
    assert "LOCAL 127.0.0.1 ONLY" in content
    assert "REAL MANUAL LIVE" in content and "HOLD" in content
    assert "does not authenticate your Tower owner session" in content
    assert "data-ob-room=\"local-owner-rehearsal\"" in content
    assert "/assets/ob/ob_local_owner_rehearsal.js" in content
    assert html.headers["Cache-Control"] == "no-store, private"
    assert "frame-ancestors 'none'" in html.headers["Content-Security-Policy"]
    assert html.headers["Referrer-Policy"] == "no-referrer"
    assert get(client, "/api/status", token).status_code == 200
    assert not archive.exists()
    # Main and Tower expose different dormant WSGI entrypoint filenames.
    for entrypoint in ("web/managed_staging.py", "web/hosted_tower.py"):
        target = ROOT / entrypoint
        if target.exists():
            assert "create_local_owner_rehearsal_app" not in target.read_text()
    assert "ob_local_owner_rehearsal" not in (
        ROOT / "web/templates/owner_dashboard.html"
    ).read_text()


def test_obsim047_no_wrong_host_remote_origin_or_missing_token_can_mutate(tmp_path):
    _, client, archive, now, token, headers = setup(tmp_path)
    now[0] = BASE + timedelta(seconds=30)
    assert client.get("/", base_url="http://localhost:8765").status_code == 403
    assert client.get(
        "/", base_url=BASE_URL,
        environ_overrides={"REMOTE_ADDR": "203.0.113.7"},
    ).status_code == 403
    assert client.get("/api/status", base_url=BASE_URL).status_code == 403
    assert client.get("/api/example", base_url=BASE_URL).status_code == 403
    assert post(client, "/api/tick", {"Origin": BASE_URL}, SAMPLE).status_code == 403
    assert post(client, "/api/tick", {"X-OB-Rehearsal-Token": token}, SAMPLE).status_code == 403
    assert post(client, "/api/tick", {
        **headers, "Origin": "https://attacker.example",
    }, SAMPLE).status_code == 403
    assert client.post(
        "/api/tick", base_url=BASE_URL, headers=headers,
        data=json.dumps(SAMPLE), content_type="text/plain",
    ).status_code == 403
    assert post(client, "/api/tick", headers, []).status_code == 400
    assert not archive.exists()


def test_obsim048_one_explicit_due_tick_pause_resume_and_final_archive(tmp_path):
    _, client, archive, now, token, headers = setup(tmp_path)
    example = get(client, "/api/example", token)
    assert example.status_code == 200
    assert example.json["source_kind"] == "SYNTHETIC"
    assert "NOT-A-MARKET-FEED" in example.json["frame"]["source_reference"]
    now[0] = BASE + timedelta(seconds=29)
    early = post(client, "/api/tick", headers, SAMPLE)
    assert early.status_code == 409 and early.json["manual_live_unlock"] is False
    assert not archive.exists()
    now[0] = BASE + timedelta(seconds=30)
    accepted = post(client, "/api/tick", headers, SAMPLE)
    assert accepted.status_code == 200
    body = accepted.json
    assert body["accepted_ticks"] == 1
    assert body["proof_demo_only"] and body["simulation_only"]
    assert body["last_lanes"] and len(body["last_lanes"]) == 3
    for flag in ("source_provider_authenticated", "tower_owner_authenticated_here",
                 "real_manual_live_ready", "broker_submission",
                 "capital_movement", "unattended_tick_scheduled"):
        assert body[flag] is False
    now[0] = BASE + timedelta(seconds=31)
    assert post(client, "/api/pause", headers).json["state"] == "PAUSED"
    now[0] = BASE + timedelta(seconds=60)
    assert post(client, "/api/tick", headers, SAMPLE).status_code == 409
    now[0] = BASE + timedelta(seconds=100)
    assert post(client, "/api/resume", headers).json["state"] == "RUNNING"
    now[0] = BASE + timedelta(seconds=129)
    assert post(client, "/api/tick", headers, SAMPLE).status_code == 409
    new_input = deepcopy(SAMPLE)
    new_input["frame"].update(
        frame_id="OWNER-SAMPLE-F002",
        observed_at="2026-09-24T10:01:00-04:00",
        source_reference="SYNTHETIC-OWNER-SAMPLE-F002-NOT-A-MARKET-FEED",
    )
    for lane in new_input["decisions"]:
        new_input["decisions"][lane]["decision_id"] = "OWNER-SAMPLE-F002-" + lane
    now[0] = BASE + timedelta(seconds=130)
    assert post(client, "/api/tick", headers, new_input).json["accepted_ticks"] == 2
    now[0] = BASE + timedelta(seconds=131)
    stopped = post(client, "/api/stop", headers)
    assert stopped.status_code == 200
    assert stopped.json["state"] == "STOPPED"
    assert stopped.json["archive_state"] == "FINALIZED_REPORT_ONLY"
    assert stopped.json["archive_tick_count"] == 2
    assert stopped.json["in_memory_session_restored"] is False
    assert post(client, "/api/tick", headers, new_input).status_code == 409
    saved = LocalSimulationReportStore(archive).inspect_archive("LOCAL-WEB-TEST")
    assert saved["status"] == "FINALIZED_REPORT_ONLY" and saved["tick_count"] == 2


def test_obsim049_reject_spoofed_provider_owner_account_and_empty_source(tmp_path):
    _, client, archive, now, token, headers = setup(tmp_path)
    now[0] = BASE + timedelta(seconds=30)
    for patch in (
        {"verified_tower_owner": True},
        {"account_key": "ob_acct_trust"},
        {"source_kind": "LIVE_OBSERVED"},
        {"broker_submission": True},
    ):
        wrong = {**SAMPLE, **patch}
        response = post(client, "/api/tick", headers, wrong)
        assert response.status_code == 409
        assert response.json["status"] == "REJECTED_NO_ADDITIONAL_REPORT"
        assert "ob_acct_trust" not in response.get_data(as_text=True)
    assert not archive.exists()
    assert get(client, "/api/status", token).json["accepted_ticks"] == 0


def test_obsim050_no_public_listener_no_automatic_tick_or_external_api(tmp_path):
    runner = (ROOT / "scripts/ob_local_owner_rehearsal_web.py").read_text()
    browser = (ROOT / "web/static/ob/ob_local_owner_rehearsal.js").read_text()
    module = (ROOT / "web/ob_local_owner_rehearsal_ui.py").read_text()
    assert 'app.run(host="127.0.0.1", port=args.port, threaded=False, debug=False, use_reloader=False)' in runner
    assert "create_local_owner_rehearsal_app" in runner
    assert "X-OB-Rehearsal-Token" in module
    assert 'request.headers.get("Origin") != expected_origin' in module
    assert "MAX_CONTENT_LENGTH=MAX_REQUEST_SIZE" in module
    assert "setInterval" in browser
    assert "Submit one simulated tick" in (
        ROOT / "web/templates/local_owner_rehearsal.html"
    ).read_text()
    assert "setInterval(() => {" in browser
    assert "/api/tick" in browser and 'mutate("/api/tick"' in browser
    assert "innerHTML" not in browser
    assert "localStorage" not in browser
    assert "place_order(" not in module
    assert "@app.route('/ob/" not in module
    with pytest.raises(ValueError, match="nonprivileged fixed port"):
        create_local_owner_rehearsal_app(archive=tmp_path, port=0)
    with pytest.raises(ValueError, match="historical/synthetic"):
        create_local_owner_rehearsal_app(
            archive=tmp_path, source_kind=SourceKind.LIVE_OBSERVED,
        )
