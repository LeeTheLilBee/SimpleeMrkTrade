
# =============================================================================
# The Tower - Security Command Dashboard Page Renderer
# Pack 020
# =============================================================================

from __future__ import annotations

import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from tower.security_command_view import build_security_command_view, load_security_command_view


TOWER_DIR = Path(__file__).resolve().parent
DATA_DIR = TOWER_DIR / "data"
HTML_PATH = DATA_DIR / "security_command_dashboard.html"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _esc(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except Exception:
        return default


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _tone_class(tone: str) -> str:
    tone = str(tone or "watch").lower().strip()
    if tone in {"critical", "danger", "urgent"}:
        return "tone-critical"
    if tone in {"high", "warning"}:
        return "tone-high"
    if tone in {"clear", "good", "ok"}:
        return "tone-clear"
    return "tone-watch"


def _render_metric_cards(cards: List[Dict[str, Any]]) -> str:
    parts = []
    for card in cards:
        label = _esc(card.get("label", "Metric"))
        value = _esc(card.get("display_value", card.get("value", 0)))
        reason = _esc(card.get("human_reason", ""))
        tone = _tone_class(str(card.get("tone", "watch")))

        parts.append(f'''
        <section class="metric-card {tone}">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <p>{reason}</p>
        </section>
        ''')

    return "\\n".join(parts)


def _render_action_hints(action_hints: List[Dict[str, Any]]) -> str:
    pills = []
    for action in _safe_list(action_hints):
        if not isinstance(action, dict):
            continue
        label = _esc(action.get("label", action.get("action", "Review")))
        reason = _esc(action.get("human_reason", ""))
        tone = _tone_class(str(action.get("tone", "watch")))
        pills.append(f'<span class="action-pill {tone}" title="{reason}">{label}</span>')
    return "\\n".join(pills)


def _render_owner_tasks(tasks: List[Dict[str, Any]]) -> str:
    if not tasks:
        return '<div class="empty-card">No owner tasks are currently available.</div>'

    parts = []
    for index, task in enumerate(tasks, start=1):
        priority = _esc(task.get("priority", "watch"))
        app_name = _esc(task.get("app_name", "unknown"))
        reason_code = _esc(task.get("reason_code", "unknown"))
        human_task = _esc(task.get("human_task", "Review this item."))
        open_count = _as_int(task.get("open_count"), 0)
        hints = _render_action_hints(_safe_list(task.get("action_hints")))

        plural = "s" if open_count != 1 else ""

        parts.append(f'''
        <article class="task-card">
          <div class="task-topline">
            <span class="task-number">#{index}</span>
            <span class="priority-chip">{priority}</span>
            <span class="app-chip">{app_name}</span>
          </div>
          <h3>{reason_code}</h3>
          <p>{human_task}</p>
          <div class="task-meta">
            <span>{open_count} open item{plural}</span>
          </div>
          <div class="action-row">{hints}</div>
        </article>
        ''')

    return "\\n".join(parts)


def _render_lane_groups(lanes: Dict[str, Any]) -> str:
    lane_order = [
        ("urgent", "Urgent"),
        ("high", "High"),
        ("watch", "Watch"),
        ("other", "Other"),
    ]

    lane_blocks = []

    for lane_key, lane_label in lane_order:
        groups = _safe_list(lanes.get(lane_key))
        cards = []

        for group in groups[:8]:
            if not isinstance(group, dict):
                continue

            app_name = _esc(group.get("app_name", "unknown"))
            reason_code = _esc(group.get("reason_code", "unknown"))
            source_type = _esc(group.get("source_type", "unknown"))
            summary = _esc(group.get("summary", "Needs review."))
            open_count = _as_int(group.get("open_count"), 0)
            priority_score = _as_int(group.get("priority_score"), 0)
            hints = _render_action_hints(_safe_list(group.get("action_hints")))

            cards.append(f'''
            <article class="group-card">
              <div class="group-topline">
                <span>{app_name}</span>
                <span>{source_type}</span>
              </div>
              <h3>{reason_code}</h3>
              <p>{summary}</p>
              <div class="group-meta">
                <span>{open_count} open</span>
                <span>score {priority_score}</span>
              </div>
              <div class="action-row">{hints}</div>
            </article>
            ''')

        if not cards:
            cards.append('<div class="empty-card">No items in this lane.</div>')

        group_plural = "s" if len(groups) != 1 else ""

        lane_blocks.append(f'''
        <section class="lane">
          <div class="lane-header">
            <h2>{lane_label}</h2>
            <span>{len(groups)} group{group_plural}</span>
          </div>
          <div class="lane-stack">
            {"".join(cards)}
          </div>
        </section>
        ''')

    return "\\n".join(lane_blocks)


def render_security_command_dashboard_html(view: Optional[Dict[str, Any]] = None) -> str:
    if view is None:
        view = load_security_command_view()
        if not view:
            view = build_security_command_view()

    hero = view.get("hero", {}) if isinstance(view.get("hero"), dict) else {}
    metrics = view.get("metrics", {}) if isinstance(view.get("metrics"), dict) else {}
    summary_cards = _safe_list(view.get("summary_cards"))
    primary_owner_tasks = _safe_list(view.get("primary_owner_tasks"))
    lanes = view.get("lanes", {}) if isinstance(view.get("lanes"), dict) else {}

    title = _esc(hero.get("title", "The Tower"))
    subtitle = _esc(hero.get("subtitle", "Security Command Dashboard"))
    headline = _esc(hero.get("headline", "The Tower needs review."))
    human_reason = _esc(hero.get("human_reason", "Review current security state."))
    state_label = _esc(hero.get("state_label", "Review"))
    hero_tone = _tone_class(str(hero.get("tone", "watch")))

    generated_at = _esc(view.get("generated_at", _utc_now()))

    open_inbox = _as_int(metrics.get("open_inbox"), 0)
    critical_alerts = _as_int(metrics.get("critical_alerts"), 0)
    high_alerts = _as_int(metrics.get("high_alerts"), 0)
    step_up_pending = _as_int(metrics.get("step_up_pending"), 0)

    metric_cards_html = _render_metric_cards(summary_cards)
    owner_tasks_html = _render_owner_tasks(primary_owner_tasks)
    lanes_html = _render_lane_groups(lanes)

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} - {subtitle}</title>
  <style>
    :root {{
      --bg: #070914;
      --panel: rgba(255,255,255,0.065);
      --panel-strong: rgba(255,255,255,0.105);
      --line: rgba(255,255,255,0.14);
      --text: #f7f2e8;
      --muted: rgba(247,242,232,0.68);
      --soft: rgba(247,242,232,0.48);
      --gold: #d8b75d;
      --red: #ff5f6d;
      --orange: #ffb86b;
      --blue: #89b7ff;
      --green: #8be7b2;
      --shadow: 0 24px 80px rgba(0,0,0,0.42);
    }}

    * {{
      box-sizing: border-box;
    }}

    body {{
      margin: 0;
      min-height: 100vh;
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at top left, rgba(216,183,93,0.18), transparent 34rem),
        radial-gradient(circle at top right, rgba(137,183,255,0.13), transparent 32rem),
        linear-gradient(135deg, #050711 0%, #0b1020 52%, #050711 100%);
    }}

    .shell {{
      width: min(1440px, calc(100% - 32px));
      margin: 0 auto;
      padding: 28px 0 48px;
    }}

    .hero {{
      border: 1px solid var(--line);
      border-radius: 30px;
      background:
        linear-gradient(135deg, rgba(255,255,255,0.11), rgba(255,255,255,0.045)),
        radial-gradient(circle at top right, rgba(216,183,93,0.18), transparent 28rem);
      box-shadow: var(--shadow);
      padding: 28px;
      display: grid;
      grid-template-columns: 1.4fr 0.9fr;
      gap: 24px;
      overflow: hidden;
      position: relative;
    }}

    .hero:before {{
      content: "";
      position: absolute;
      inset: -2px;
      background: linear-gradient(90deg, transparent, rgba(216,183,93,0.18), transparent);
      opacity: 0.7;
      pointer-events: none;
    }}

    .hero-content,
    .hero-stats {{
      position: relative;
      z-index: 1;
    }}

    .eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 10px;
      border: 1px solid rgba(216,183,93,0.34);
      border-radius: 999px;
      padding: 8px 12px;
      color: var(--gold);
      background: rgba(216,183,93,0.08);
      font-size: 0.82rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 20px 0 8px;
      font-size: clamp(2.35rem, 6vw, 5.4rem);
      line-height: 0.94;
      letter-spacing: -0.08em;
    }}

    .headline {{
      margin: 0;
      font-size: clamp(1.2rem, 2vw, 1.65rem);
      color: var(--text);
      max-width: 760px;
    }}

    .hero-reason {{
      color: var(--muted);
      max-width: 760px;
      line-height: 1.65;
      margin-top: 12px;
    }}

    .hero-stats {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}

    .stat {{
      border: 1px solid var(--line);
      border-radius: 22px;
      background: rgba(0,0,0,0.18);
      padding: 18px;
    }}

    .stat span {{
      display: block;
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .stat strong {{
      display: block;
      margin-top: 8px;
      font-size: 2rem;
    }}

    .section-title {{
      margin: 34px 0 14px;
      display: flex;
      justify-content: space-between;
      align-items: end;
      gap: 12px;
    }}

    .section-title h2 {{
      margin: 0;
      font-size: 1.2rem;
      letter-spacing: -0.03em;
    }}

    .section-title p {{
      margin: 0;
      color: var(--muted);
      font-size: 0.92rem;
    }}

    .metrics-grid {{
      display: grid;
      grid-template-columns: repeat(6, minmax(0, 1fr));
      gap: 12px;
    }}

    .metric-card,
    .task-card,
    .group-card,
    .empty-card {{
      border: 1px solid var(--line);
      border-radius: 24px;
      background: var(--panel);
      box-shadow: 0 16px 44px rgba(0,0,0,0.20);
    }}

    .metric-card {{
      padding: 18px;
      min-height: 150px;
    }}

    .metric-label {{
      color: var(--muted);
      font-size: 0.82rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .metric-value {{
      margin-top: 14px;
      font-size: 2.35rem;
      font-weight: 800;
      letter-spacing: -0.06em;
    }}

    .metric-card p,
    .task-card p,
    .group-card p,
    .empty-card {{
      color: var(--muted);
      line-height: 1.55;
      font-size: 0.92rem;
    }}

    .tone-critical {{
      border-color: rgba(255,95,109,0.42);
      box-shadow: 0 18px 50px rgba(255,95,109,0.08);
    }}

    .tone-high {{
      border-color: rgba(255,184,107,0.42);
      box-shadow: 0 18px 50px rgba(255,184,107,0.07);
    }}

    .tone-watch {{
      border-color: rgba(137,183,255,0.28);
    }}

    .tone-clear {{
      border-color: rgba(139,231,178,0.38);
      box-shadow: 0 18px 50px rgba(139,231,178,0.06);
    }}

    .tasks-grid {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
    }}

    .task-card {{
      padding: 18px;
    }}

    .task-topline,
    .group-topline,
    .group-meta,
    .task-meta {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
      color: var(--soft);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.07em;
    }}

    .task-number,
    .priority-chip,
    .app-chip,
    .action-pill {{
      border: 1px solid var(--line);
      border-radius: 999px;
      padding: 6px 9px;
      background: rgba(255,255,255,0.055);
    }}

    .task-card h3,
    .group-card h3 {{
      font-size: 1rem;
      line-height: 1.2;
      margin: 16px 0 8px;
      letter-spacing: -0.03em;
      word-break: break-word;
    }}

    .action-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}

    .action-pill {{
      color: var(--text);
      font-size: 0.75rem;
      text-transform: none;
      letter-spacing: 0;
    }}

    .lanes-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      align-items: start;
    }}

    .lane {{
      border: 1px solid var(--line);
      border-radius: 28px;
      padding: 12px;
      background: rgba(0,0,0,0.15);
      min-height: 420px;
    }}

    .lane-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 8px 14px;
      border-bottom: 1px solid var(--line);
      margin-bottom: 12px;
    }}

    .lane-header h2 {{
      margin: 0;
      font-size: 1rem;
    }}

    .lane-header span {{
      color: var(--muted);
      font-size: 0.82rem;
    }}

    .lane-stack {{
      display: grid;
      gap: 10px;
    }}

    .group-card {{
      padding: 16px;
      background: rgba(255,255,255,0.052);
    }}

    .empty-card {{
      padding: 18px;
    }}

    .footer {{
      margin-top: 34px;
      color: var(--soft);
      font-size: 0.84rem;
      text-align: center;
    }}

    @media (max-width: 1180px) {{
      .hero {{
        grid-template-columns: 1fr;
      }}

      .metrics-grid {{
        grid-template-columns: repeat(3, minmax(0, 1fr));
      }}

      .tasks-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}

      .lanes-grid {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
    }}

    @media (max-width: 720px) {{
      .shell {{
        width: min(100% - 20px, 1440px);
      }}

      .hero {{
        padding: 20px;
        border-radius: 24px;
      }}

      .hero-stats,
      .metrics-grid,
      .tasks-grid,
      .lanes-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero {hero_tone}">
      <div class="hero-content">
        <div class="eyebrow">{state_label}</div>
        <h1>{title}</h1>
        <p class="headline">{headline}</p>
        <p class="hero-reason">{human_reason}</p>
      </div>

      <div class="hero-stats">
        <div class="stat"><span>Open Inbox</span><strong>{open_inbox}</strong></div>
        <div class="stat"><span>Critical</span><strong>{critical_alerts}</strong></div>
        <div class="stat"><span>High</span><strong>{high_alerts}</strong></div>
        <div class="stat"><span>Step-Ups</span><strong>{step_up_pending}</strong></div>
      </div>
    </section>

    <div class="section-title">
      <h2>Command Metrics</h2>
      <p>Dashboard-ready cards from The Tower view model.</p>
    </div>
    <section class="metrics-grid">
      {metric_cards_html}
    </section>

    <div class="section-title">
      <h2>Primary Owner Focus</h2>
      <p>The first things the owner should review.</p>
    </div>
    <section class="tasks-grid">
      {owner_tasks_html}
    </section>

    <div class="section-title">
      <h2>Review Lanes</h2>
      <p>Grouped alerts separated by urgency.</p>
    </div>
    <section class="lanes-grid">
      {lanes_html}
    </section>

    <div class="footer">
      Generated by The Tower Security Command Renderer at {generated_at}
    </div>
  </main>
</body>
</html>'''


def save_security_command_dashboard_html(path: Optional[Path] = None) -> Dict[str, Any]:
    view = load_security_command_view()
    if not view:
        view = build_security_command_view()

    html_doc = render_security_command_dashboard_html(view=view)
    output_path = path or HTML_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_doc, encoding="utf-8")

    return {
        "ok": True,
        "status": "saved",
        "path": str(output_path),
        "bytes": len(html_doc.encode("utf-8")),
        "view_name": view.get("view_name"),
        "state": (view.get("status") or {}).get("state"),
        "open_inbox": (view.get("metrics") or {}).get("open_inbox"),
        "primary_owner_tasks": len(view.get("primary_owner_tasks") or []),
    }


def get_security_command_dashboard_html() -> str:
    if not HTML_PATH.exists():
        save_security_command_dashboard_html()
    return HTML_PATH.read_text(encoding="utf-8")
