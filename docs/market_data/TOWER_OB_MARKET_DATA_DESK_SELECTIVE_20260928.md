# Tower ↔ OB Market Data Desk selective integration review (2026-09-28)

Issue: #208. Original stacked OB source: #205 (intake) → #206 (multi-provider gateway) → #207 (seven-stage owner desk). This Tower integration selectively stages the immutable source files and exact Desk UI, NOT stale whole-branch history.

## Exact owner corridor
- `GET/HEAD /ob/data-desk` is a single explicit path in both Tower OB route guards; no wildcard, generic `/ob/*` enablement, POST, connect or approval route.
- Requires current owner session, fresh step-up and operational Tower→OB admission. The blueprint independently rechecks all three *before* accessing the snapshot.
- Source-only host builds a fresh disconnected catalog/status projection from `UniversalMarketGateway()` and `ProviderDeskProcess()` without installing a source or opening a provider transport. This deliberately has no persistent approval/audit and no runtime health.
- Rendered provider offerings are candidates only. The view has no quote payload, license, API capacity estimate, secret, market-price request, broker access, Manual Live grant, invitee display or payment.
- Source errors or invalid projection fail closed with a generic 503, no client fallback claiming a working feed.
- Existing MENU retains protected Trade/Review routes and the OB→Tower return corridor; only adds Data Desk when the page carries the server-authored route marker. Tower return supports the bounded Market Data Desk room label.

## Release distinction
The source-only owner UI and static connector catalog may pass CI, but no actual market feed is licensed, configured, entitled or authenticated by this PR. This is not a resolution of the open canonical `/ob/engine-feed-snapshot.json` source/rights corridor #199; that independent route and market-time/provenance authority must be reviewed separately before live quote presentation. No stale/delayed/indicative fallback can impersonate live quotes. In-memory workflow state must get approved transactional persistence before connecting real credentials or owner approvals.

No paid Render resource, vendor account, API key, provider session, public quote redistribution, account entitlement, purchase, broker action or trading mode change is authorized. Keep PR draft until code review and source/runtime checks; actual hosted owner walkthrough is independently required before treating the Desk as accepted.
