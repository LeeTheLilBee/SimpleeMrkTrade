# TWR-OBBETA016–020 — legacy Tower owner dashboard source-trust parity

September 27, 2026. Tower's dedicated hosted branch retained the older `OBUX021` owner dashboard JS while accepted OB `main` independently fixed its newer owner dashboard in [#92](https://github.com/LeeTheLilBee/SimpleeMrkTrade/pull/92). The old Tower `sourceLooksVerified` still elevated a normal successful HTTP JSON to `verified:true` unless a fallback/demo/preview string or literal `verified:false` appeared. Its self-declared page-global mission/history objects could also claim authenticated balances/change history. It is **not safe to copy all of main's newer layout over Tower's existing older contract**, which has different API and existing listeners.

This parity patch changes only the legacy browser contract's *interpretation*; existing Tower identity, hosted rehearsal adapter, owner dashboard route, Teller and production settings remain untouched.

- Any nonempty 200 JSON is only `source_observed:true`, never independently authenticated. Empty/invalid/error stays guarded. All four source endpoints carry `independent_provenance_authenticated:false` and `verified:false` until a different, independently designed server receipt path exists.
- Engine trust displays "declaration received / independently unverified". Manual Live readiness may display a source-observed score only as **operator practice**, explicitly separate from owner/Tower clearance and authenticated brokerage. Private beta may display received source declaration, never hosted approval or public launch.
- Page-global `OB_OWNER_MISSION_SNAPSHOT` and `OB_OWNER_CHANGE_HISTORY` self-certified fields cannot turn into spendable balances, verified milestones, patterns or invented history. The old dormant dashboard keeps its policy mission labels and source-only explanations.
- This does not change the newer Tower-hosted owner rehearsal adapter in `tower/ob_hosted_owner_rehearsal.py`: it remains explicitly opt-in, exact Tower-gated, ephemeral single-process Proof/Demo/SYNTHETIC and real Manual Live/HYBRID/AUTO HOLD.
- No new Render service, feature activation, paid storage, broker connection, trading execution, capital movement or direct BuyBox money access.

A standalone Node test executes the actual old browser module and tries forged `verified:true` endpoint payloads and a page-global fake trust balance/history. Exact-head CI also checks existing older owner-route/policy compatibility and targeted Tower hosted rehearsal regressions. The separately recorded older non-hermetic whole-suite failures must not be mislabelled a clean production gate.

No service settings or runtime deployment change is requested. Existing auto-deploy branch semantics apply only if the Tower maintainer chooses to merge this source review after its tests.
