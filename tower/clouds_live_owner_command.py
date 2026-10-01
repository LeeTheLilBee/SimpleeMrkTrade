"""Live Clouds owner-command composition for the hosted Tower runtime.

This module is intentionally presentation + navigation intent only.

Boundaries:
- Clouds reads existing summary/focus payloads.
- Tower owns protected app crossings.
- Existing app-specific launch gates remain authoritative.
- A route existing is not the same as a product being launchable.
- Missing launch corridors stay visibly blocked.
- No business action, payment, trading, storage mutation, or capital movement
  is authorized here.
"""

from __future__ import annotations

from html import escape
from typing import Any, Dict, Iterable, Mapping
from urllib.parse import quote

from flask import current_app

from clouds.clouds_app_lane_status_service import (
    get_clouds_app_status_board_payload,
)
from clouds.clouds_today_service import (
    get_clouds_today_dashboard_payload,
)
from tower.app_registry import (
    registered_apps,
)
from tower.app_truth_projection import (
    registered_app_truth_projection,
)


CORE_APP_IDS = (
    "clouds",
    "observatory",
    "teller",
    "grounds",
    "buybox",
    "vault",
    "simplee_on_the_go",
)

SOURCE_TO_TOWER_APP = {
    "clouds": "clouds",
    "tower": "tower",
    "observatory": "observatory",
    "teller": "teller",
    "archive_vault": "vault",
    "vault": "vault",
    "grounds": "grounds",
    "buybox": "buybox",
    "simplee_on_the_go": "simplee_on_the_go",
    "simplee_property": "grounds",
    "soulaana": "clouds",
    "private_beta": "clouds",
}

CLOUDS_SOURCE_BY_TOWER_APP = {
    "observatory": "observatory",
    "teller": "teller",
    "vault": "archive_vault",
    "simplee_on_the_go": "simplee_on_the_go",
}

STATUS_LABELS = {
    "verified_open": "OPEN",
    "current_clouds": "HERE",
    "protected_gate": "GATED",
    "not_published": "NOT OPEN",
    "not_mounted": "NOT MOUNTED",
    "tower_home": "OPEN",
}


def _list(value: Any) -> list:
    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if value in (None, ""):
        return []

    return [value]


def _safe_payload(factory, fallback):
    try:
        value = factory()
    except Exception:
        return fallback

    return value if isinstance(value, Mapping) else fallback


def _route_paths() -> set[str]:
    try:
        return {
            rule.rule
            for rule
            in current_app.url_map.iter_rules()
        }
    except Exception:
        return set()


def _truth_lookup() -> Dict[str, dict]:
    try:
        rows = registered_app_truth_projection()
    except Exception:
        rows = []

    return {
        str(row.get("app_id") or ""): dict(row)
        for row
        in rows
        if isinstance(row, Mapping)
        and row.get("app_id")
    }


def _registration_lookup() -> Dict[str, dict]:
    try:
        rows = registered_apps()
    except Exception:
        rows = []

    return {
        str(row.get("app_id") or ""): dict(row)
        for row
        in rows
        if isinstance(row, Mapping)
        and row.get("app_id")
    }


def _clouds_feed_lookup() -> Dict[str, dict]:
    payload = _safe_payload(
        get_clouds_app_status_board_payload,
        {"app_status_cards": []},
    )

    cards = payload.get(
        "app_status_cards",
        [],
    )

    return {
        str(card.get("app_id") or ""): dict(card)
        for card
        in cards
        if isinstance(card, Mapping)
        and card.get("app_id")
    }


def _door_state(
    *,
    app_id: str,
    launch_route: str,
    launchable: bool,
    route_paths: set[str],
) -> str:
    if app_id == "tower":
        return "tower_home"

    if app_id == "clouds":
        return "current_clouds"

    if not (
        launch_route.startswith(
            "/tower/launch/"
        )
    ):
        return "not_published"

    if launch_route not in route_paths:
        return "not_mounted"

    if launchable:
        return "verified_open"

    return "protected_gate"


