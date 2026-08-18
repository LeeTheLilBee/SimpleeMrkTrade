# OBUX035 — Legacy Market Map Retirement

The legacy Market Map implementations are retired.

Compatibility-only routes remain:

- `/market-map`
- `/market-map-v10`
- `/ob/market-map-v10`

Each redirects to the single canonical protected room:

- `/ob/market-map`

These aliases contain no Market Map rendering, engine plumbing,
fixture consumption, or independent UI behavior.

Deleted:

- `web/templates/market_map_v10.html`
- `web/static/ob/ob_market_map_symbol_page.js`

Tower route/security inventory snapshots remain unchanged so historical
route identity and default-deny bookkeeping are not silently invalidated.

Symbol Page remains independent on its own template and JavaScript.

Git history is the archive for retired implementations.
