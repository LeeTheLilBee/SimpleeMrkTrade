# OBSCAN041–055 — Market Data Desk: operating process and protected UI

**Status:** Stacked, source-only draft on PR #206; not deployed or registered with the hosted Tower app. No provider accounts, credentials, paid plans, live market-price requests, automatic polling, trading actions or role unlocks are introduced. PR #205 and #206 must be reviewed in order.

## Owner experience

The Observatory gains its own **Market Data Desk**, not a tab crammed into the scanner. A dedicated celestial/glass room at proposed exact path `GET /ob/data-desk` has:

- Soulaana source-truth and next-step focus card; no generic success text when no live feed is attached.
- Metrics for catalog products, verified live feeds, review queue and traffic budget (unknown is **—**, never fabricated zero).
- Provider constellation with filter chips (All/Stocks/Options/Research), scope and status badges; each card opens an accessible details drawer.
- Seven-step onboarding rail, owner review queue, feed traffic/health space and exception/rights boundary.
- Responsive narrow/mobile layout, keyboard Escape/focus restoration, reduced-motion/forced-colors support.
- The same existing hover MENU with a conditional owner Data Desk destination. The link appears only if the **server** provides `data-ob-data-desk-route-enabled=true` on a page after Tower's exact route is mapped. A client marker is presentation only, not auth.
- No browser fields for vendor credentials, no misleading “Connect now”, no client-side approval actions, no vendor `fetch`, WebSocket or browser-scanned market prices.

## Operating process (one case per exact provider PRODUCT/source)

1. **DISCOVERED:** find candidate feed or research source. Review actual origin; reference/event products remain discovery-only.
2. **RIGHTS_REVIEW:** record an independent reviewed `SourceRights` with source ID, upstream family, product instrument, automated non-display right, owner/invitee display, redistribution, real-time scope and expiry. Personal brokerage access is not automatically business or invitee distribution permission.
3. **CONFIGURATION_PENDING:** verify a backend-only secret reference. Do not store key material, credential names or raw account identifiers in the process or UI.
4. **VERIFICATION_PENDING:** independently test authenticated read-only transport, actual entitlement, true provider event timestamp, canonical market clock, non-indicative real-time data and measured provider limits. An installed adapter, screenshot, static fixture or Tradier sandbox does not prove a live feed.
5. **OWNER_APPROVAL:** require fresh Tower owner step-up and an auditable authority receipt. Browser UI is strictly read-only. A source-only code branch does not grant owner approval.
6. **OBSERVING:** keep entitlement expiry, vendor request quotas, streaming contract symbols, quote freshness, cross-feed upstream independence, options identity and conflict holds visible. The gateway still independently checks every observation before Survey research; process approval alone is not a quote.
7. **HOLD / REVOKED:** hold stale/expired/mislicensed/conflicting source. Revoke from actual gateway and purge its stored observations; new permission needs a newly reviewed source/case, not a click that silently turns the old source back on.

Receipt IDs are unique and append-only *within the in-memory process contract*; a production backend must persist them transactionally, enforce backend-only transitions and maintain audit history. On restart or missing authoritative storage, do NOT reassert approval. `ProviderDeskProcess` does not mutate the live `UniversalMarketGateway`: an independent trusted integration must couple completed review to `install()`, handle revoke `revoke()`, and validate every new quote. Read-only source projections do not promise a healthy live connection.

## Contract and route files

- `engine/market_intake/desk_process.py`: typed workflow, receipts, proof and step-up gates, fail-closed status.
- `engine/market_intake/desk_projection.py`: no-price `OB_MARKET_DATA_DESK_V1` projection based on the existing gateway and process.
- `web/ob_market_data_desk_route.py`: **unregistered**, exact Flask blueprint; injected trusted Tower guard must return literal `True` before protected snapshot callback is called. Malformed snapshot 503, no-store, GET/HEAD only, no wildcard routes.
- `web/templates/market_data_desk.html`, `web/static/ob/ob_market_data_desk.css`, `web/static/ob/ob_market_data_desk.js`: UI and sealed, optional server JSON.
- `web/static/ob/ob_nav_shell.js`: feature-gated nav link and room identity. Other rooms get the server-set marker only after the hosted route is actually mapped.
- `tests/test_obscan041_055_market_data_desk.py`: synthetic source tests, strict transition and owner boundary tests.

**No current market-price feed:** the template can show a clearly labeled *catalog preview*, with all planned sources NOT CONFIGURED/REFERENCE ONLY, or it can display the strictly shaped server snapshot. It never silently invents active feeds, API usage, streaming, prices or approved connections.

## Tower selective integration request

1. Review and merge scanner PR #205 → gateway PR #206 → this PR in order or selectively port exact source changes. Do **not** wholesale merge the independently evolving OB visual PR #166 or hosted Tower UI PR #169/#177.
2. Add exact `/ob/data-desk` route to Tower protected map, owner-only normal read; require valid owner identity, Tower→OB session launch, fresh step-up, active OB access and default-deny/revocation checks. No broad `/ob/*` wildcard. Unknown methods and paths remain denied.
3. Mount only the approved blueprint with **real backend** authority callback and server-side `build_desk_snapshot()` or a stricter equivalent. No proof/approval actions exposed as GET, client-side forms, or query parameters. Read-only user/member/invitee requests must fail.
4. The template and CSS/JS must be loaded as protected assets and checked for current UI/appearance integration. On every approved room using the shared hover rail, server set the route-enabled marker (presentation only); before this, keep the nav item suppressed to avoid sending the owner into an unmapped Tower corridor.
5. Persist case receipt state and connect real rights verification, protected credential storage, tests and telemetry independently. Only after actual reviewed entitlement and successful transport can real runtime health show verified connections, with complete source/venue/coverage/timestamp semantics.
6. Validate all protected rooms and exact route on deployed SHA with anonymous, member, expired-session, stale-step-up, revoked-owner and owner test matrix. No deploy/paid service/broker access from this PR alone.

**Governance:** Market Data Desk is operational health and intake administration. Market Map displays eligible projected market findings. Trade/Review Center and broker router retain entirely separate mode, capital and execution controls. No provider or Soulaana conclusion bypasses admission, Tower or owner decisions.

## Offline verification

```sh
python -m compileall -q engine/market_intake web/ob_market_data_desk_route.py
node --check web/static/ob/ob_market_data_desk.js
node --check web/static/ob/ob_nav_shell.js
python -m pytest -q tests/test_obscan001_025_sovereign_intake.py tests/test_obscan026_040_universal_gateway.py tests/test_obscan041_055_market_data_desk.py tests/test_obscan_public_edgar_fetch.py
```