def _feed_state(
    app_id: str,
    feeds: Mapping[str, Mapping[str, Any]],
) -> dict:
    if app_id == "clouds":
        return {
            "source_state": "internal_owner_command",
            "health": "ready",
            "source_label": "Clouds",
        }

    if app_id == "tower":
        card = feeds.get("tower", {})
    else:
        card = feeds.get(
            CLOUDS_SOURCE_BY_TOWER_APP.get(
                app_id,
                "",
            ),
            {},
        )

    if not card:
        return {
            "source_state": "not_connected_yet",
            "health": "not_connected",
            "source_label": app_id,
        }

    return {
        "source_state": str(
            card.get(
                "source_status",
                "unknown",
            )
        ),
        "health": str(
            card.get(
                "health",
                "unknown",
            )
        ),
        "source_label": str(
            card.get(
                "label",
                app_id,
            )
        ),
    }


def build_ecosystem_lines() -> list[dict]:
    registrations = _registration_lookup()
    truths = _truth_lookup()
    feeds = _clouds_feed_lookup()
    paths = _route_paths()

    rows = [
        {
            "app_id": "tower",
            "app_name": "The Tower",
            "registry_status": "hosted_front_door",
            "launch_route": "/tower/access-home",
            "primary_room_route": "/tower/access-home",
            "launchable": True,
            "door_state": "tower_home",
            "door_label": STATUS_LABELS["tower_home"],
            "action_route": "/tower/access-home",
            "action_label": "Open Tower",
            "feed_state": _feed_state(
                "tower",
                feeds,
            ),
            "dangerous_actions_locked": True,
            "broker_execution_enabled": False,
            "capital_action_enabled": False,
        }
    ]

    for app_id in CORE_APP_IDS:
        registration = registrations.get(
            app_id,
            {},
        )
        truth = truths.get(
            app_id,
            {},
        )

        app_name = str(
            registration.get(
                "app_name",
                app_id.replace(
                    "_",
                    " ",
                ).title(),
            )
        )

        launch_route = str(
            registration.get(
                "tower_launch_route",
                "",
            )
            or ""
        )

        if app_id == "clouds":
            launch_route = (
                "/tower/launch/clouds"
            )

        launchable = bool(
            truth.get(
                "launchable"
            )
            is True
        )

        door_state = _door_state(
            app_id=app_id,
            launch_route=launch_route,
            launchable=launchable,
            route_paths=paths,
        )

        if door_state in {
            "verified_open",
            "protected_gate",
            "current_clouds",
        }:
            action_route = (
                "/tower/clouds/open/"
                + quote(
                    app_id,
                    safe="",
                )
            )
            action_label = (
                "Open through Tower"
                if app_id != "clouds"
                else "Stay in Clouds"
            )
        else:
            action_route = (
                "/tower/integrations?app="
                + quote(
                    app_id,
                    safe="",
                )
            )
            action_label = (
                "View blockers"
            )

        rows.append(
            {
                "app_id": app_id,
                "app_name": app_name,
                "registry_status": str(
                    registration.get(
                        "app_status",
                        "unregistered",
                    )
                ),
                "launch_route": launch_route,
                "primary_room_route": str(
                    registration.get(
                        "primary_room_route",
                        "",
                    )
                ),
                "launchable": launchable,
                "door_state": door_state,
                "door_label": STATUS_LABELS.get(
                    door_state,
                    door_state.upper(),
                ),
                "action_route": action_route,
                "action_label": action_label,
                "feed_state": _feed_state(
                    app_id,
                    feeds,
                ),
                "dangerous_actions_locked": bool(
                    registration.get(
                        "dangerous_actions_locked",
                        True,
                    )
                ),
                "broker_execution_enabled": bool(
                    registration.get(
                        "broker_execution_enabled",
                        False,
                    )
                ),
                "capital_action_enabled": bool(
                    registration.get(
                        "capital_action_enabled",
                        False,
                    )
                ),
            }
        )

    seen = {
        row["app_id"]
        for row
        in rows
    }

    for app_id, registration in registrations.items():
        if app_id in seen:
            continue

        truth = truths.get(
            app_id,
            {},
        )

        launch_route = str(
            registration.get(
                "tower_launch_route",
                "",
            )
            or ""
        )

        launchable = bool(
            truth.get(
                "launchable"
            )
            is True
        )

        door_state = _door_state(
            app_id=app_id,
            launch_route=launch_route,
            launchable=launchable,
            route_paths=paths,
        )

        rows.append(
            {
                "app_id": app_id,
                "app_name": str(
                    registration.get(
                        "app_name",
                        app_id,
                    )
                ),
                "registry_status": str(
                    registration.get(
                        "app_status",
                        "unregistered",
                    )
                ),
                "launch_route": launch_route,
                "primary_room_route": str(
                    registration.get(
                        "primary_room_route",
                        "",
                    )
                ),
                "launchable": launchable,
                "door_state": door_state,
                "door_label": STATUS_LABELS.get(
                    door_state,
                    door_state.upper(),
                ),
                "action_route": (
                    "/tower/integrations?app="
                    + quote(
                        app_id,
                        safe="",
                    )
                ),
                "action_label": "View integration",
                "feed_state": _feed_state(
                    app_id,
                    feeds,
                ),
                "dangerous_actions_locked": bool(
                    registration.get(
                        "dangerous_actions_locked",
                        True,
                    )
                ),
                "broker_execution_enabled": bool(
                    registration.get(
                        "broker_execution_enabled",
                        False,
                    )
                ),
                "capital_action_enabled": bool(
                    registration.get(
                        "capital_action_enabled",
                        False,
                    )
                ),
            }
        )

    return rows


