from __future__ import annotations

from flask import jsonify, redirect

from tower.security_map_service import (
    build_tower_security_map,
    security_map_status_cards,
)
from tower.tower_human_login_ob_launch import owner_session_active


def _tower_security_map_html() -> str:
    security_map = build_tower_security_map()
    summary = security_map["summary"]
    cards = security_map_status_cards()
    apps = security_map["apps"]
    routes = security_map["routes"]

    card_html = "\n".join(
        f"""
        <article class="tower-card tower-card-{card['status']}">
          <div class="tower-card-label">{card['title']}</div>
          <div class="tower-card-value">{card['value']}</div>
          <p>{card['meaning']}</p>
        </article>
        """
        for card in cards
    )

    app_html = "\n".join(
        f"""
        <article class="tower-row">
          <div>
            <strong>{app['app_name']}</strong>
            <span>{app['app_status']}</span>
          </div>
          <p>{app['explanation']}</p>
        </article>
        """
        for app in apps
    )

    route_html = "\n".join(
        f"""
        <article class="tower-route">
          <div class="tower-route-main">
            <strong>{route['route']}</strong>
            <span>{route['label']}</span>
          </div>
          <div class="tower-route-chips">
            <span>{route['lock_state']}</span>
            <span>{'owner-only' if route['owner_only'] else 'step-up' if route['requires_step_up'] else 'protected'}</span>
            <span>{route['risk_level']}</span>
            {('<span>placeholder</span>' if route['temporary_placeholder'] else '')}
          </div>
          <p>{route['explanation']}</p>
        </article>
        """
        for route in routes
    )

    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tower · Security Map</title>
        <style>
          :root {{
            --bg: #080510;
            --panel: rgba(255,255,255,0.075);
            --panel-strong: rgba(255,255,255,0.12);
            --text: #f8f3ff;
            --muted: #c8b8e8;
            --gold: #f6d77b;
            --violet: #8d6bff;
            --border: rgba(246,215,123,0.28);
            --danger: #ffb4b4;
            --good: #baf7d1;
          }}

          * {{
            box-sizing: border-box;
          }}

          body {{
            margin: 0;
            min-height: 100vh;
            background:
              radial-gradient(circle at top left, rgba(141,107,255,0.28), transparent 36rem),
              radial-gradient(circle at 80% 12%, rgba(246,215,123,0.13), transparent 30rem),
              var(--bg);
            color: var(--text);
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}

          main {{
            width: min(1180px, calc(100% - 32px));
            margin: 0 auto;
            padding: 36px 0 56px;
          }}

          .tower-hero {{
            border: 1px solid var(--border);
            background: linear-gradient(135deg, rgba(255,255,255,0.10), rgba(255,255,255,0.035));
            box-shadow: 0 24px 80px rgba(0,0,0,0.38);
            border-radius: 28px;
            padding: 30px;
            margin-bottom: 22px;
          }}

          .eyebrow {{
            color: var(--gold);
            text-transform: uppercase;
            letter-spacing: .16em;
            font-size: 12px;
            font-weight: 800;
          }}

          h1 {{
            margin: 10px 0 10px;
            font-size: clamp(34px, 5vw, 64px);
            line-height: .95;
          }}

          .hero-copy {{
            color: var(--muted);
            font-size: 18px;
            max-width: 860px;
            line-height: 1.55;
          }}

          .summary-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin: 22px 0;
          }}

          .tower-card {{
            border: 1px solid rgba(255,255,255,0.12);
            background: var(--panel);
            border-radius: 22px;
            padding: 18px;
            min-height: 150px;
          }}

          .tower-card-label {{
            color: var(--muted);
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .12em;
          }}

          .tower-card-value {{
            color: var(--gold);
            font-size: 34px;
            font-weight: 900;
            margin: 10px 0;
          }}

          .tower-card p,
          .tower-row p,
          .tower-route p {{
            color: var(--muted);
            line-height: 1.45;
            margin-bottom: 0;
          }}

          .tower-section {{
            margin-top: 24px;
            border: 1px solid rgba(255,255,255,0.10);
            background: rgba(0,0,0,0.18);
            border-radius: 26px;
            padding: 22px;
          }}

          .tower-section h2 {{
            margin: 0 0 14px;
            font-size: 24px;
          }}

          .tower-row,
          .tower-route {{
            border: 1px solid rgba(255,255,255,0.10);
            background: var(--panel);
            border-radius: 18px;
            padding: 16px;
            margin-top: 12px;
          }}

          .tower-row div,
          .tower-route-main {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: center;
          }}

          .tower-row span,
          .tower-route-main span {{
            color: var(--gold);
            font-size: 13px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: .10em;
          }}

          .tower-route-chips {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-top: 12px;
          }}

          .tower-route-chips span {{
            border: 1px solid rgba(246,215,123,0.25);
            background: rgba(246,215,123,0.08);
            color: var(--gold);
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 800;
          }}

          .tower-next {{
            margin-top: 22px;
            border: 1px solid rgba(186,247,209,0.28);
            background: rgba(186,247,209,0.08);
            border-radius: 22px;
            padding: 18px;
          }}

          .tower-next strong {{
            color: var(--good);
          }}

          @media (max-width: 820px) {{
            .summary-grid {{
              grid-template-columns: 1fr;
            }}

            .tower-row div,
            .tower-route-main {{
              align-items: flex-start;
              flex-direction: column;
            }}
          }}
        </style>
      </head>
      <body>
        <main>
          <section class="tower-hero">
            <div class="eyebrow">Tower Security Map</div>
            <h1>The lock map is visible now.</h1>
            <p class="hero-copy">{summary['tower_meaning']}</p>
          </section>

          <section class="summary-grid">
            {card_html}
          </section>

          <section class="tower-section">
            <h2>Registered Simplee rooms</h2>
            {app_html}
          </section>

          <section class="tower-section">
            <h2>Protected route coverage</h2>
            {route_html}
          </section>

          <section class="tower-next">
            <strong>Owner next move:</strong>
            {summary['owner_next_action']}
          </section>
        </main>
      </body>
    </html>
    """


def register_tower_security_map_routes(app):
    marker = "_tower_security_map_routes_registered"

    if getattr(app, marker, False):
        return app

    @app.route("/tower/security-map")
    def tower_security_map_page():
        if not owner_session_active():
            return redirect("/tower/login")
        return _tower_security_map_html()

    @app.route("/tower/security-map.json")
    def tower_security_map_json():
        if not owner_session_active():
            return redirect("/tower/login")
        return jsonify(build_tower_security_map())

    setattr(
        app,
        marker,
        True,
    )

    return app
