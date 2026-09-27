"""Owner-driven, zero-hosting-cost OBSIM report session (OBSIM016–020).

A caller supplies one already-authored ReplayStep on each due poll. This module
does not start a timer, obtain prices, generate decisions, trade, or create a
background job. It reuses the accepted fresh-harness replay, including OBTIME
and CAPSIM safeguards. A UI/local process may call tick_session every 30 seconds.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from enum import Enum
import json
import os
from pathlib import Path
import re
import stat
import tempfile

from web.ob_multi_simulation_harness import (
    MultiSimulationHarness, SimulationLane, compare_simulation_lanes, stable_hash,
)
from web.ob_multi_simulation_replay import ReplayStep, replay_three_lanes


SCHEMA_VERSION = "OB_ON_DEMAND_SIMULATION_SESSION_V1"
SERVICE_VERSION = "OBSIM016_020_FREE_OWNER_SESSION"
INTERVAL_SECONDS = 30
# Replaying the entire accepted history from a fresh harness is bounded until
# a separately reviewed incremental/checkpoint replay contract exists.
MAX_TICKS = 120
LANES = tuple(SimulationLane)
SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


class SourceKind(str, Enum):
    HISTORICAL = "HISTORICAL"
    SYNTHETIC = "SYNTHETIC"
    LIVE_OBSERVED = "LIVE_OBSERVED"


class SessionStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"


def _utc(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("session clock must be timezone-aware")
    return value.astimezone(timezone.utc)


def _observed(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("source observation must be ISO-8601")
    try:
        return _utc(datetime.fromisoformat(value.replace("Z", "+00:00")))
    except (TypeError, ValueError) as exc:
        raise ValueError("source observation must be timezone-aware ISO-8601") from exc


def _hash_report(material: dict[str, object]) -> dict[str, object]:
    return {**material, "report_hash": stable_hash(material)}


@dataclass(frozen=True)
class OwnerSimulationSession:
    session_id: str
    initial_harness: MultiSimulationHarness
    source_kind: SourceKind
    started_at: datetime
    last_tick_at: datetime
    status: SessionStatus = SessionStatus.RUNNING
    steps: tuple[ReplayStep, ...] = ()
    reports: tuple[dict[str, object], ...] = ()


class LocalSimulationReportStore:
    """Owner-chosen local directory, one immutable JSON file per tick.

    This is a single-writer beta archive, not a multiuser database or hosting
    service. Persisted reports can be reviewed after restart. Restoring live
    harness positions requires separately verified ReplayStep inputs, not a
    report-only reconstruction.
    """

    def __init__(self, root: Path):
        self.root = Path(root)

    def _folder(self, session_id: str) -> Path:
        if not SESSION_ID.fullmatch(session_id):
            raise ValueError("invalid session id")
        return self.root / session_id

    def _write(self, path: Path, payload: dict[str, object]) -> None:
        # Never write through a symlinked owner archive or an accessible directory.
        # Do not silently chmod an owner-chosen path whose permissions are unsafe.
        if self.root.is_symlink() or path.parent.is_symlink():
            raise ValueError("symlinked simulation archive forbidden")
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if (self.root.is_symlink() or path.parent.is_symlink() or
                any(stat.S_IMODE(folder.stat().st_mode) & 0o077
                    for folder in (self.root, path.parent))):
            raise ValueError("simulation archive must be private")
        if path.exists() or path.is_symlink():
            raise FileExistsError("simulation report already exists")
        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=path.parent,
                prefix=".pending-", suffix=".json", delete=False,
            ) as file:
                temporary = file.name
                json.dump(payload, file, sort_keys=True, separators=(",", ":"), allow_nan=False)
                file.flush()
                os.fsync(file.fileno())
            # Atomic no-clobber publication: os.replace can overwrite a report
            # created by a second writer between existence check and publication.
            # A same-directory hard link fails atomically if the final path exists.
            os.link(temporary, path, follow_symlinks=False)
            Path(temporary).unlink()
            temporary = None
            # Persist the directory entry on POSIX where supported.
            if hasattr(os, "O_DIRECTORY"):
                directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)

    def save_tick(self, report: dict[str, object]) -> None:
        self._write(
            self._folder(str(report["session_id"])) / f'{int(report["sequence"]):04d}.json',
            report,
        )

    def save_final(self, final: dict[str, object]) -> None:
        self._write(self._folder(str(final["session_id"])) / "_final.json", final)

    def load_ticks(self, session_id: str) -> tuple[dict[str, object], ...]:
        folder = self._folder(session_id)
        reports = []
        for expected, path in enumerate(sorted(folder.glob("[0-9][0-9][0-9][0-9].json")), 1):
            with path.open(encoding="utf-8") as file:
                report = json.load(file)
            provided_hash = report.pop("report_hash", None)
            if (
                report.get("session_id") != session_id
                or report.get("sequence") != expected
                or provided_hash != stable_hash(report)
                or report.get("simulation_only") is not True
                or report.get("broker_submission") is not False
            ):
                raise ValueError("local simulation report integrity/sequence failure")
            reports.append({**report, "report_hash": provided_hash})
        return tuple(reports)


def start_session(
    *, session_id: str, initial_harness: MultiSimulationHarness,
    source_kind: SourceKind, now: datetime,
) -> OwnerSimulationSession:
    if not SESSION_ID.fullmatch(session_id):
        raise ValueError("invalid session id")
    if not isinstance(source_kind, SourceKind):
        raise ValueError("source kind must be explicitly declared")
    if not isinstance(initial_harness, MultiSimulationHarness):
        raise ValueError("canonical OBSIM harness required")
    if len(initial_harness.lanes) != 3 or {s.lane for s in initial_harness.lanes} != set(LANES):
        raise ValueError("three independent simulation lanes required")
    if initial_harness.market_frames or any(
        s.positions or s.trades or s.decisions or s.receipts or s.time_bindings or s.review_history
        for s in initial_harness.lanes
    ):
        raise ValueError("start with a fresh harness; no silent reset")
    instant = _utc(now)
    return OwnerSimulationSession(
        session_id=session_id, initial_harness=initial_harness,
        source_kind=source_kind, started_at=instant, last_tick_at=instant,
    )


def tick_session(
    session: OwnerSimulationSession, step: ReplayStep, *,
    now: datetime, store: LocalSimulationReportStore,
    effective_policy: dict[str, object] | None = None,
) -> OwnerSimulationSession:
    if session.status is not SessionStatus.RUNNING:
        raise ValueError("session is not running")
    instant = _utc(now)
    if instant - session.last_tick_at < timedelta(seconds=INTERVAL_SECONDS):
        raise ValueError("next report is not due")
    if len(session.steps) >= MAX_TICKS:
        raise ValueError("bounded beta session exhausted; stop and start a new session")
    if not isinstance(step, ReplayStep):
        raise ValueError("caller must supply a canonical historical/simulated replay step")
    observed = _observed(step.frame.observed_at)
    if observed > instant:
        raise ValueError("cannot report an observation from the future")
    if not isinstance(step.frame.source_reference, str) or not step.frame.source_reference.strip():
        raise ValueError("market frame requires explicit source reference")

    # Recompute against an untouched fresh harness: never bypass accepted replay
    # validation, synthetic fills, CAPSIM, OBTIME, receipt chain, or lane isolation.
    result = replay_three_lanes(
        session.initial_harness, session.steps + (step,), effective_policy=effective_policy,
    )
    current = result.report["comparison"]["lanes"]
    previous = (
        session.reports[-1]["lanes"]
        if session.reports else compare_simulation_lanes(session.initial_harness)["lanes"]
    )
    deltas = {
        lane.value: {
            "equity": current[lane.value]["equity"] - previous[lane.value]["equity"],
            "realized_pnl": current[lane.value]["realized_pnl"] - previous[lane.value]["realized_pnl"],
            "unrealized_pnl": current[lane.value]["unrealized_pnl"] - previous[lane.value]["unrealized_pnl"],
            "trades": current[lane.value]["trades"] - previous[lane.value]["trades"],
        }
        for lane in LANES
    }
    age = (instant - observed).total_seconds()
    freshness = (
        session.source_kind.value
        if session.source_kind is not SourceKind.LIVE_OBSERVED
        else ("FRESH" if age <= 120 else "STALE")
    )
    events = [
        {
            "lane": e.lane.value, "decision_id": e.decision_id,
            "action": e.action.value, "status": e.status,
            "capital_assessment_id": e.capital_assessment_id,
            "capital_admission_id": e.capital_admission_id,
        }
        for e in result.events[-3:]
    ]
    material = {
        "schema_version": SCHEMA_VERSION, "service_version": SERVICE_VERSION,
        "session_id": session.session_id, "sequence": len(session.steps) + 1,
        "interval_seconds": INTERVAL_SECONDS, "reported_at_utc": instant.isoformat(),
        "frame_id": step.frame.frame_id, "observed_at": step.frame.observed_at,
        "source_reference": step.frame.source_reference,
        "source_kind": session.source_kind.value, "source_claim_verified": False,
        "source_age_seconds": age, "source_freshness": freshness,
        "market_time_receipt_id": step.market_time.receipt_id,
        "lanes": current, "deltas": deltas, "events": events,
        "replay_report_hash": result.report["report_hash"],
        "receipt_chains_valid": all(row["receipt_chain_valid"] for row in current.values()),
        "simulation_only": True, "broker_submission": False,
        "capital_movement": False, "manual_live_unlock": False,
        "hybrid_unlock": False, "automated_unlock": False,
        "winner_selected": False,
    }
    report = _hash_report(material)
    # Save first. If replay/persistence fails, caller's immutable session is unchanged.
    store.save_tick(report)
    return replace(
        session, steps=session.steps + (step,), reports=session.reports + (report,),
        last_tick_at=instant,
    )


def pause_session(session: OwnerSimulationSession) -> OwnerSimulationSession:
    if session.status is not SessionStatus.RUNNING:
        raise ValueError("only running sessions can pause")
    return replace(session, status=SessionStatus.PAUSED)


def resume_session(session: OwnerSimulationSession, *, now: datetime) -> OwnerSimulationSession:
    if session.status is not SessionStatus.PAUSED:
        raise ValueError("only paused sessions can resume")
    instant = _utc(now)
    if instant < session.last_tick_at:
        raise ValueError("resume clock cannot go backwards")
    # Require a fresh full 30-second interval; no burst catch-up after pause.
    return replace(session, status=SessionStatus.RUNNING, last_tick_at=instant)


def stop_session(
    session: OwnerSimulationSession, *, now: datetime, store: LocalSimulationReportStore,
) -> OwnerSimulationSession:
    if session.status is SessionStatus.STOPPED:
        raise ValueError("session already stopped")
    instant = _utc(now)
    if instant < session.last_tick_at:
        raise ValueError("stop clock cannot go backwards")
    last_lanes = (
        session.reports[-1]["lanes"]
        if session.reports else compare_simulation_lanes(session.initial_harness)["lanes"]
    )
    material = {
        "schema_version": SCHEMA_VERSION, "session_id": session.session_id,
        "stopped_at_utc": instant.isoformat(), "total_ticks": len(session.reports),
        "last_report_hash": session.reports[-1]["report_hash"] if session.reports else None,
        "lanes": last_lanes, "simulation_only": True, "broker_submission": False,
        "capital_movement": False,
    }
    store.save_final(_hash_report(material))
    return replace(session, status=SessionStatus.STOPPED)


def session_contract() -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION, "service_version": SERVICE_VERSION,
        "owner_initiated": True, "interval_seconds": INTERVAL_SECONDS,
        "three_isolated_existing_lanes": True, "fresh_harness_replay": True,
        "bounded_beta_max_ticks": MAX_TICKS, "local_report_only": True,
        "caller_supplies_verified_market_time_and_explicit_decisions": True,
        "no_unattended_timer_or_hosting": True, "no_price_feed_or_trade_generator": True,
        "simulation_only": True, "broker_submission": False, "capital_movement": False,
        "manual_live_unlock": False, "hybrid_unlock": False, "automated_unlock": False,
    }