def _line_lookup(
    lines: Iterable[Mapping[str, Any]],
) -> Dict[str, dict]:
    return {
        str(line.get("app_id") or ""): dict(line)
        for line
        in lines
        if isinstance(line, Mapping)
        and line.get("app_id")
    }


def _focus_action(
    item: Mapping[str, Any],
    lines: Mapping[str, Mapping[str, Any]],
) -> dict:
    source_app = str(
        item.get(
            "source_app",
            "",
        )
        or ""
    )

    tower_app = SOURCE_TO_TOWER_APP.get(
        source_app,
        "",
    )

    if source_app == "tower":
        return {
            "tower_app": "tower",
            "route": "/tower/access-home",
            "label": "Open Tower",
            "state": "tower_home",
        }

    if not tower_app:
        return {
            "tower_app": "",
            "route": "/tower/integrations",
            "label": "View integration",
            "state": "unknown_source",
        }

    line = lines.get(
        tower_app,
        {},
    )

    return {
        "tower_app": tower_app,
        "route": str(
            line.get(
                "action_route",
                "/tower/integrations",
            )
        ),
        "label": str(
            line.get(
                "action_label",
                "View integration",
            )
        ),
        "state": str(
            line.get(
                "door_state",
                "not_published",
            )
        ),
    }


