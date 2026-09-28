# The Observatory — Living Market Sky V1
**Product, celestial visual language, data-to-object semantics, and screen-by-screen UX**
Owner design decision: September 28, 2026. Source-first candidate on `main`. No photos/stock assets or external images embedded. No Tower or trading authority changes.

## 1. Product specification: an instrument, not wallpaper
The Market Map is a navigable read-only view of **the existing canonical Observatory market projection**. It turns actual projected sectors, symbols and *explicit* membership into a spatial observatory. It does not scrape prices, infer correlations, invent market events, generate fake live quotes, invent missing symbols, score/trade/order, or create a second market-data source. A celestial coordinate is layout, not market evidence.

**User questions:** What is happening in the sky? Where is my attention? How are actual source-backed symbols arranged? What changed since the prior *observed* snapshot? Can I isolate a region, understand one symbol, and continue to Symbol Page? What is stale/missing/held? The answer should remain clear without relying on animation or color.

### One-screen hierarchy
1. A broad **Sky stage** occupies the dominant viewport, with procedural, original dark/teal/mint/deep-blue layers. A tiny fixed primary label: `MARKET SKY / Observation only`.
2. Sparse, organically placed **Regions** represent only sectors present in `marketMapContract().sectors`, never default placeholder sectors. Each region has a name, a counted source-backed symbol population, and an atmospheric visual field. Region location/nebula hue is design only.
3. Within a region, interactive **Symbol stars** represent only supplied `sector.symbols`. Explicit membership (open position, signal, candidate, watchlist) can add a labelled ring/glow, with priority only for overlapping presentational markers; never hide multiple memberships in its accessible text.
4. A **Focus drawer** opens on region/symbol selection; clicking a star must not unexpectedly leave the map. The explicit `Open Symbol Page` action navigates to the existing `/ob/symbol/<symbol>` route.
5. A short **Soulaana sky briefing** uses the existing interpretation/receipt. The raw technical evidence remains progressive disclosure. Top-three attention, not a list wall.
6. An unobtrusive **filter rail** may isolate membership types locally, not change canonical truth. A `Reset sky` control restores all projected regions. Missing/stale states visibly HOLD instead of animated hot signals.

### Spatial layout: deliberately non-stilted
- Organic deterministic geometry: stable per-sector layout keys; modest intentional offsets, depth and non-uniform cluster bounds. Avoid a circular wheel, even card grid, orbiting symbols, overlapping unreadable labels, random numbers, draggable false geography, and automatic reordering on every data refresh.
- Sky is one coherent wide field: spacious composition, nebula regions never hard rectangular cards; near/mid/far layers use restrained CSS gradients and generated point textures; no supplied photo is used as an asset.
- Focus expands a region/spotlight while neighbors visually recede, not disappear from the source. No simulated price movement, comet/flare or relationship edge when the source lacks that metric.
- Future true pan/zoom must be bounded, keyboard navigable, announce zoom, retain scene position on refresh, include `Reset view`, and not replace Symbol Page as detail destination. V1 uses accessible `Explore region` / `Show whole sky` focus without free-camera traps.
- Source refresh reuses canonical `obEngineFeedAdapterUpdated`, never a competing timer/poll. Age timer changes only age text.

## 2. Original celestial object / design-language contract
References: the owner's astronomical images are **mood references only**. Do not copy, trace, embed or distribute photographs, including a watermarked stock reference. Render original procedural texture, soft fields and CSS/SVG primitives. Palette remains **space black, telescope teal, aurora mint, moon silver and guarded red**; any amber/violet is transient secondary atmosphere, never a return to Tower's old plum/gold identity.

| Celestial visual | Meaning / restriction |
| --- | --- |
| Far-field stars | Pure decoration, aria-hidden, no fake symbol label/data. Static/reduced-motion equivalent required. |
| Diffuse nebula province | Sector identity **only when canonical sector exists**; hue is decoration, not a performance scale. |
| Named star | Canonical symbol membership in the supplied region. Stable layout position; text or accessible label always accompanies it. |
| Bright/ringed beacon | Explicit set membership: position, signal, candidate, watchlist. Label states exactly which; brightness is never a numeric score by itself. |
| Active focus glow | User hover/keyboard/selection, **not** trade opportunity or live recommendation. |
| Constellation line | Only if an explicit, provenance-labelled relation is supplied. Otherwise decorative filaments must be clearly non-data and not connect named stars. |
| Pressure/hotspot wave | Future gated metric only, with metric name, source, as-of, threshold and legend; NEVER derive from arbitrary counts or color. |
| Alert flare | Future real, source-backed alert ID, state and scope only. No visualized synthetic market event in live view. |
| Darkened / quiet sky | Display ineligible, missing or stale. Status/reason in text; no old animation suggesting current data. |

**Tokens:** `--sky-void: #02070d`; `--sky-deep: #061a27`; `--sky-teal: #34b9b0`; `--sky-mint: #9ce8d6`; `--sky-silver: #e5edf4`; `--sky-guard: #ed7f86`. WCAG-readable text and focus ring; tone-on-tone panels get opaque backing. No perpetual movement on the content layer. Support `prefers-reduced-motion: reduce` and `forced-colors: active`; all essential semantics survive without gradients.

