# OB Commercial-Free Market Context

Date: 2026-09-30

## Decision

The Observatory has two reviewed zero-cost commercial market-context connector
families:

1. Twelve Data Business Basic.
2. Finazon US Equities Basic free trial.

They are intentionally separate from OB's execution-grade quote contract. Neither
connector may invent or synthesize bid/ask, NBBO, SIP, OPRA, broker truth, candidate
admission, order authority, capital authority, Manual Live or Live Auto.

## Twelve Data Business Basic

Official business pricing currently lists Basic as free and describes:
- internal non-display usage;
- real-time US equities and ETFs;
- 8 API credits/minute, 800 API credits/day;
- 8 trial WebSocket credits.

The free WebSocket credits are trial credits. They do not authorize arbitrary
eight-symbol streaming. The connector therefore requires an explicit current
provider-confirmed trial-symbol set before planning Twelve Data WebSocket
subscriptions. The default WebSocket plan is empty.

REST market context uses the fixed official `/quote` endpoint. It may normalize:
- latest/close price;
- open/high/low;
- previous close;
- volume and average volume;
- percent change;
- 52-week high/low;
- market-open indicator;
- source timestamp.

The raw values remain server-side. Twelve Data Business Basic is not treated as an
owner/browser display grant.

Official references:
- https://twelvedata.com/pricing-business
- https://twelvedata.com/docs
- https://support.twelvedata.com/en/articles/5620516-how-to-stream-the-data
- https://support.twelvedata.com/en/articles/5194610-websocket-faq

## Finazon US Equities Basic free trial

Finazon describes US Equities Basic as real-time, license-free US market data for
commercial use without a separate market-data agreement. The free-forever trial is
restricted to AAPL, TSLA and GOOG; current published limits include one WebSocket
symbol and two snapshot requests per minute.

The connector uses the fixed `/ticker_snapshot` endpoint and may normalize:
- last trade price/time;
- daily OHLCV;
- previous-day close;
- 52-week high/low and average volume;
- daily, weekly and monthly percentage change.

The runtime refuses non-trial Finazon symbols on the free lane before making a
network request.

Finazon WebSocket support is represented by a parser/planner for
`us_stocks_essential` bar events. Its official WebSocket endpoint is
`wss://ws.finazon.io/v1?apikey=...`; the credential must never be logged or exposed.

Official references:
- https://finazon.io/dataset/us_stocks_essential
- https://finazon.io/dataset/us_stocks_essential/docs/api/latest
- https://finazon.io/dataset/us_stocks_essential/docs/ws/latest

## Runtime gates

No commercial-free network request is permitted unless all applicable gates pass:

- current Tower owner session;
- temporary provider credential from the protected Key Desk;
- `OB_COMMERCIAL_FREE_MARKET_FETCH_ENABLED=1`;
- exact provider commercial-use review flag.

Provider flags:
- `OB_PROVIDER_TWELVE_DATA_BUSINESS_BASIC_REVIEWED=1`
- `OB_PROVIDER_FINAZON_US_EQUITIES_BASIC_COMMERCIAL_REVIEWED=1`

Additional rights remain independent:
- `OB_PROVIDER_TWELVE_DATA_AI_USE_REVIEWED=1`
- `OB_PROVIDER_FINAZON_AI_USE_REVIEWED=1`
- `OB_PROVIDER_FINAZON_OWNER_DISPLAY_REVIEWED=1`

The AI flags are deliberately OFF by default. A commercial/internal data-use grant
is not automatically treated as permission to provide source content to Soulaana.

## Quota-aware caching

To avoid wasting free allowances:
- Twelve Data REST context is cached for 12 seconds per owner session/provider/symbol.
- Finazon snapshots are cached for 35 seconds per owner session/provider/symbol.

Provider failures use the shared secret-safe diagnostic vocabulary. Raw provider
messages, credential-bearing URLs, credentials and account identifiers are not
returned to the browser.

## Scanner and Soulaana handoffs

Trusted server-side components receive three distinct readers:

- `ob_commercial_free_market_reader_v1`: normalized internal context;
- `ob_commercial_free_scanner_context_v1`: bounded price/volume/range watch context;
- `ob_commercial_free_soulaana_context_v1`: only source rows with a separate
  AI-use review flag.

The scanner handoff may describe movement, relative volume and 52-week-range
position. It does not alter existing scores or admit a candidate.

The Soulaana handoff remains internal non-display, deterministic at this layer and
does not call an external model. It includes no source unless that source's
provider-specific AI-use flag is explicitly reviewed.

## Browser status only

Exact protected GET:
`/ob/data-desk/commercial-free.json`

This route contains connection, rights, quota and capability status only.
It never contains market prices or raw provider payloads.

## Streaming state

WebSocket parsers and entitlement-aware slot planning are installed. No provider
WebSocket is automatically opened by this merge. A persistent upstream streaming
worker must remain default-off until credentials, exact trial-symbol eligibility,
reconnect/backoff behavior and deployment lifecycle are verified. OB's internal
`/ob/events/stream` remains a separate notification bus and does not imply an
upstream provider stream is connected.