def build_owner_command_payload() -> dict:
    today = _safe_payload(
        get_clouds_today_dashboard_payload,
        {
            "today_focus": {
                "focus_count": 0,
                "critical_count": 0,
                "high_count": 0,
                "ready_count": 0,
                "blocked_count": 0,
                "today_top_items": [],
            },
            "today_watch": {
                "watch_card_count": 0,
                "watch_cards": [],
                "blocked_reason_count": 0,
                "placeholder_count": 0,
            },
            "snapshot": {
                "snapshot_status": "unavailable",
                "vault_final_score": None,
                "clouds_view": "summary unavailable",
                "cards": [],
            },
        },
    )

    lines = build_ecosystem_lines()
    line_by_id = _line_lookup(
        lines
    )

    focus = dict(
        today.get(
            "today_focus",
            {},
        )
        or {}
    )

    top_items = [
        dict(item)
        for item
        in _list(
            focus.get(
                "today_top_items",
                [],
            )
        )
        if isinstance(
            item,
            Mapping,
        )
    ]

    needs_you = []
    keep_watching = []
    can_wait = []

    for item in top_items:
        priority = str(
            item.get(
                "priority",
                "medium",
            )
        )
        blocked_by = _list(
            item.get(
                "blocked_by",
                [],
            )
        )

        card = {
            **item,
            "priority": priority,
            "blocked_by": blocked_by,
            "tower_action": _focus_action(
                item,
                line_by_id,
            ),
        }

        if priority in {
            "critical",
            "high",
        } and len(needs_you) < 6:
            needs_you.append(card)

        elif (
            blocked_by
            or str(
                item.get(
                    "status",
                    "",
                )
            )
            in {
                "watch",
                "locked",
                "placeholder_not_connected",
            }
        ):
            keep_watching.append(
                card
            )

        else:
            can_wait.append(
                card
            )

    watch_cards = [
        dict(card)
        for card
        in _list(
            today.get(
                "today_watch",
                {},
            ).get(
                "watch_cards",
                [],
            )
            if isinstance(
                today.get(
                    "today_watch",
                    {},
                ),
                Mapping,
            )
            else []
        )
        if isinstance(
            card,
            Mapping,
        )
    ]

    not_open_lines = [
        line
        for line
        in lines
        if line["door_state"]
        in {
            "not_published",
            "not_mounted",
        }
    ]

    return {
        "title": "The Clouds",
        "subtitle": "Simplee World Owner Command",
        "headline": (
            "Here is what needs you, what I am watching, "
            "and what can wait."
        ),
        "focus_summary": {
            "focus_count": int(
                focus.get(
                    "focus_count",
                    len(top_items),
                )
                or 0
            ),
            "critical_count": int(
                focus.get(
                    "critical_count",
                    0,
                )
                or 0
            ),
            "high_count": int(
                focus.get(
                    "high_count",
                    0,
                )
                or 0
            ),
            "ready_count": int(
                focus.get(
                    "ready_count",
                    0,
                )
                or 0
            ),
            "blocked_count": int(
                focus.get(
                    "blocked_count",
                    0,
                )
                or 0
            ),
        },
        "needs_you": needs_you,
        "keep_watching": keep_watching,
        "can_wait": can_wait,
        "watch_cards": watch_cards,
        "ecosystem_lines": lines,
        "not_open_count": len(
            not_open_lines
        ),
        "snapshot": dict(
            today.get(
                "snapshot",
                {},
            )
            or {}
        ),
        "boundary": {
            "clouds_can_route": True,
            "clouds_can_execute": False,
            "tower_controls_crossings": True,
            "owning_apps_keep_authority": True,
            "route_presence_is_not_launchability": True,
            "missing_lines_are_not_fake_open": True,
            "broker_execution_authorized": False,
            "capital_movement_authorized": False,
            "payroll_execution_authorized": False,
            "vault_mutation_authorized": False,
        },
    }


def _button(
    route: str,
    label: str,
    *,
    primary: bool = False,
) -> str:
    klass = (
        "button primary"
        if primary
        else "button"
    )

    return (
        f'<a class="{klass}" '
        f'href="{escape(route, quote=True)}">'
        f"{escape(label)}"
        "</a>"
    )


