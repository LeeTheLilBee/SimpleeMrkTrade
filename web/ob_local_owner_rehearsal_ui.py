"""OBSIM046–050: independently launched loopback-only owner rehearsal web desk.

This is NOT a hosted Observatory route or Tower identity adapter. No global app
object is exported: the local owner explicitly starts a separate 127.0.0.1
process and manually submits source-declared SYNTHETIC/HISTORICAL JSON. All
simulation, OBTIME and archive authority delegates to the accepted OBSIM desk.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import secrets
import threading
from typing import Callable

from flask import Flask, abort, jsonify, render_template, request

from scripts.ob_local_owner_rehearsal import REHEARSAL_ACCOUNT, SIMULATED_UNITS
from web.ob_explicit_owner_rehearsal_input import LocalOwnerRehearsalDesk
from web.ob_multi_simulation_harness import create_multi_simulation_harness
from web.ob_on_demand_simulation_session import (
    LocalSimulationReportStore, SourceKind, start_session,
)

LOCAL_SCHEMA = "OBSIM_LOOPBACK_OWNER_REHEARSAL_UI_V1"
MAX_REQUEST_SIZE = 65536
SAMPLE = Path(__file__).resolve().parents[1] / "examples/obsim_owner_synthetic_hold_example.json"


def create_local_owner_rehearsal_app(
    *, archive: Path, port: int = 8765,
    session_id: str = "LOCAL-OWNER-WEB-REHEARSAL",
    source_kind: SourceKind = SourceKind.SYNTHETIC,
    clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
) -> Flask:
    """Build only a standalone, single-process, loopback-bound local rehearsal.

    The process itself must use app.run(host="127.0.0.1", threaded=False,
    debug=False, use_reloader=False). This function does not register with
    web.app, hosted Tower, managed staging, or an externally bound application.
    """
    if type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("local rehearsal requires an explicit nonprivileged fixed port")
    if source_kind not in (SourceKind.SYNTHETIC, SourceKind.HISTORICAL):
        raise ValueError("local owner web accepts historical/synthetic only")
    if not callable(clock):
        raise ValueError("local rehearsal requires a clock")

    harness = create_multi_simulation_harness(
        harness_id="OBSIM_LOOPBACK_REHEARSAL", account_key=REHEARSAL_ACCOUNT,
        starting_capital=SIMULATED_UNITS,
        control_ref="CONTROL-FROZEN",
        integrated_ref="INTEGRATED-ACCEPTED",
        experimental_ref="EXPERIMENTAL-ISOLATED",
    )
    desk = LocalOwnerRehearsalDesk(
        start_session(
            session_id=session_id, initial_harness=harness,
            source_kind=source_kind, now=clock(),
        ),
        LocalSimulationReportStore(Path(archive)),
    )
    csrf = secrets.token_urlsafe(32)
    expected_host = f"127.0.0.1:{port}"
    expected_origin = f"http://{expected_host}"
    lock = threading.RLock()

    app = Flask(
        __name__, template_folder="templates", static_folder="static",
        static_url_path="/assets",
    )
    app.config.update(
        MAX_CONTENT_LENGTH=MAX_REQUEST_SIZE,
        JSON_SORT_KEYS=True,
    )

    @app.before_request
    def _standalone_loopback_gate():
        # Explicitly refuse Host rewriting, remote traffic and proxy exposure.
        if request.host != expected_host or request.remote_addr not in ("127.0.0.1", "::1"):
            abort(403)
        if request.path.startswith("/api/"):
            supplied = request.headers.get("X-OB-Rehearsal-Token", "")
            if not secrets.compare_digest(csrf, supplied):
                abort(403)
        if request.method not in ("GET", "HEAD"):
            if request.path.startswith("/assets/"):
                abort(405)
            if (
                request.headers.get("Origin") != expected_origin
                or request.mimetype != "application/json"
                or not secrets.compare_digest(
                    csrf, request.headers.get("X-OB-Rehearsal-Token", "")
                )
            ):
                abort(403)

    @app.after_request
    def _private_headers(response):
        response.headers["Cache-Control"] = "no-store, private"
        response.headers["Pragma"] = "no-cache"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; script-src 'self'; style-src 'self'; "
            "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
            "form-action 'none'"
        )
        return response

    def _snapshot(now: datetime) -> dict[str, object]:
        state = desk.view(now=now)
        last = desk.session.reports[-1] if desk.session.reports else None
        return {
            "schema_version": LOCAL_SCHEMA, "state": state["state"],
            "session_id": state["session_id"],
            "declared_source_kind": state["declared_source_kind"],
            "due": state["due"],
            "accepted_ticks": state["accepted_ticks"],
            "last_report_hash": state["last_report_hash"],
            "last_lanes": last["lanes"] if last else None,
            "last_source_freshness": last["source_freshness"] if last else None,
            "sample_is_synthetic_not_live": True,
            "proof_demo_only": True,
            "source_provider_authenticated": False,
            "tower_owner_authenticated_here": False,
            "real_manual_live_ready": False,
            "broker_submission": False,
            "capital_movement": False,
            "unattended_tick_scheduled": False,
            "simulation_only": True,
        }

    def _mutation_response(operation: Callable[[], object], now: datetime):
        with lock:
            try:
                operation()
                return jsonify(_snapshot(now))
            except (ValueError, FileExistsError, OSError):
                # Never echo a submitted source/account payload or filesystem path.
                return jsonify({
                    "status": "REJECTED_NO_ADDITIONAL_REPORT",
                    "simulation_only": True, "manual_live_unlock": False,
                }), 409

    @app.get("/")
    def local_owner_rehearsal():
        return render_template(
            "local_owner_rehearsal.html", csrf=csrf, source_kind=source_kind.value,
        )

    @app.get("/api/status")
    def local_status():
        with lock:
            try:
                return jsonify(_snapshot(clock()))
            except ValueError:
                return jsonify({"status": "CLOCK_OR_SESSION_INVALID"}), 409

    @app.get("/api/example")
    def local_example():
        # Fixed, checked-in, clearly SYNTHETIC example; never a downloaded feed.
        payload = json.loads(SAMPLE.read_text(encoding="utf-8"))
        return jsonify(payload)

    @app.post("/api/tick")
    def local_tick():
        supplied = request.get_json(silent=True)
        if type(supplied) is not dict:
            return jsonify({"status": "EXPLICIT_JSON_OBJECT_REQUIRED"}), 400
        instant = clock()
        return _mutation_response(
            lambda: desk.submit_explicit_input(supplied, now=instant), instant,
        )

    @app.post("/api/pause")
    def local_pause():
        instant = clock()
        return _mutation_response(lambda: desk.pause(), instant)

    @app.post("/api/resume")
    def local_resume():
        instant = clock()
        return _mutation_response(lambda: desk.resume(now=instant), instant)

    @app.post("/api/stop")
    def local_stop():
        instant = clock()
        with lock:
            try:
                final = desk.stop(now=instant)
                return jsonify({
                    **_snapshot(instant),
                    "archive_state": final["status"],
                    "archive_tick_count": final["tick_count"],
                    "in_memory_session_restored": False,
                })
            except (ValueError, FileExistsError, OSError):
                return jsonify({"status": "STOP_REPORT_NOT_ACCEPTED"}), 409

    return app
