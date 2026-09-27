"""OBSIM056–060: explicit opt-in hosted owner synthetic rehearsal, NOT local server.

A separate Tower-gated HTTPS route drives accepted OBSIM/OBTIME/CAPSIM. It
never imports or exposes the localhost Flask factory, handles no real account,
keeps all fictional reports in this single Python process, and is disabled
without exact deployment-specific origin + explicit source-reviewed opt-in.
Ephemeral reports and sessions are lost on worker restart/deploy.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import threading
from urllib.parse import urlsplit

from flask import abort, jsonify, render_template, request, session

from tower.tower_human_login_ob_launch import (
    SESSION_OWNER_ID, ensure_tower_session_id, operational_ob_access_active,
    owner_session_active, step_up_active,
)
from web.ob_explicit_owner_rehearsal_input import LocalOwnerRehearsalDesk
from web.ob_multi_simulation_harness import create_multi_simulation_harness, stable_hash
from web.ob_on_demand_simulation_session import (
    LocalSimulationReportStore, SourceKind, start_session,
)

SCHEMA = "OBSIM_HOSTED_OWNER_EPHEMERAL_REHEARSAL_V1"
ENTRY = "/ob/owner-rehearsal"
API = ENTRY + "/"
METHODS = ("status.json", "sample.json", "tick.json", "pause.json",
           "resume.json", "stop.json", "new.json")
EXACT_PATHS = frozenset((ENTRY, *(API + method for method in METHODS)))
MAX_BYTES = 65536
MAX_WORKSPACES = 8
IDLE_TTL = timedelta(hours=1)
SAMPLE = Path(__file__).resolve().parents[1] / "examples/obsim_owner_synthetic_hold_example.json"


class EphemeralOwnerReportStore(LocalSimulationReportStore):
    """In-memory no-clobber report sink; never claims durable local/hosted archive."""

    def __init__(self) -> None:
        super().__init__(Path("/not-a-persistent-hosted-report-path"))
        self.rows: list[dict[str, object]] = []
        self.final: dict[str, object] | None = None

    def save_tick(self, report: dict[str, object]) -> None:
        material = {key: value for key, value in report.items() if key != "report_hash"}
        if (self.final is not None or type(report.get("sequence")) is not int
                or report["sequence"] != len(self.rows) + 1
                or report.get("report_hash") != stable_hash(material)
                or report.get("simulation_only") is not True
                or report.get("broker_submission") is not False
                or report.get("capital_movement") is not False):
            raise ValueError("ephemeral report rejected")
        self.rows.append(json.loads(json.dumps(report, allow_nan=False)))

    def save_final(self, final: dict[str, object]) -> None:
        material = {key: value for key, value in final.items() if key != "report_hash"}
        if (self.final is not None or final.get("report_hash") != stable_hash(material)
                or final.get("total_ticks") != len(self.rows)
                or final.get("last_report_hash") != (
                    self.rows[-1]["report_hash"] if self.rows else None
                ) or final.get("simulation_only") is not True
                or final.get("broker_submission") is not False
                or final.get("capital_movement") is not False):
            raise ValueError("ephemeral final report rejected")
        self.final = json.loads(json.dumps(final, allow_nan=False))

    def inspect_archive(self, session_id: str) -> dict[str, object]:
        if (self.final is not None and self.final.get("session_id") != session_id
                or any(row.get("session_id") != session_id for row in self.rows)):
            raise ValueError("ephemeral report scope mismatch")
        return {
            "status": "EPHEMERAL_FINALIZED_REPORT_ONLY" if self.final
            else "EPHEMERAL_INCOMPLETE_REPORT_ONLY",
            "tick_count": len(self.rows), "durable_archive": False,
            "restart_recovery": False, "trading_session_restored": False,
            "simulation_only": True,
        }


class _Workspace:
    def __init__(self, now: datetime) -> None:
        self.csrf = secrets.token_urlsafe(32)
        self.last_seen = now
        self.store = EphemeralOwnerReportStore()
        self.desk = LocalOwnerRehearsalDesk(
            start_session(
                session_id="OB-WEB-" + secrets.token_hex(16),
                initial_harness=create_multi_simulation_harness(
                    harness_id="OB-WEB-EPHEMERAL-" + secrets.token_hex(8),
                    account_key="PROOF-DEMO", starting_capital=10000.0,
                    control_ref="CONTROL-FROZEN",
                    integrated_ref="INTEGRATED-ACCEPTED",
                    experimental_ref="EXPERIMENTAL-ISOLATED",
                ),
                source_kind=SourceKind.SYNTHETIC,
                now=now,
            ),
            self.store,
        )


def _origin(value: str) -> tuple[str, str]:
    parsed = urlsplit(value)
    if (not value or parsed.scheme != "https" or not parsed.netloc
            or parsed.username or parsed.password or parsed.path not in ("", "/")
            or parsed.query or parsed.fragment or parsed.hostname is None
            or parsed.netloc != parsed.netloc.lower()):
        raise ValueError("explicit exact HTTPS rehearsal origin required")
    return "https://" + parsed.netloc, parsed.netloc


def _strict_object(body: bytes) -> dict[str, object]:
    def unique(pairs):
        found = {}
        for key, value in pairs:
            if key in found:
                raise ValueError("duplicate owner JSON key")
            found[key] = value
        return found

    def invalid(_):
        raise ValueError("nonfinite JSON number")

    parsed = json.loads(
        body.decode("utf-8"), object_pairs_hook=unique,
        parse_constant=invalid,
    )
    if type(parsed) is not dict:
        raise ValueError("JSON object required")
    return parsed


def register_ob_hosted_owner_rehearsal(
    app, *, enabled: bool = False, canonical_origin: str | None = None,
    clock=lambda: datetime.now(timezone.utc),
):
    """Register exact protected routes, default disabled; NO self-grant/remote local adapter."""
    if app.extensions.get("ob_hosted_owner_rehearsal_registered"):
        return app
    if not callable(clock):
        raise ValueError("clock required")
    configured_origin, configured_host = (
        _origin(canonical_origin or "") if enabled else ("", "")
    )
    boot_salt = secrets.token_bytes(32)
    lock = threading.RLock()
    workspaces: dict[str, _Workspace] = {}

    def scope() -> str:
        owner = session.get(SESSION_OWNER_ID)
        sid = ensure_tower_session_id()
        if (not owner_session_active() or not step_up_active()
                or not operational_ob_access_active()
                or not isinstance(owner, str) or not owner or not sid):
            abort(403)
        # Both owner and Tower session identity are server-validated by Tower.
        return hmac.new(boot_salt, (owner + "\x00" + sid).encode(), hashlib.sha256).hexdigest()

    def get_workspace(*, create=False):
        key = scope()
        now = clock()
        if not isinstance(now, datetime) or now.tzinfo is None:
            abort(503)
        with lock:
            for existing, item in list(workspaces.items()):
                if now - item.last_seen > IDLE_TTL:
                    del workspaces[existing]
            item = workspaces.get(key)
            if item is None and create:
                if len(workspaces) >= MAX_WORKSPACES:
                    abort(503)
                item = _Workspace(now)
                workspaces[key] = item
            if item is None:
                abort(409)
            item.last_seen = now
            return item

    @app.before_request
    def _hosted_owner_rehearsal_gate():
        if request.path not in EXACT_PATHS:
            return None
        if not enabled:
            abort(503)
        if request.host != configured_host:
            abort(403)
        scope()
        if request.path != ENTRY:
            key = scope()
            with lock:
                item = workspaces.get(key)
                if item is None:
                    abort(409)
                received = request.headers.get("X-OB-Rehearsal-Token", "")
                if not secrets.compare_digest(item.csrf, received):
                    abort(403)
        if request.method == "POST":
            if request.headers.get("Origin") != configured_origin:
                abort(403)
            if request.mimetype != "application/json":
                abort(415)
            size = request.content_length
            if type(size) is not int or not 0 < size <= MAX_BYTES:
                abort(413)
        return None

    @app.after_request
    def _hosted_owner_rehearsal_headers(response):
        if request.path in EXACT_PATHS:
            response.headers["Cache-Control"] = "no-store, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = "no-referrer"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Content-Security-Policy"] = (
                "default-src 'none'; script-src 'self'; style-src 'self'; "
                "connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; "
                "form-action 'none'"
            )
        return response

    def view(item: _Workspace, now: datetime) -> dict[str, object]:
        state = item.desk.view(now=now)
        last = item.desk.session.reports[-1] if item.desk.session.reports else None
        return {
            **state, "schema_version": SCHEMA,
            "last_lanes": last["lanes"] if last else None,
            "last_source_freshness": last["source_freshness"] if last else None,
            "storage_state": "VOLATILE_PROCESS_MEMORY_ONLY",
            "durable_archive": False, "restart_recovery": False,
            "proof_demo_only": True, "actual_capital_known": False,
            "tower_owner_session_checked_each_request": True,
            "tower_ob_operational_access_checked_each_request": True,
            "hosted_rehearsal_is_manual_live_clearance": False,
            "manual_live_unlock": False, "hybrid_unlock": False,
            "automated_unlock": False, "broker_submission": False,
            "capital_movement": False,
        }

    def mutation(action):
        item = get_workspace()
        instant = clock()
        with lock:
            try:
                result = action(item, instant)
                payload = view(item, instant)
                if isinstance(result, dict):
                    payload.update({
                        "archive_state": result.get("status"),
                        "archive_tick_count": result.get("tick_count"),
                        "in_memory_session_restored": False,
                    })
                return jsonify(payload)
            except (ValueError, FileExistsError, OSError):
                return jsonify({
                    "status": "REJECTED_NO_ADDITIONAL_REPORT",
                    "simulation_only": True, "manual_live_unlock": False,
                }), 409

    def page():
        item = get_workspace(create=True)
        return render_template(
            "hosted_owner_rehearsal.html",
            csrf=item.csrf, source_kind="SYNTHETIC",
        )

    def status():
        item = get_workspace()
        with lock:
            return jsonify(view(item, clock()))

    def sample():
        return jsonify(_strict_object(SAMPLE.read_bytes()))

    def tick():
        try:
            payload = _strict_object(request.get_data())
        except (ValueError, UnicodeDecodeError):
            return jsonify({"status": "EXPLICIT_STRICT_JSON_REQUIRED"}), 400
        return mutation(lambda item, instant: item.desk.submit_explicit_input(payload, now=instant))

    def empty_command_valid():
        try:
            return _strict_object(request.get_data()) == {}
        except (ValueError, UnicodeDecodeError):
            return False

    def pause():
        if not empty_command_valid():
            return jsonify({"status": "EXACT_EMPTY_JSON_COMMAND_REQUIRED"}), 400
        return mutation(lambda item, instant: item.desk.pause())

    def resume():
        if not empty_command_valid():
            return jsonify({"status": "EXACT_EMPTY_JSON_COMMAND_REQUIRED"}), 400
        return mutation(lambda item, instant: item.desk.resume(now=instant))

    def stop():
        if not empty_command_valid():
            return jsonify({"status": "EXACT_EMPTY_JSON_COMMAND_REQUIRED"}), 400
        return mutation(lambda item, instant: item.desk.stop(now=instant))

    def fresh():
        if not empty_command_valid():
            return jsonify({"status": "EXACT_EMPTY_JSON_COMMAND_REQUIRED"}), 400
        item = get_workspace()
        with lock:
            if item.desk.session.status.value != "STOPPED":
                return jsonify({"status": "STOP_EXISTING_SESSION_FIRST"}), 409
            key = scope()
            new_item = _Workspace(clock())
            # Same currently checked Tower session keeps its unguessable local
            # CSRF token; do not strand the already-open browser after reset.
            new_item.csrf = item.csrf
            workspaces[key] = new_item
            return jsonify(view(new_item, clock()))

    app.add_url_rule(ENTRY, endpoint="ob_owner_rehearsal_hosted_page", view_func=page, methods=["GET"])
    for name, fn, method in (
        ("status", status, "GET"), ("sample", sample, "GET"),
        ("tick", tick, "POST"), ("pause", pause, "POST"),
        ("resume", resume, "POST"), ("stop", stop, "POST"),
        ("new", fresh, "POST"),
    ):
        app.add_url_rule(
            API + name + ".json", endpoint="ob_owner_rehearsal_hosted_" + name,
            view_func=fn, methods=[method],
        )
    app.extensions["ob_hosted_owner_rehearsal_registered"] = {
        "enabled": enabled, "canonical_origin_configured": bool(configured_origin),
        "durable_archive": False, "manual_live_grant": False,
        "source_only_until_explicit_reviewed_activation": True,
    }
    return app


def register_configured_ob_hosted_owner_rehearsal(app):
    """Default OFF; no secret, origin, hosted report store or permission invented."""
    enabled = os.environ.get("OB_OWNER_REHEARSAL_HOSTED_ENABLED") == "1"
    return register_ob_hosted_owner_rehearsal(
        app, enabled=enabled,
        canonical_origin=os.environ.get("OB_OWNER_REHEARSAL_ORIGIN", ""),
    )