def _focus_card(
    item: Mapping[str, Any],
) -> str:
    label = str(
        item.get(
            "label",
            "Focus item",
        )
        or "Focus item"
    )

    source_app = str(
        item.get(
            "source_app",
            "unknown",
        )
        or "unknown"
    )

    priority = str(
        item.get(
            "priority",
            "medium",
        )
        or "medium"
    )

    status = str(
        item.get(
            "status",
            "unknown",
        )
        or "unknown"
    )

    owner_action = str(
        item.get(
            "owner_action",
            "No next-action detail was supplied by the source.",
        )
        or ""
    )

    blockers = [
        str(value)
        for value
        in _list(
            item.get(
                "blocked_by",
                [],
            )
        )
        if value
    ]

    action = dict(
        item.get(
            "tower_action",
            {},
        )
        or {}
    )

    action_route = str(
        action.get(
            "route",
            "/tower/integrations",
        )
    )

    action_label = str(
        action.get(
            "label",
            "View integration",
        )
    )

    change_copy = (
        "This current Clouds payload does not carry a delta field, "
        "so I am not inventing a change that the source did not report."
    )

    attention_copy = (
        "Blocked by: "
        + ", ".join(
            blockers
        )
        if blockers
        else (
            "The current source reports no blocker for this item. "
            "The owning app still controls any real action."
        )
    )

    wait_copy = (
        "Keep the lock in place until the owning app and Tower clear it."
        if blockers
        else (
            "No explicit can-wait signal was supplied. "
            "Clouds keeps it visible without manufacturing urgency."
        )
    )

    return f"""
    <article class="focus-card">
      <div class="focus-top">
        <div>
          <div class="source-kicker">
            {escape(source_app.replace("_", " ").title())}
          </div>
          <h3>{escape(label)}</h3>
        </div>
        <span class="status-badge">
          {escape(priority.upper())}
        </span>
      </div>

      <p class="soulaana-line">
        {escape(owner_action)}
      </p>

      <div class="chip-row compact">
        <span class="chip">
          Status · {escape(status)}
        </span>
        <span class="chip">
          Priority · {escape(priority)}
        </span>
        <span class="chip">
          Blockers · {len(blockers)}
        </span>
      </div>

      <div class="actions">
        {_button(
            action_route,
            action_label,
            primary=True,
        )}
      </div>

      <details>
        <summary>Soulaana explains</summary>
        <div class="explain-grid">
          <div>
            <strong>What it is</strong>
            <p>
              {escape(label)} is a current Clouds focus item
              from {escape(source_app)}.
            </p>
          </div>
          <div>
            <strong>What it means</strong>
            <p>{escape(owner_action)}</p>
          </div>
          <div>
            <strong>Why it matters</strong>
            <p>
              Clouds currently classifies it as
              {escape(priority)} priority and
              {escape(status)} status.
            </p>
          </div>
          <div>
            <strong>What changed</strong>
            <p>{escape(change_copy)}</p>
          </div>
          <div>
            <strong>Needs attention</strong>
            <p>{escape(attention_copy)}</p>
          </div>
          <div>
            <strong>Can wait</strong>
            <p>{escape(wait_copy)}</p>
          </div>
          <div>
            <strong>Next action</strong>
            <p>
              Use the Tower-controlled button above.
              Clouds does not perform the downstream action.
            </p>
          </div>
        </div>
      </details>
    </article>
    """


def _line_card(
    line: Mapping[str, Any],
) -> str:
    app_name = str(
        line.get(
            "app_name",
            line.get(
                "app_id",
                "App",
            ),
        )
    )

    state = str(
        line.get(
            "door_state",
            "not_published",
        )
    )

    door_label = str(
        line.get(
            "door_label",
            state,
        )
    )

    feed = dict(
        line.get(
            "feed_state",
            {},
        )
        or {}
    )

    source_state = str(
        feed.get(
            "source_state",
            "unknown",
        )
    )

    launchable = bool(
        line.get(
            "launchable"
        )
        is True
    )

    if state == "verified_open":
        explanation = (
            "Tower has a mounted protected launch and current "
            "product-level launchability is verified."
        )

    elif state == "current_clouds":
        explanation = (
            "You are already inside the protected Clouds owner command."
        )

    elif state == "protected_gate":
        explanation = (
            "The Tower launch gate exists, but current publication, "
            "health, entitlement, provider, or release truth is not fully "
            "verified. The gate will fail closed if anything is missing."
        )

    elif state == "tower_home":
        explanation = (
            "Tower is the current hosted front door."
        )

    elif state == "not_mounted":
        explanation = (
            "The registry names a launch route, but that exact route is "
            "not mounted in this runtime."
        )

    else:
        explanation = (
            "No product launch corridor is published yet. "
            "Source or packet visibility does not equal app access."
        )

    return f"""
    <article class="line-card">
      <div class="focus-top">
        <div>
          <div class="source-kicker">
            ECOSYSTEM LINE
          </div>
          <h3>{escape(app_name)}</h3>
        </div>
        <span class="status-badge">
          {escape(door_label)}
        </span>
      </div>

      <p>{escape(explanation)}</p>

      <div class="chip-row compact">
        <span class="chip">
          Feed · {escape(source_state)}
        </span>
        <span class="chip">
          Door · {escape(state)}
        </span>
        <span class="chip">
          Launchable · {str(launchable).lower()}
        </span>
      </div>

      <div class="actions">
        {_button(
            str(
                line.get(
                    "action_route",
                    "/tower/integrations",
                )
            ),
            str(
                line.get(
                    "action_label",
                    "View integration",
                )
            ),
            primary=(
                state
                in {
                    "verified_open",
                    "protected_gate",
                    "tower_home",
                }
            ),
        )}
      </div>
    </article>
    """


