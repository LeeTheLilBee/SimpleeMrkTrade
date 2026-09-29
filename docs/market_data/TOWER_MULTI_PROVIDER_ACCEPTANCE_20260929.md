# Tower multi-provider acceptance and information dissemination — 2026-09-29

This reconciliation is based on the **current** hosted Tower, which already has Public owner connect fixes through #230 and four official no-login source panels from #231. It selectively stages the protected Finnhub/Alpha Vantage API Key Desk proposed in #232 without overwriting #231's Market Desk, keyless panels, current canonical Trade/Review links, reciprocal OB→Tower return or existing Public flow.

## Four different kinds of evidence
1. **Credential entered:** The exact owner session temporarily holds a Finnhub or Alpha Vantage key in one worker's RAM, up to 30 minutes. No browser cookie, repository, Render env, URL or permanent Vault entry contains it. A forgotten/expired/restarted session loses it.
2. **Read-only provider reachability:** Only an explicit protected owner action can perform a one-shot, fixed official probe. Successful syntax/auth is not commercial/internal-use permission, not a SIP/OPRA quote grant, and not a connected gateway source.
3. **Source use and display reviewed:** The pre-existing keyless SEC/BLS/Treasury/OpenFIGI system independently requires per-provider owner-use/display settings, then its own HTTPS retrieval/source period. A configured flag alone is not a successful data fetch, source timestamp, current quote, or AI grant.
4. **Live data accepted:** Not supplied by this patch. Public's actual account list is separately checked; successful token exchange with `accounts: []` cannot be presented as an account connection. No provider key is installed into `UniversalMarketGateway`, `engine-feed-snapshot.json`, Trade Center or brokerage execution.

## Tower-owned dissemination
- Authenticated owner-only exact GET `/ob/data-desk/connections.json` returns **OB_TOWER_PROVIDER_CONNECTION_TRUTH_V1**. It reads only sanitized, same-session Public and temporary-key status from server-only reader functions and configured keyless source-review flags. It never calls a vendor or returns a key, bearer, account ID, quote, raw portfolio, source response, rate-limit budget or inferred live-feed count.
- The Market Data Desk renders that status through `ob_connection_truth.js` with `textContent` and same-origin/no-store GET. It also retains #231's independently protected `/ob/research/keyless.json` shared rail in the other OB rooms. The new status endpoint is a typed read-only contract reusable by later protected room cards; no direct app-to-app or browser-vendor traffic.
- All new exact routes use the authoritative signed Tower owner identity via `data_desk` clearance, fresh step-up, operational OB admission and existing default-deny. Credential POST separately requires HTTPS canonical Origin, fetch metadata, CSRF, bounded/unique form fields and opt-in feature flag.

## Release and external gates
Source introduction alone has `OB_PROVIDER_KEY_DESK_ENABLED=0` by default. No keys or Public secrets are submitted in this change. Activation requires deployment to the specific approved Tower HTTPS service and a fresh owner browser acceptance test. The real provider endpoints must have documented plan/account eligibility; internal/non-display, owner display, AI, historic retention and equity/options permissions must be reviewed **separately for each provider/product** before data ingestion or dissemination. Unattended credentials require approved durable secret storage and revocation/rotation; in-memory temporary keys cannot supply it. Public's empty linked-account list requires provider-side resolution, not invented account selection.

No paid resources, automatic background requests, licensed live stock/options data, quote fallback, broker order, capital movement or trading-mode change are authorized.