## 3. Data-to-celestial mapping and truth contract
Read `OB_DATA_CONTRACTS_V22.marketMapContract()` and canonical engine adapter `getProjection()`, the already existing one-source pipeline. Use only `contract.sectors`, each sector's `symbols`, and the explicit `contract.open_positions/signals/candidates/watchlist` sets. Render only on `projection.display_eligible`; show current/freshness/as-of/source and canonical reason. `current_eligible` must not be inferred from display eligibility alone. Empty means empty, missing means missing, a source hash is not provider authentication.

| Input field/evidence | Object behavior | Missing/stale behavior |
| --- | --- | --- |
| Sector record + symbols | Province and contained named stars; stable non-semantic layout | No generated province/stars |
| open_positions | Named `Position` ring/chip | No position claim |
| signals | Named `Signal` ring/chip | No signal claim |
| candidates | Named `Candidate` ring/chip, owner-grade states never fabricated in normal user view | No NOW/watch inference |
| watchlist | Named `Saved` ring/chip | No saved claim |
| source/as_of/freshness | Readable source strip, age, explicit state | HOLD/unknown; never reset as_of to browser current time |
| projection.current_eligible/display_eligible/reason | Permit eligible display; canonical reason shown | Quiet empty sky with stated blocker |
| sector strength/mood/crowding | Display textual values only when actually projected | Hide metric; never compute brightness from unsupported enum |
| explicit relationship record (future) | Visible linked arc with legend and source receipt | No analytic connection |
| market momentum, volatility, volume, correlations (future) | Only via individually versioned authenticated field contracts with units/window/normalization | Decorative ambient field only; no metric animation |

**No visual overclaim:** the layout's deterministic hash is only to keep positions stable. The scene cannot be used as a proxy for spendable capital, a broker fill, real options permission, NOW advice, or execution. Soulaana narrates canonical meanings and restrictions; cannot override source. Distinguish user, owner-only and Proof/Demo contexts. Tower remains identity/permissions. Teller mediates any acquisition readiness; no direct BuyBox balance path.

## 4. Exact UI/UX flow
**Screen A / Entrance:** Tower current authentication and operational OB launch → `/ob/dashboard`; the **Dashboard is mounted under a privacy scrim**, with first-run/new-version and voluntary Soulaana check-in inside one unified popup carousel. No independent OB marketing/home/landing stage. Skip the voluntary questions without losing safe entry; a required versioned beta SOP remains acknowledged explicitly when shown. Return/OB sign-out remains Tower-governed. Do not insert a second credential step.
**Screen B / Dashboard:** first focus and Soulaana briefing; `See the sky` opens Market Map.
**Screen C / Wide Sky:** full market field, readable source badge, a brief Soulaana interpretation, restrained filter rail and three attention items. Empty feed renders a calm truthful HOLD scene. No fake sample market.
**Screen D / Region focus:** click or Enter on an actual province `Explore region`; foreground region, de-emphasize others, show count and source sector metadata; Escape/`Show whole sky` reverses without navigation. Region focus itself is not a new data fetch.
**Screen E / Symbol spotlight:** click/focus a named star; drawer shows symbol, exact memberships, region and canonical timestamp/status, `Open Symbol Page` and `Back to sky`. No unsupported price/change/contract display. Keyboard can focus individual buttons.
**Screen F / Symbol Page:** existing protected route for deep source-backed facts, Soulaana and review-only next steps. Any Trade Center link respects mode/entitlements.
**Screen G / Attention & evidence:** choose canonical existing attention item; explain source/why/what changed or missing; expand raw evidence deliberately. No dismissal of canonical BLOCK.
**Screen H / Return:** dashboard/back-to-Tower preserve authorised routing; browser/back/reset restore accessible scene; no unexpected direct market orders.

### Accessibility/acceptance
- Region labels are visible and keyboard reachable; named star labels not solely tooltips; exact memberships via aria-label and drawer. Escape closes focus, proper visible focus; skip and continue controls have accessible labels.
- Motion optional. No auto-camera, auto-scroll, audio, photoflash or high-frequency pulse. Mobile becomes stacked readable regions/explicit star controls with the same data and actions. Low-end browser may render no decorative particles and must remain functional.
- Test: no sectors/no display eligibility yields zero synthetic stars; sector focus filters presentation only; symbol selection does not trade/navigate until explicit handoff; source update replaces stale scene and selections safely; no duplicate labels; CSS/JS syntax, keyboard, reduced-motion and original prior OBUX031–035 regressions.
- Beta is an owner walkthrough checkpoint. Source merge, CI, and a Render live status do not constitute authenticated owner acceptance.

## 5. Delivery stages
- **096–100**: this integrated specification and safe, original atmospheric presentation; retain canonical renderer/empty-sky semantics.
- **101–105**: genuine coherent field, focus and symbol spotlight, responsive/keyboard fallbacks; canonical tests.
- **106–110**: check-in-first dashboard entry and Tower handoff; no Tower route/auth changes from this OB main branch.
- Later: explicit data contracts for real relationship/metric waves; independent market feed/security validation, provenance, performance budget and owner-device acceptance. Manual Live/Hybrid/Auto are unrelated separately gated releases.