def _watch_card(
    card: Mapping[str, Any],
) -> str:
    label = str(
        card.get(
            "label",
            "Watch",
        )
    )

    value = card.get(
        "value",
        "—",
    )

    unit = str(
        card.get(
            "unit",
            "",
        )
    )

    summary = str(
        card.get(
            "summary",
            "",
        )
    )

    return f"""
    <article class="mini-card">
      <div class="source-kicker">
        KEEP WATCHING
      </div>
      <div class="metric">
        {escape(str(value))}
      </div>
      <strong>{escape(label)}</strong>
      <p>
        {escape(unit)}
        {(" · " if unit and summary else "")}
        {escape(summary)}
      </p>
    </article>
    """


def render_owner_command(
    *,
    page_factory,
    clouds_return_path: str,
) -> str:
    payload = build_owner_command_payload()

    needs_you = payload[
        "needs_you"
    ]

    watching = payload[
        "keep_watching"
    ]

    can_wait = payload[
        "can_wait"
    ]

    lines = payload[
        "ecosystem_lines"
    ]

    watch_cards = payload[
        "watch_cards"
    ]

    summary = payload[
        "focus_summary"
    ]

    core_lines = [
        line
        for line
        in lines
        if line["app_id"]
        in {
            "tower",
            *CORE_APP_IDS,
        }
    ]

    portfolio_lines = [
        line
        for line
        in lines
        if line["app_id"]
        not in {
            "tower",
            *CORE_APP_IDS,
        }
    ]

    needs_html = (
        "".join(
            _focus_card(
                item
            )
            for item
            in needs_you
        )
        or """
        <article class="focus-card calm-card">
          <div class="source-kicker">NEEDS YOU</div>
          <h3>No current top-focus card</h3>
          <p>
            Clouds did not return a critical or high top item.
            I did not manufacture one.
          </p>
        </article>
        """
    )

    watching_html = "".join(
        _watch_card(
            card
        )
        for card
        in watch_cards[:6]
    )

    if not watching_html:
        watching_html = """
        <article class="mini-card">
          <div class="source-kicker">KEEP WATCHING</div>
          <strong>No watch cards returned</strong>
          <p>
            The current source did not supply a watch card.
          </p>
        </article>
        """

    wait_items = (
        watching
        + can_wait
    )

    wait_html = "".join(
        _focus_card(
            item
        )
        for item
        in wait_items[:8]
    )

    core_lines_html = "".join(
        _line_card(
            line
        )
        for line
        in core_lines
    )

    portfolio_html = "".join(
        _line_card(
            line
        )
        for line
        in portfolio_lines
    )

    style = """
    <style id="clouds-live-owner-command-20261001">
      .command-rail {
        display:grid;
        grid-template-columns:repeat(5,minmax(0,1fr));
        gap:10px;
        margin-top:20px;
      }

      .command-stat,
      .mini-card {
        border:1px solid var(--line);
        border-radius:18px;
        padding:14px;
        background:rgba(255,255,255,.045);
      }

      .command-stat strong,
      .metric {
        display:block;
        font-size:1.7rem;
        line-height:1;
        margin-bottom:6px;
      }

      .command-stat span,
      .mini-card p {
        color:var(--muted);
        font-size:.78rem;
        margin:0;
      }

      .lane {
        margin-top:16px;
        border:1px solid var(--line);
        border-radius:24px;
        padding:20px;
        background:rgba(19,15,33,.82);
      }

      .lane-head {
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        gap:16px;
        margin-bottom:12px;
      }

      .lane-title {
        color:var(--gold);
        font-size:.8rem;
        font-weight:950;
        letter-spacing:.14em;
        text-transform:uppercase;
      }

      .lane-head h2 {
        margin-top:7px;
        font-size:1.35rem;
        text-transform:none;
        letter-spacing:0;
      }

      .focus-grid,
      .watch-grid,
      .line-grid {
        display:grid;
        grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
        gap:12px;
      }

      .focus-card,
      .line-card {
        border:1px solid var(--line);
        border-radius:20px;
        padding:17px;
        background:var(--panel2);
      }

      .focus-top {
        display:flex;
        justify-content:space-between;
        align-items:flex-start;
        gap:12px;
      }

      .focus-top h3 {
        margin:5px 0 0;
        font-size:1.13rem;
      }

      .source-kicker {
        color:var(--violet);
        font-size:.68rem;
        font-weight:950;
        letter-spacing:.13em;
        text-transform:uppercase;
      }

      .status-badge {
        border:1px solid var(--line);
        border-radius:999px;
        padding:7px 9px;
        font-size:.68rem;
        font-weight:950;
        color:var(--gold);
        white-space:nowrap;
      }

      .soulaana-line {
        color:var(--text);
        min-height:3em;
      }

      .compact {
        margin-top:10px;
      }

      .compact .chip {
        padding:7px 9px;
        font-size:.72rem;
      }

      .explain-grid {
        display:grid;
        grid-template-columns:repeat(2,minmax(0,1fr));
        gap:10px;
        margin-top:12px;
      }

      .explain-grid > div {
        border-radius:14px;
        padding:12px;
        background:rgba(255,255,255,.04);
      }

      .explain-grid strong {
        color:var(--gold);
        font-size:.75rem;
        text-transform:uppercase;
        letter-spacing:.06em;
      }

      .explain-grid p {
        margin:5px 0 0;
      }

      .calm-card {
        min-height:160px;
      }

      .truth-note {
        margin-top:16px;
        border:1px solid rgba(185,247,211,.20);
        border-radius:18px;
        padding:14px 16px;
        background:rgba(36,76,54,.13);
      }

      .truth-note strong {
        color:var(--good);
      }

      .quiet-summary {
        display:flex;
        justify-content:space-between;
        align-items:center;
        gap:12px;
      }

      @media (max-width:900px) {
        .command-rail {
          grid-template-columns:repeat(2,minmax(0,1fr));
        }

        .explain-grid {
          grid-template-columns:1fr;
        }
      }

      @media (max-width:560px) {
        .command-rail {
          grid-template-columns:1fr;
        }

        .lane {
          padding:14px;
        }
      }
    </style>
    """

    body = f"""
    {style}

    <div class="kicker">
      {escape(payload["subtitle"])}
    </div>

    <section class="hero">
      <h1>{escape(payload["title"])}</h1>
      <h2>Good to see you.</h2>

      <p>
        {escape(payload["headline"])}
        Soulaana leads with meaning first;
        the receipts and technical truth stay underneath.
      </p>

      <div class="command-rail">
        <div class="command-stat">
          <strong>{summary["critical_count"]}</strong>
          <span>Critical</span>
        </div>

        <div class="command-stat">
          <strong>{summary["high_count"]}</strong>
          <span>High</span>
        </div>

        <div class="command-stat">
          <strong>{summary["ready_count"]}</strong>
          <span>Ready</span>
        </div>

        <div class="command-stat">
          <strong>{summary["blocked_count"]}</strong>
          <span>Blocked</span>
        </div>

        <div class="command-stat">
          <strong>{payload["not_open_count"]}</strong>
          <span>Lines not open yet</span>
        </div>
      </div>

      <div class="truth-note">
        <strong>How to read this:</strong>
        Feed status and Door status are separate.
        A feed can exist while the app door is closed,
        and a Tower launch gate can exist while current
        publication or provider truth still blocks the crossing.
      </div>

      <div class="actions">
        {_button(
            "/tower/access-home",
            "Tower home",
        )}
        {_button(
            "/tower/integrations",
            "Integration desk",
        )}
        {_button(
            clouds_return_path,
            "Return through Tower",
        )}
      </div>
    </section>

    <section class="lane">
      <div class="lane-head">
        <div>
          <div class="lane-title">Needs You</div>
          <h2>
            The small pile to look at first.
          </h2>
        </div>
        <span class="status-badge">
          {len(needs_you)} shown
        </span>
      </div>

      <div class="focus-grid">
        {needs_html}
      </div>
    </section>

    <section class="lane">
      <div class="lane-head">
        <div>
          <div class="lane-title">Keep Watching</div>
          <h2>
            Visible without turning everything into an emergency.
          </h2>
        </div>
        <span class="status-badge">
          {len(watch_cards)} signals
        </span>
      </div>

      <div class="watch-grid">
        {watching_html}
      </div>
    </section>

    <section class="lane">
      <div class="lane-head">
        <div>
          <div class="lane-title">Ecosystem Lines</div>
          <h2>
            What Clouds can see versus what Tower can actually open.
          </h2>
        </div>
        <span class="status-badge">
          {len(core_lines)} core
        </span>
      </div>

      <div class="line-grid">
        {core_lines_html}
      </div>
    </section>

    <details class="lane">
      <summary class="quiet-summary">
        <span>
          <span class="lane-title">Can Wait</span>
          <strong>
            Quiet work stays tucked away.
          </strong>
        </span>
        <span class="status-badge">
          {len(wait_items)} focus items
        </span>
      </summary>

      <div class="focus-grid" style="margin-top:14px">
        {
            wait_html
            or '''
            <article class="focus-card">
              <h3>No quiet focus items returned.</h3>
              <p>
                I did not invent any.
              </p>
            </article>
            '''
        }
      </div>
    </details>

    <details class="lane">
      <summary class="quiet-summary">
        <span>
          <span class="lane-title">Portfolio / Later</span>
          <strong>
            Registered apps that are not part of today's core command.
          </strong>
        </span>
        <span class="status-badge">
          {len(portfolio_lines)} apps
        </span>
      </summary>

      <div class="line-grid" style="margin-top:14px">
        {portfolio_html}
      </div>
    </details>

    <details class="lane">
      <summary class="quiet-summary">
        <span>
          <span class="lane-title">Technical Truth</span>
          <strong>
            Safety boundary.
          </strong>
        </span>
      </summary>

      <div class="explain-grid">
        <div>
          <strong>Clouds</strong>
          <p>
            Sees summary/focus data, interprets it, and routes.
            It does not perform the downstream action.
          </p>
        </div>

        <div>
          <strong>Tower</strong>
          <p>
            Owns protected launch, current owner session,
            step-up, entitlement checks, and default deny.
          </p>
        </div>

        <div>
          <strong>Owning apps</strong>
          <p>
            Keep business authority after entry.
          </p>
        </div>

        <div>
          <strong>Execution</strong>
          <p>
            No broker order, payroll execution,
            capital movement, or Vault mutation is authorized here.
          </p>
        </div>
      </div>
    </details>
    """

    return page_factory(
        title=payload[
            "title"
        ],
        body=body,
    )
