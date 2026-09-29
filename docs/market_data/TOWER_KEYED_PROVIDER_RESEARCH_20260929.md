# Tower keyed-provider research dissemination — 2026-09-29

## What this closes
Tower already accepts temporary Finnhub and Alpha Vantage keys in the protected API Key Desk and publishes sanitized connection truth. This change adds the missing **content dissemination** seam without converting either provider into an OB live feed.

- Exact authenticated GET `/ob/research/providers.json?symbol=SYMBOL`.
- Requires current Tower owner session, fresh step-up and operational OB admission through the same exact-route guard as the Desk.
- Reads temporary keys only through a trusted server closure. No key/token/account identifier enters JSON, HTML, URL query, logs or Soulaana.
- One global feature switch plus provider-specific source-use and owner-display review flags are required before any provider request.
- Separate provider-specific AI-use review flag is required before Soulaana receives provider content.
- Finnhub dissemination is bounded to company-profile reference fields; no quote endpoint.
- Alpha Vantage dissemination is bounded to compact raw completed daily history; no intraday or realtime entitlement parameter.
- Five-minute per-owner/provider/symbol in-memory cache prevents every room redraw from spending provider quota.
- Shared OB source panel queries keyed providers only after an explicit ticker lookup. No background polling or automatic page-load vendor traffic.
- Output cannot authorize candidate admission, broker execution, capital movement or trading-mode changes.

## Still separate
Provider commercial/AI/display terms, upstream exchange provenance, live quote entitlement, Public account linkage, broker positions/orders, durable secret storage and any market-data redistribution remain independent gates. Existing Public connector and keyless SEC/BLS/Treasury/OpenFIGI lanes are unchanged.
