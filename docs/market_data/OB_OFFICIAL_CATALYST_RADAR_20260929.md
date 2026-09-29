# OB Market Catalyst Radar — source-rights and Soulaana translation

Scope: five bounded official-publication adapters connected to the EXISTING Tower Market Data Desk via the exact owner-only GET /ob/research/catalysts.json, and a common read-only source/Soulaana card across the eight protected OB rooms. SEC EDGAR is delegated to existing Symbol Research; no duplicate SEC fetch, shared fair-access budget or fictitious filing receipt.

**Never** use this corridor as an equity/options quote, market-data subscription, options chain, candidate, capital authorization, broker transport, trading signal, or external AI-model request. No paid Render resource, third-party login, background polling or autonomous provider scanner. A source's retrieval time is NOT its publication/event time. Some publications are weekly or annual. The first two source groups run on explicit owner requests with process-local TTLs.

## Primary-source rights and limitations, checked 2026-09-29

| Source | API | Publisher's documented reuse | Scope admitted |
| --- | --- | --- | --- |
| Federal Register | https://www.federalregister.gov/developers/documentation/api/v1 | Public federal documents are US government works, subject to any separate protected third-party materials. API key not required. | Only SEC-filtered latest Rule/Proposed Rule/Notice metadata and canonical document URLs. A proposed rule is never described as effective. |
| CFTC TFF | https://publicreporting.cftc.gov/stories/s/r4w3-av2u and https://www.cftc.gov/WebPolicy/index.htm | CFTC-produced government information public domain, requested acknowledgment. Public Reporting Environment offers API access; no-key requests more heavily throttled. | Bounded gpe5-46if TFF futures-only report metadata; not live futures/options data or consolidated listed options chain. No third-party content. |
| EIA | https://www.eia.gov/about/copyrights_reuse.php and https://www.eia.gov/opendata/terms-of-service.php | EIA-generated publications/data public domain; source and publication-date acknowledgment requested. Free API key required; registration/access policy applies. | Exact weekly commercial crude-inventory series, read only after its own key and review. No key => KEY_REQUIRED, no request. |
| World Bank | https://data.worldbank.org/summary-terms-of-use | WB-produced open datasets default CC BY 4.0, commercial reuse allowed with attribution/indication of changes; exceptions on individual third-party datasets/indicators. | Exact World Development Indicators indicator NY.GDP.MKTP.CD / US, after individual metadata/source/license review flag and runtime source-ID check. No universal license assumption. |
| NOAA/NWS | https://www.weather.gov/documentation/services-web-api and https://www.weather.gov/disclaimer | NWS API intended free for any purpose, reasonable rate limits; government product disclaimer and no endorsement; identifying User-Agent required. | Actual active Georgia alert facts only. No alerts in a snapshot != definitive safety. |
| SEC EDGAR | https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data | Existing free SEC government filing/data corridor; fair-access controls and separate source review remain authoritative. | Existing owner Symbol Research link; no duplicate retrieval in radar. |

These are **source- and content-specific** reviews, not implied permission for third-party material embedded in an API response. Use public data as attributed research only. Cross-source interpretations do not claim a causal price response. Permission to process official observations in these deterministic transformations does not, by itself, authorize an external model/vendor or dissemination of otherwise restricted third-party inputs.

## Activation and approvals

Default-off: OB_CATALYST_RADAR_ENABLED=0. Independently per source prefix OB_CATALYST_<FEDERAL_REGISTER|CFTC|EIA|WORLD_BANK|NWS>_:

- COMMERCIAL_REUSE_REVIEWED=1
- AUTOMATED_USE_REVIEWED=1
- OWNER_DISPLAY_REVIEWED=1
- SOULAANA_CONTENT_REVIEWED=1 (independent from owner use/display)

Content is translated only if OB_CATALYST_SOULAANA_ENABLED=1 and the source-specific Soulaana review flag is true. World Bank additionally needs OB_CATALYST_WORLD_BANK_GDP_LICENSE_REVIEWED=1 after indicator metadata exceptions have been verified. EIA needs the free key server-side as OB_CATALYST_EIA_API_KEY; never put it in GitHub, frontend, response or a public log. No key means KEY_REQUIRED, not synthetic data. No permissions inherited from BLS, FRED, Twelve Data, FMP, Public brokerage, or other feeds. Unreviewed/revoked sources discard cache on next request. Source errors/denials become a limited SOURCE_HOLD, not a fallback to unrelated content.

Soulaana outputs OBSERVATION facts, a source-specific interpretation and limits, source reference, true source period and separate retrieval time; it DOES NOT call an LLM. TFF is clearly futures-only. Federal Register distinguishes rulemaking stage, WB GDP is annual/current USD, NWS alert geography is Georgia, and EIA is a dated inventory observation, never prices. The owner browser inserts bounded text using textContent; all API traffic is server-side behind an exact Tower route with current owner session + step-up + OB admission. Test all data using synthetic fixtures without external network.

## Remaining owner/operator acceptance

1. Confirm exact source/product permissions, per-indicator World Bank license metadata, and EIA free API registration if desired; enable only individually cleared flags.
2. On authenticated Tower owner session, open Market Data Desk / eight shared owner research surfaces, request radar and inspect source states, valid source attribution and source-native date.
3. Test production from current Render environment; source-specific 403, quota, unsupported shape or no publication stays HOLD/NO_PUBLICATION. Offline synthetic tests are NOT production receipts.
4. Do not call the broader Observatory live feed verified until separate stock/options transport and market-data entitlements are actually established.
