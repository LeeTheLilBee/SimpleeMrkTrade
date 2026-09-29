/* OBSCAN049: accessible, READ ONLY Market Data Desk view.
   No vendor network access, API key, browser approval, synthetic quotes or browser persistence.
   Future protected Tower handler may inject OB_MARKET_DATA_DESK_V1 only after owner access.
*/
(function () {
  "use strict";
  const FALLBACK = [
    ["tradier-equity","Tradier","equity","consolidated","Potential real-time production equities; check account/business use."],
    ["tradier-options","Tradier","option","consolidated","Potential production options; requires exact product permission."],
    ["alpaca-iex-equity","Alpaca","equity","venue_limited","IEX equities only; not the consolidated market."],
    ["alpaca-sip-equity","Alpaca","equity","consolidated","SIP equities require separate entitlement."],
    ["alpaca-opra-options","Alpaca","option","consolidated","OPRA options require separate entitlement."],
    ["alpaca-indicative-options","Alpaca","option","indicative","Indicative option data; not live quote authority."],
    ["ibkr-equity","Interactive Brokers","equity","entitlement_defined","Exact venue and brokerage subscription must be confirmed."],
    ["ibkr-options","Interactive Brokers","option","entitlement_defined","Options entitlement independent of equity access."],
    ["direct-sip-equity","Direct SIP","equity","consolidated","Future contractual exchange feed."],
    ["direct-opra-options","Direct OPRA","option","consolidated","Future contractual options feed."],
    ["nasdaq-directory","Nasdaq Trader","metadata","reference","Security reference and identity only, not quotes."],
    ["occ-reports","OCC","metadata","reference","Listed series, historical reports and interest context only."],
    ["sec-edgar","SEC EDGAR","event","reference","Issuer filings and disclosures; research events only."]
  ].map(function (p) {
    return { product_key:p[0],company:p[1],instrument:p[2],quote_kind:p[3],
             state:p[3]==="reference"?"REFERENCE_ONLY":"NOT_CONFIGURED",
             description:p[4] };
  });
  const NEXT = {
    NOT_CONFIGURED:"Review this product's rights and secure exact-source credentials.",
    REFERENCE_ONLY:"Review source terms; use for identity or event discovery, never quote truth.",
    SOURCE_ONLY_READY:"Mapping exists, but no actual authorized live transport is verified here.",
    RIGHTS_HOLD:"Review the exact source entitlement and expiry; do not display quotes.",
    DISCOVERED:"Begin source and business-use rights review.",
    RIGHTS_REVIEW:"Verify instrument, non-display, owner/invitee display, redistribution and expiry.",
    CONFIGURATION_PENDING:"Use server-held credentials, never browser fields or source control.",
    VERIFICATION_PENDING:"Test authenticated live coverage, event timestamps, limits and clock.",
    OWNER_APPROVAL:"Request an independent fresh Tower owner step-up through protected backend.",
    OBSERVING:"Continue freshness/traffic/conflict checks; no execution permission.",
    HOLD:"Inspect reason, revoke or open a newly reviewed replacement case.",
    REVOKED:"This source is withdrawn. A new reviewed source identity is required."
  };
  const $ = function(id) { return document.getElementById(id); };
  const write = function(id, value) { const el=$(id); if(el) el.textContent=value; };
  const allowedStates = new Set(Object.keys(NEXT));
  const allowedInstruments = new Set(["equity","option","event","metadata"]);
  const allowedCoverage = new Set(["consolidated","venue_limited","entitlement_defined","indicative","reference"]);

  function readSnapshot() {
    try {
      const value = JSON.parse($("mddSnapshot").textContent);
      if (!value || value.schema !== "OB_MARKET_DATA_DESK_V1" || value.read_only !== true ||
          value.prices_attached !== false || !Array.isArray(value.providers) ||
          !Array.isArray(value.cases) || typeof value.summary !== "object" ||
          value.summary === null || !value.safety || value.safety.can_execute !== false ||
          value.safety.can_approve_in_browser !== false) return null;
      if (value.providers.length > 200 || value.cases.length > 200 ||
          value.providers.some(p=>!p || typeof p.product_key!=="string" ||
            typeof p.company!=="string" || p.product_key.length>100 || p.company.length>100 ||
            !allowedInstruments.has(p.instrument) || !allowedCoverage.has(p.quote_kind) ||
            !allowedStates.has(p.state))) return null;
      return value;
    } catch (_) { return null; }
  }
  const snapshot=readSnapshot();
  const providers=snapshot ? snapshot.providers.map(p=>Object.assign({},p)) : FALLBACK;
  let currentFilter="all", lastFocused=null;

  function statusText(state) {
    const labels={NOT_CONFIGURED:"Not configured",REFERENCE_ONLY:"Reference only",
      SOURCE_ONLY_READY:"Mapping ready · not live",RIGHTS_HOLD:"Rights HOLD",
      OWNER_APPROVAL:"Owner review",OBSERVING:"Process approved · health unverified",
      HOLD:"HOLD",REVOKED:"Revoked"};
    return labels[state] || state.replaceAll("_"," ").toLowerCase();
  }
  function badge(state) {
    const b=document.createElement("span");
    b.className="mdd-badge" + (state==="SOURCE_ONLY_READY"?" ready": /HOLD|REVOKED/.test(state)?" hold":"");
    b.textContent=statusText(state);
    return b;
  }
  function group(p) {return p.instrument==="event"||p.instrument==="metadata"?"reference":p.instrument;}
  function description(p) {
    if(typeof p.description==="string") return p.description;
    const fromCatalog=FALLBACK.find(x=>x.product_key===p.product_key);
    return fromCatalog ? fromCatalog.description : "Exact coverage and rights require source review.";
  }
  function openDetail(p, opener) {
    lastFocused=opener;
    write("mddDrawerTitle",p.company+" · "+p.product_key);
    write("mddDrawerDescription",description(p));
    write("mddDetailLane",group(p)==="reference"?"Research / metadata":p.instrument==="equity"?"Equity":"Options");
    write("mddDetailCoverage",p.quote_kind.replaceAll("_"," "));
    write("mddDetailState",statusText(p.state)+(snapshot?" (protected source-only snapshot)":" (catalog preview only)"));
    write("mddDetailNext",NEXT[p.state]||"Revalidate rights and the exact feed.");
    $("mddBackdrop").hidden=false;
    $("mddDrawer").hidden=false;
    $("mddDrawer").setAttribute("aria-hidden","false");
    document.body.style.overflow="hidden";
    $("mddClose").focus();
  }
  function closeDetail() {
    $("mddBackdrop").hidden=true;$("mddDrawer").hidden=true;
    $("mddDrawer").setAttribute("aria-hidden","true");
    document.body.style.overflow="";
    if(lastFocused && lastFocused.isConnected)lastFocused.focus();
  }
  function renderProviders() {
    const root=$("mddProviderGrid");root.replaceChildren();
    const visible=providers.filter(p=>currentFilter==="all"||group(p)===currentFilter);
    if(!visible.length) {const empty=document.createElement("p");empty.className="mdd-empty";empty.textContent="No products in this lane.";root.appendChild(empty);return;}
    visible.forEach(p=>{
      const card=document.createElement("article");card.className="mdd-provider-card";
      const top=document.createElement("div");top.className="mdd-card-top";
      const h=document.createElement("h3");h.textContent=p.company;
      top.append(h,badge(p.state));card.appendChild(top);
      const lane=document.createElement("span");lane.className="mdd-card-lane";lane.textContent=p.instrument+" · "+p.quote_kind.replaceAll("_"," ");card.appendChild(lane);
      const summary=document.createElement("p");summary.textContent=description(p);card.appendChild(summary);
      const button=document.createElement("button");button.type="button";button.textContent="Inspect source & next proof →";
      button.setAttribute("aria-label","Inspect "+p.company+" "+p.product_key);
      button.addEventListener("click",()=>openDetail(p,button));card.appendChild(button);root.appendChild(card);
    });
  }
  function renderCases() {
    const root=$("mddCases");root.replaceChildren();
    if(!snapshot || snapshot.cases.length===0) {
      const p=document.createElement("p");p.className="mdd-empty";
      p.textContent=snapshot?"No reviewed onboarding cases in this source-only snapshot.":"No protected onboarding cases attached. There is no browser approval shortcut.";
      root.appendChild(p);return;
    }
    snapshot.cases.forEach(c=>{
      if(!c || typeof c.case_id!=="string" || typeof c.product_key!=="string" ||
         !allowedStates.has(c.state))return;
      const card=document.createElement("div");card.className="mdd-case";
      const left=document.createElement("div");const title=document.createElement("strong");title.textContent=c.product_key;
      const note=document.createElement("small");note.textContent=typeof c.reason==="string"&&c.reason?c.reason:NEXT[c.state];
      left.append(title,note);card.append(left,badge(c.state));root.appendChild(card);
    });
  }
  function renderSnapshot() {
    if(!snapshot) {
      write("mddTruth","Catalog preview · live status unavailable");
      write("mddAsOf","Tower has not attached a protected provider-status projection.");
      write("mddProducts",String(providers.length));
      write("mddSoulaanaHeadline","We have a place for every planned source. No real connection is claimed.");
      write("mddSoulaanaMeaning","Directory and filing sources help discovery; they do not supply current quotes.");
      write("mddSoulaanaNext","Review product rights and map the exact protected read-only backend.");
      renderCases();renderProviders();return;
    }
    write("mddTruth", "Protected source-only catalog · runtime health unverified");
    write("mddAsOf","Snapshot as of "+String(snapshot.as_of||"timestamp unavailable"));
    write("mddProducts",String(snapshot.summary.catalog_products??"—"));
    write("mddLive",snapshot.runtime_health_attached&&Number.isSafeInteger(snapshot.summary.live_feeds_verified)?String(snapshot.summary.live_feeds_verified):"—");
    write("mddAttention",Number.isSafeInteger(snapshot.summary.actions_needing_review)?String(snapshot.summary.actions_needing_review):"—");
    write("mddTraffic","—");
    write("mddSoulaanaHeadline",String(snapshot.soulaana?.headline||"No Soulaana source conclusion.") .slice(0,300));
    write("mddSoulaanaMeaning",String(snapshot.soulaana?.meaning||"Connection evidence still needed.").slice(0,400));
    write("mddSoulaanaNext",String(snapshot.soulaana?.next_step||"Review the exact source rights.").slice(0,400));
    renderCases();renderProviders();
  }
  $("mddClose").addEventListener("click",closeDetail);
  $("mddBackdrop").addEventListener("click",closeDetail);
  document.addEventListener("keydown",e=>{
    if($("mddDrawer").hidden)return;
    if(e.key==="Escape"){e.preventDefault();closeDetail();return;}
    if(e.key==="Tab") {
      // Only the close button is interactive inside the read-only drawer.
      e.preventDefault();$("mddClose").focus();
    }
  });
  document.querySelectorAll("[data-mdd-filter]").forEach(button=>{
    button.addEventListener("click",()=>{
      currentFilter=button.dataset.mddFilter;
      document.querySelectorAll("[data-mdd-filter]").forEach(b=>{
        const selected=b===button;b.classList.toggle("is-active",selected);b.setAttribute("aria-pressed",String(selected));
      });
      renderProviders();
    });
  });
  renderSnapshot();
})();
