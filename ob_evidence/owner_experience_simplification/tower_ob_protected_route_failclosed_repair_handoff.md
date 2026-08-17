# Tower → OB Protected Route Fail-Closed Repair

- Base main: `4acd633e671d05a1137cfbcba0361bc779273fbe`
- Repair branch: `tower-ob-protected-route-failclosed-repair`
- Trigger: unauthenticated hosted `/ob/dashboard` returned HTTP 200 with protected Soulaana content.
- Wiring strategy: register fail-closed OB web enforcement immediately after the unique `register_tower_human_login(app)` call.
- Repair scope: actual Flask request enforcement for approved `/ob/*` rooms.
- Unknown `/ob/*`: default deny / HTTP 403.
- Anonymous approved room: redirect to Tower login.
- Normal approved room without owner step-up: redirect to Tower Access Home.
- Owner Console: remains owner-session-only.
- Owner Dashboard: untouched.
- Owner Console UI: untouched.
- GP066: parked.
- Live Auto: locked.
- Broker execution: false.
- Capital action: false.
- Deployment: not performed by this repair cell.

This is Tower security-boundary work. OB rooms are the protected target.
