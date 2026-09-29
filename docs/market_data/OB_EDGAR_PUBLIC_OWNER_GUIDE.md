# OB EDGAR public research — owner activation guide (source-only)

**Status:** read-only owner/developer source and offline tests. No SEC account, SEC API key, provider subscription, broker access, automatic trade, paid Render resources, or hosted deployment. This is an additive transport for the existing **OBINTEL** symbol research contracts; it does not replace OB's scanner, candidate admission, source/time checks, Soulaana or Tower.

## Official data interfaces

- Ticker/CIK/exchange cross-reference: https://www.sec.gov/files/company_tickers_exchange.json
- Issuer submissions: https://data.sec.gov/submissions/CIK##########.json
- SEC XBRL issuer facts: https://data.sec.gov/api/xbrl/companyfacts/CIK##########.json
- API docs: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
- Developer/fair access: https://www.sec.gov/about/developer-resources ; https://www.sec.gov/about/privacy-information

**No SEC EDGAR filing account is required to read these public JSON endpoints.** Such accounts are for filers, not for this read-only collection. Registering an unrelated brokerage API key is also unnecessary.

The private contact address in the HTTP User-Agent is required to classify automated collection. Set it in a developer/host secret or local environment, **never in GitHub, public pages, logs or chat**. The collector uses at least 0.6 seconds between requests from one process, timeouts, response-size bounds, a strict official endpoint allowlist, rejects redirects, and fails closed on HTTP errors. The SEC's published threshold is **10 requests/second total per user, regardless of machines**. A multi-worker/cloud deployment must independently implement and verify a shared organization/IP throttle; one-process rate limiting alone is insufficient.

## Office manual smoke test (read-only; no hosted app change)

1. Read the official SEC API/fair-access policy, and separately review the Nasdaq Trader symbol-directory data-use terms.
2. Obtain an approved, current copy of **nasdaqlisted.txt** or **otherlisted.txt** from https://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs. This independent listed-security directory is required so a SEC ticker match alone cannot manufacture a listing.
3. Set a real business contact privately. In PowerShell:

   $env:OB_SEC_CONTACT_EMAIL="YOUR_REAL_BUSINESS_CONTACT@YOUR_DOMAIN"

4. From the repo root, with the approved file in the current directory, explicitly execute:

   python -m scripts.ob_edgar_public_probe --symbol AAPL --directory-file .\nasdaqlisted.txt --confirm-sec-policy-reviewed --confirm-directory-use-approved --confirm-single-worker

   The optional \`--enable-ai-explanation\` flag is permitted only after separately reviewing that use for the owner context. Without it, Soulaana's facts are withheld from assistant explanation.

5. The command displays the SEC CIK identity match, source-bound record state, **counts** of verified financial concepts and filing events, current-quote status and trading-denial flags. It does not log financial values, retain raw SEC payloads, create a hosted route or authorize real-time stock/options quotes.

For backend integration, a trusted, already Tower-authorized owner service must build an \`EDGARPolicy\` after source-use review, create \`EDGARPublicClient(contact)\`, instantiate \`EDGARResearchCollector(..., owner_authorized=True, single_worker_confirmed=True)\` only when actually true (otherwise configure independently reviewed shared throttling), call \`public_ticker_index()\`, and pass an independently accepted \`SymbolRow\` to \`collect_symbol(row, index)\`. The output is existing \`SymbolResearchInputs\`; \`owner_snapshot()\` passes it to the existing \`symbol_research_snapshot()\` and Soulaana's source-bound \`soulaana_research_brief()\` when AI-use permission is approved.

**Do not** expose these methods as a generic URL fetch, browser endpoint or public/admin credential entry form. The hosted Tower code intentionally has no active \`research_resolver\` until a separate verified, owner-authenticated backend integration is reviewed. Do not claim the hosted app has live SEC research because this code has landed.

## Exact data protections

- SEC identity uses a **separate** approved listed-security directory, the SEC exchange/ticker map and the exact ten-digit CIK. A mismatch holds; it never guesses.
- Companyfacts values retain original GAAP concepts, units and fiscal ends; only accepted accession timestamps from the SEC submission payload are used. Facts that cannot be independently associated with a known, no-future accession are excluded. The recent submission payload may omit much older filings: unavailable does not mean zero or a complete historical financial record.
- Issuer filing events are research leads, **not evidence of a specific price move**.
- Raw companyfacts data, provider responses, contact email or API traffic is not persisted by this prototype. The existing optional reference-only memory still checks retention rights. Historical stock candles are a separate source, and **no SEC filing grants equity or OPRA option quote permissions**.
- The manual probe runs at one process; no background worker, job, automatic schedule, paid cloud resource, order permission or trading mode is activated.
- SEC access can refuse automated clients on network reputation/User-Agent or rate-limit grounds; a failure remains \`HOLD\`. Do not bypass a block using rotating proxies or alternate accounts.

## Acceptance

Offline test: \`python -m pytest -q tests/test_ob_edgar_public_research.py tests/test_obintel001_030_symbol_research.py tests/test_obscan001_025_sovereign_intake.py\`. Also compile new modules/CLI and statically confirm no hosted source registration. A real owner SEC request and Tower runtime walkthrough remain independent gates.
