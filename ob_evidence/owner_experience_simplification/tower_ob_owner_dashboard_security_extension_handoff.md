# Tower OB Owner Dashboard Security Extension

- Base main: `9b60bab5eaca797d236d4f33fd33b1e967ae13e6`
- Branch: `tower-ob-owner-dashboard-security-extension`
- New protected route: `/ob/owner-dashboard`
- Existing owner route reconfirmed: `/ob/owner-console`
- Owner-only routes:
  - `/ob/owner-console`
  - `/ob/owner-dashboard`
- Precise route maps patched:
  - `tower/ob_web_route_enforcement.py`
  - `tower/ob_route_guard.py`
  - `tower/tower_ob_real_surface_route_map.py`
  - `web/app.py`
- Anonymous direct owner dashboard access: redirect to Tower login.
- Anonymous direct owner console access: redirect to Tower login.
- Unknown `/ob/*`: default deny / HTTP 403.
- Owner Dashboard template status: temporary `owner_console.html` placeholder until the OB design pass gives Owner Dashboard its own page.
- OB page design: not modified here.
- Tower security: extended.
- Live Auto: locked.
- Broker execution: false.
- Capital action: false.

This keeps Tower security ahead of the OB owner-page build while Solice continues the walkthrough/design pass.
