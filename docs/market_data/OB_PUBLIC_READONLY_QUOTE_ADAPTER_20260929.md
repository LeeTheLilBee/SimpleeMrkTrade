# OB Public account-scoped quote connector — source-only, September 29, 2026

Based on merged free research PR #218 and the current Tower dev branch. This patch prepares an optional, strictly read-only Public quote adapter. **No Public account has been registered/connected, no real marketdata entitlement or business rights have been verified, no bearer token has been obtained, no deployment or provider HTTP call was performed, and no live quote may be claimed.**

Official docs:
- Quotes: https://public.com/api/docs/resources/market-data/get-quotes
- Authentication: https://public.com/api/docs/quickstart
- Business API account information: https://help.public.com/en/articles/16948003-does-public-support-api-trading-for-business-accounts
- Public individual terms (personal/non-commercial): https://public.com/documents/individual-api-program

Public documents an account-scoped marketdata POST endpoint returning EQUITY and OPTION quotes with independent lastTimestamp, bidTimestamp and askTimestamp. The documented business API has no key/call fee, which does **not** establish the user's account eligibility, data use, display, non-display or redistribution grants. Individual API terms are explicitly personal and non-commercial; an OB business/invite-only application must establish the proper terms before activation.

Implemented:
- catalog keys public-account-equity and public-account-option, separately NOT_CONFIGURED, entitlement_defined (do not label SIP/OPRA/consolidated without separately verified upstream family)
- PublicReadPolicy: literal True for account scope, owner display, non-display/internal research, marketdata scope, and instrument-specific grants
- PublicReadOnlyQuoteClient.fetch_once: exactly the allowlisted account-scoped /marketdata/{accountId}/quotes endpoint, POST only, a short-lived vetted backend token injected for this call. Fixed domain; sanitized errors, redirect denied, 8s timeout, 500KB cap and 8-instrument cap. No auth token minting, account enumeration, order or preflight call, provider stream, cache or browser key.
- normalize_public_quotes: exact requested identity and SUCCESS, no duplicates; reject missing, stale/future/malformed timestamps, bad prices, crossed markets, inconsistent option strike or OCC symbol. Retain source-provided last/bid/ask stamps; conservative oldest stamp is passed forward (never receipt time as event time). Output remains quote_verified_live=false and gateway_installed=false.
- SourceRights/upstream family, provider rights expiry, verified market session and age are independent required gates in the existing UniversalMarketGateway, which does not infer a live connection from this class.
- No direct UI / Tower integration and no execution authority.

Acceptance before operational activation:
1. Confirm account category and applicable business API terms, programmatic research use, permitted owner display, AI use, retention, invitee redistribution (if contemplated) and genuine instrument-specific current quote coverage; document the actual upstream venue family and provider request limits. Do not assume Public Business trading API free access equals marketdata display or redistribution rights.
2. Owner provides credentials only in approved backend secret management, not GitHub, chat or browser. Independently obtain/rotate backend access token using Public's documented access flow; do not couple this quote adapter to trading endpoints.
3. Make approved, one-time backend connection checks and record sanitized source/entitlement evidence and per-field source timestamps; negative/auth/429 tests fail closed.
4. Explicitly bind selected reviewed SourceRights to per-instrument gateway adapters and the canonical market-time/source-provenance corridor through Tower. No quote if any last/bid/ask stamp is outside live freshness budget.
5. Preserve option market-data evidence separate from current underlying evidence, Manual Live broker/order/mode gates, capital restrictions, and invitee permissions. No synthetic/indicative/delayed fallback.

Offline validation command:
python -m pytest -q tests/test_public_quote_readonly.py tests/test_ob_public_research_sources.py tests/test_obscan026_040_universal_gateway.py tests/test_tower_ob_market_data_desk_selective.py

No provider or paid Render resource is provisioned by this source-only integration.

## Owner business account created; next safe, local proof

Public's business-account page says approved eligible business accounts include full API access. However its currently published generic authentication endpoint is explicitly named "create personal access token," and the quote endpoint says "available to individual investors." Account opening and key issuance alone do not establish that this exact token exchange or internal research/AI/owner-display use is contractually permitted for this business key. Ask Public's API desk at api-concierge@public.com to confirm applicable business token-exchange endpoint and marketdata permissions, including equity/options, internal non-display, AI processing, retention and any invitee use. Document the reply privately; do not paste a key or account ID.

**The key may have trading powers.** Our code does not invoke any order endpoint, but it cannot make Public's underlying credential itself read-only. Keep it outside chat/GitHub/any hosted service until backend controls/authorization are separately verified; do not use Public-hosted trading MCP for this test.

Local, explicit one-shot proof (no credentials in command line or stored in files):

1. On your trusted computer, get the source branch, open a terminal at repository root; Python 3.11+ required. Do not run this on a shared device or cloud CI/browser terminal.
2. py -m scripts.ob_public_local_probe previews the HOLD/default-off without prompting for any key and without contacting Public.
3. **Only once Public has confirmed business-key authentication via its documented token endpoint**, run: py -m scripts.ob_public_local_probe --business-auth-confirmed . Secret key is entered via a hidden local getpass prompt. Script obtains a 15-minute token through Public's official endpoint, retrieves only account-list metadata, shows account numbers/types without their IDs, and requires the owner to select the appropriate business account by ordinal. It prints a sanitized outcome, never account ID, secret or access token. No order, balance or positions endpoint is available in this script.
4. Only after Public confirms actual owner/non-display research and instrument-specific marketdata quote rights, run: py -m scripts.ob_public_local_probe --business-auth-confirmed --equity AAPL --quote-rights-confirmed . One source-only quote request is validated with source-reported last, bid, ask event timestamps; output has no raw prices or credentials, does not install a gateway provider or imply independent SIP/OPRA or current quote entitlement.
5. **Do not run these proof commands or set any rights flags just because the API key exists.** After a successful local test, share only the status labels and whether a quote age was reported, not terminal screenshots that may reveal private inputs. Protected Tower deployment must still be approved separately.

Troubleshooting: 401/403 → stop, verify business API scope/credentials with Public privately; 400/missing marketdata → stop, verify account/product eligibility; 429 → respect quota, no automatic retry; missing source timestamps → HOLD, never guess. The one-shot probe intentionally does not retry, persist marketdata, check balances, fetch positions, open orders or place trades.
