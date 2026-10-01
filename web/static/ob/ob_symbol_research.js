(function () {
  "use strict";

  const CATALYST_SOURCES = ["federal_register", "cftc", "eia", "world_bank", "nws"];

  function byId(id) { return document.getElementById(id); }
  function symbol() {
    const room = byId("obSymbolRoom");
    return String((room && room.dataset.symbol) || document.body.dataset.obSymbol || "").trim().toUpperCase();
  }
  function set(id, value, fallback) {
    const node = byId(id);
    if (node) node.textContent = value == null || value === "" ? (fallback || "—") : String(value);
  }
  function fmt(value, digits) {
    const n = Number(value);
    return Number.isFinite(n) ? n.toLocaleString(undefined, { maximumFractionDigits: digits == null ? 2 : digits }) : "—";
  }
  function pct(value) {
    const n = Number(value);
    if (!Number.isFinite(n)) return "—";
    return (n > 0 ? "+" : "") + n.toFixed(2) + "%";
  }
  function money(value) {
    const n = Number(value);
    return Number.isFinite(n) ? n.toLocaleString(undefined, {style:"currency", currency:"USD", maximumFractionDigits:2}) : "—";
  }
  function paragraph(value, cls) {
    const p = document.createElement("p");
    if (cls) p.className = cls;
    p.textContent = String(value || "");
    return p;
  }
  function sourceRow(rows, id, field) {
    const key = field || "provider";
    return Array.isArray(rows) ? rows.find(row => row && row[key] === id) || null : null;
  }
  async function json(path) {
    const response = await fetch(path, {
      credentials: "same-origin", cache: "no-store",
      headers: {"Accept":"application/json"}
    });
    if (!response.ok) throw new Error(path + " " + response.status);
    return response.json();
  }


  function serverResearch() {
    const node = byId("symbolServerResearch");
    if (!node) return null;
    try { return JSON.parse(node.textContent || "null"); }
    catch (_) { return null; }
  }

  function direction(latest, prior) {
    const a = Number(latest), b = Number(prior);
    if (!Number.isFinite(a) || !Number.isFinite(b)) return null;
    return a > b ? "up" : a < b ? "down" : "flat";
  }

  function addFinding(list, tone, text, source) {
    if (!text) return;
    list.push({tone, text, source});
  }

  function sectorSensitivity(industry) {
    const s = String(industry || "").toLowerCase();
    return {
      rateSensitive: /(software|technology|semiconductor|internet|communication|real estate|utilities|consumer durable|biotechnology)/.test(s),
      energySensitive: /(energy|oil|gas|petroleum|airline|transport)/.test(s),
      cyclical: /(industrial|manufactur|consumer cyclic|retail|automotive|materials|bank|financial)/.test(s),
    };
  }

  function renderList(id, findings, empty) {
    const mount = byId(id);
    if (!mount) return;
    mount.replaceChildren();
    const rows = findings.slice(0, 6);
    if (!rows.length) {
      mount.append(paragraph(empty, "ob-symbol-research-muted"));
      return;
    }
    rows.forEach(item => {
      const p = paragraph(item.text);
      p.className = "ob-symbol-impact-item ob-symbol-impact-item--" + item.tone;
      if (item.source) {
        const small = document.createElement("small");
        small.textContent = item.source;
        p.append(document.createElement("br"), small);
      }
      mount.append(p);
    });
  }


  function sourceStateLabel(state) {
    return String(state || "UNAVAILABLE").replaceAll("_", " ").toLowerCase();
  }

  function renderSourceAccounting(providerPacket, keylessPacket, catalystPacket, secPacket) {
    const rows = [];
    const providers = providerPacket && Array.isArray(providerPacket.provider_research)
      ? providerPacket.provider_research : [];
    ["finnhub","alpha_vantage","finazon","alpaca","public","public_options","bea"].forEach(name => {
      const item = sourceRow(providers, name);
      rows.push({
        name,
        state: item ? sourceStateLabel(item.state) : "not returned",
        disposition: item && item.state === "SOURCE_BOUND"
          ? (item.soulaana_ai_use_reviewed === true
              ? "visible + actually readable by Soulaana"
              : "visible to owner, but Soulaana AI-use review is OFF")
          : (item && item.state === "RIGHTS_OR_FETCH_HOLD"
              ? "connected credential may exist, but owner-display/fetch review is OFF"
              : "not used in this read")
      });
    });

    const publics = keylessPacket && Array.isArray(keylessPacket.sources) ? keylessPacket.sources : [];
    ["bls","treasury","openfigi"].forEach(name => {
      const item = sourceRow(publics, name, "source");
      rows.push({
        name,
        state: item ? sourceStateLabel(item.state) : "not returned",
        disposition: item && item.state === "SOURCE_BOUND"
          ? (name === "openfigi"
              ? "visible identity evidence; Soulaana accounts for the mapping without treating it as company fundamentals or a quote"
              : "visible + macro evidence used by Soulaana when reviewed")
          : "not used in this read"
      });
    });

    const catalysts = catalystPacket && Array.isArray(catalystPacket.sources) ? catalystPacket.sources : [];
    ["federal_register","cftc","eia","world_bank","nws"].forEach(name => {
      const item = sourceRow(catalysts, name, "source");
      rows.push({
        name,
        state: item ? sourceStateLabel(item.state) : "not returned",
        disposition: item && item.state === "SOURCE_BOUND"
          ? "visible catalyst evidence; Soulaana applies it only when it is relevant enough to this symbol"
          : "not used in this read"
      });
    });

    rows.push({
      name:"sec_edgar",
      state: secPacket ? sourceStateLabel(secPacket.state || (secPacket.fundamentals && secPacket.fundamentals.state)) : "not attached",
      disposition: secPacket
        ? "issuer-specific filing evidence available to the Symbol read"
        : "server-side issuer packet not attached"
    });

    const mount = byId("symbolSourceAccounting");
    if (!mount) return;
    mount.replaceChildren();
    rows.forEach(item => {
      const p = paragraph(
        item.name.toUpperCase() + " · " + item.state + " · " + item.disposition,
        "ob-symbol-source-accounting-row"
      );
      mount.append(p);
    });
  }

  function buildImpact(providerPacket, keylessPacket, catalystPacket, secPacket, ticker, governmentDossier) {
    const positive = [], negative = [], agreement = [], conflict = [], watch = [];
    const why = [];
    const providerRows = providerPacket && Array.isArray(providerPacket.provider_research)
      ? providerPacket.provider_research : [];
    const alpaca = sourceRow(providerRows, "alpaca");
    const finazon = sourceRow(providerRows, "finazon");
    const publicQuote = sourceRow(providerRows, "public");
    const publicOptions = sourceRow(providerRows, "public_options");
    const finnhub = sourceRow(providerRows, "finnhub");
    const alpha = sourceRow(providerRows, "alpha_vantage");
    const bea = sourceRow(providerRows, "bea");

    const alphaProfile = alpha && alpha.company_profile && typeof alpha.company_profile === "object"
      ? alpha.company_profile : null;
    const industry = (finnhub && finnhub.industry) ||
      (alphaProfile && (alphaProfile.industry || alphaProfile.sector));
    const sensitivity = sectorSensitivity(industry);
    if (industry) why.push(ticker + " is classified by the connected company-profile sources in " + industry + ".");
    if (sensitivity.rateSensitive) why.push("That industry can be sensitive to discount-rate changes, so Treasury yield direction belongs in this symbol read.");
    if (sensitivity.energySensitive) why.push("That industry has direct sensitivity to energy conditions, so EIA context is more relevant than it would be for many other symbols.");
    if (sensitivity.cyclical) why.push("That industry is economically cyclical, so growth and labor direction matter to the backdrop.");

    if (alpha && alpha.state === "SOURCE_BOUND" && Array.isArray(alpha.bars) && alpha.bars.length >= 2) {
      const d = direction(alpha.bars[0].close, alpha.bars[1].close);
      if (d === "up") addFinding(positive, "positive", "The latest completed daily close is above the prior completed session.", "Alpha Vantage");
      if (d === "down") addFinding(negative, "negative", "The latest completed daily close is below the prior completed session.", "Alpha Vantage");
      addFinding(watch, "neutral", "Watch whether the next completed session confirms or reverses the latest daily-price direction.", "Alpha Vantage");
    }

    if (alpaca && alpaca.state === "SOURCE_BOUND") {
      const q = alpaca.quote || {}, b = alpaca.bar || {};
      if (Number.isFinite(Number(q.midpoint)) && Number.isFinite(Number(b.close))) {
        const d = direction(q.midpoint, b.close);
        if (d === "up") addFinding(positive, "positive", "Current IEX midpoint is above the latest minute close, a small near-term firming signal in venue-limited data.", "Alpaca IEX");
        if (d === "down") addFinding(negative, "negative", "Current IEX midpoint is below the latest minute close, a small near-term softening signal in venue-limited data.", "Alpaca IEX");
      }
    }

    if (publicQuote && publicQuote.state === "SOURCE_BOUND") {
      const pb = Number(publicQuote.bid), pa = Number(publicQuote.ask);
      if (Number.isFinite(pb) && Number.isFinite(pa) && pa >= pb) {
        const pm = (pb + pa) / 2;
        addFinding(watch, "neutral", "Public personal API is contributing current owner-only quote context around " + pm.toFixed(2) + ".", "Public");
        if (alpaca && alpaca.state === "SOURCE_BOUND" && alpaca.quote && Number.isFinite(Number(alpaca.quote.midpoint))) {
          const am = Number(alpaca.quote.midpoint);
          const diffPct = am > 0 ? Math.abs(pm - am) / am * 100 : null;
          if (Number.isFinite(diffPct) && diffPct <= 0.5) {
            addFinding(agreement, "agree", "Public and Alpaca IEX are broadly aligned on current price context.", "Public + Alpaca");
          } else if (Number.isFinite(diffPct) && diffPct > 0.5) {
            addFinding(conflict, "conflict", "Public and Alpaca IEX are materially apart right now, so Soulaana should treat current-price context cautiously.", "Public + Alpaca");
          }
        }
      }
    }

    if (publicOptions && publicOptions.state === "SOURCE_BOUND") {
      const count = Number(publicOptions.contract_count || 0);
      const expiry = publicOptions.expiration || "the nearest available expiration";
      addFinding(
        watch,
        "neutral",
        "Public options data is loaded for " + expiry + " with " + count +
          " bounded near-the-money contracts. Soulaana can use the real spreads, volume, open interest, IV and Greeks instead of guessing from the stock alone.",
        "Public Options"
      );
    }

    if (!(alpaca && alpaca.state === "SOURCE_BOUND") && finazon && finazon.state === "SOURCE_BOUND") {
      const ch = Number(finazon.daily_change_percent);
      if (Number.isFinite(ch) && ch > 0) addFinding(positive, "positive", "The connected current-market source shows a positive daily move.", "Finazon");
      if (Number.isFinite(ch) && ch < 0) addFinding(negative, "negative", "The connected current-market source shows a negative daily move.", "Finazon");
    }

    const publicRows = keylessPacket && Array.isArray(keylessPacket.sources) ? keylessPacket.sources : [];
    const bls = sourceRow(publicRows, "bls", "source");
    const treasury = sourceRow(publicRows, "treasury", "source");
    const openfigi = sourceRow(publicRows, "openfigi", "source");

    let inflationDir = null, laborDir = null, yieldDir = null;
    if (bls && bls.state === "SOURCE_BOUND" && Array.isArray(bls.series)) {
      const cpi = bls.series.find(x => x.series_id === "CUUR0000SA0");
      const ppi = bls.series.find(x => x.series_id === "WPUFD4");
      const jobs = bls.series.find(x => x.series_id === "CES0000000001");
      const unemp = bls.series.find(x => x.series_id === "LNS14000000");
      const cpiD = cpi && direction(cpi.value, cpi.previous_value);
      const ppiD = ppi && direction(ppi.value, ppi.previous_value);
      if (cpiD && cpiD === ppiD) inflationDir = cpiD;
      const jobsD = jobs && direction(jobs.value, jobs.previous_value);
      const unempD = unemp && direction(unemp.value, unemp.previous_value);
      if (jobsD === "up" && unempD !== "up") laborDir = "stronger";
      else if (jobsD === "down" && unempD === "up") laborDir = "weaker";
      else laborDir = "mixed";

      if (inflationDir === "down") addFinding(positive, "positive", "Consumer and producer price measures are both cooling across their latest source periods, reducing one macro pressure point.", "BLS");
      if (inflationDir === "up") addFinding(negative, "negative", "Consumer and producer price measures are both rising across their latest source periods, keeping inflation pressure in the backdrop.", "BLS");
      if (laborDir === "stronger") addFinding(positive, "positive", "Labor data are broadly firmer, which supports demand but can also keep rate pressure alive.", "BLS");
      if (laborDir === "weaker") addFinding(negative, "negative", "Labor data are broadly weakening, which can pressure cyclical demand expectations.", "BLS");
      if (laborDir === "mixed") addFinding(conflict, "conflict", "Labor measures are not telling one clean story, so Soulaana should not force a single macro label.", "BLS");
    }

    if (openfigi && openfigi.state === "SOURCE_BOUND" && openfigi.value) {
      addFinding(agreement, "agree", "The ticker has a reviewed OpenFIGI reference mapping, which strengthens identifier consistency but does not prove issuer fundamentals.", "OpenFIGI");
    }

    if (treasury && treasury.state === "SOURCE_BOUND" && treasury.rates && treasury.rates.state === "SOURCE_BOUND") {
      const d = treasury.rates.derived || {};
      const tenChange = Number(d.ten_year_change_bp);
      if (Number.isFinite(tenChange)) {
        yieldDir = tenChange > 0 ? "up" : tenChange < 0 ? "down" : "flat";
        if (sensitivity.rateSensitive && tenChange < 0) addFinding(positive, "positive", "The latest 10-year Treasury move is lower, which eases one valuation headwind for rate-sensitive businesses.", "U.S. Treasury");
        if (sensitivity.rateSensitive && tenChange > 0) addFinding(negative, "negative", "The latest 10-year Treasury move is higher, which raises one valuation headwind for rate-sensitive businesses.", "U.S. Treasury");
      }
      if (d.curve_change) addFinding(watch, "neutral", "Watch whether the Treasury curve keeps " + String(d.curve_change).replaceAll("_"," ").toLowerCase() + " at the next official close.", "U.S. Treasury");
    }

    if (bea && bea.state === "SOURCE_BOUND" && Array.isArray(bea.macro_series)) {
      const growth = bea.macro_series.find(x => x.series_id === "real_gdp_growth");
      const obs = growth && growth.observations;
      if (Array.isArray(obs) && obs.length >= 2) {
        const d = direction(obs[0].value, obs[1].value);
        if (d === "up" && sensitivity.cyclical) addFinding(positive, "positive", "Real GDP growth accelerated in the latest BEA comparison, a supportive cyclical backdrop.", "BEA");
        if (d === "down" && sensitivity.cyclical) addFinding(negative, "negative", "Real GDP growth slowed in the latest BEA comparison, a softer cyclical backdrop.", "BEA");
      }
    }

    const cats = catalystPacket && Array.isArray(catalystPacket.sources) ? catalystPacket.sources : [];
    const eia = sourceRow(cats, "eia", "source");
    const fedreg = sourceRow(cats, "federal_register", "source");
    const cftc = sourceRow(cats, "cftc", "source");
    const worldBank = sourceRow(cats, "world_bank", "source");
    const nws = sourceRow(cats, "nws", "source");
    if (eia && eia.state === "SOURCE_BOUND" && sensitivity.energySensitive) {
      addFinding(watch, "neutral", "Energy inventory data are live in the context stack; the direction matters more for this industry than for the average symbol.", "EIA");
    }
    if (fedreg && fedreg.state === "SOURCE_BOUND" && Array.isArray(fedreg.facts) && fedreg.facts.length) {
      addFinding(watch, "neutral", "Recent SEC-related Federal Register activity is present. It is policy context, not proof that this issuer is directly affected.", "Federal Register");
    }
    if (cftc && cftc.state === "SOURCE_BOUND") {
      addFinding(watch, "neutral", "Futures positioning context is available, but it is not issuer-specific and should be treated as backdrop only.", "CFTC");
    }
    if (worldBank && worldBank.state === "SOURCE_BOUND") {
      addFinding(watch, "neutral", "World Bank annual U.S. GDP context is available as a long-horizon backdrop. It is too slow-moving to explain a current symbol move by itself.", "World Bank");
    }
    if (nws && nws.state === "SOURCE_BOUND") {
      addFinding(watch, "neutral", "NWS alert context is available. Soulaana keeps it as environmental context unless a direct geographic/operational link to this issuer is established.", "NWS");
    }

    const sec = secPacket && secPacket.room === "symbol_page" ? secPacket : null;
    if (sec) {
      const events = Array.isArray(sec.issuer_events) ? sec.issuer_events : [];
      const fundamentals = sec.fundamentals || {};
      if (events.length) addFinding(watch, "neutral", events.length + " recent cited issuer event(s) are attached to this symbol and deserve direct review.", "SEC EDGAR");
      if (fundamentals.state === "SOURCE_BOUND") {
        addFinding(agreement, "agree", "Issuer filing facts are source-bound and can be checked against the market/macro story instead of relying on price alone.", "SEC EDGAR");
      }
    }

    if (inflationDir === "down" && yieldDir === "down") addFinding(agreement, "agree", "Cooling price measures and lower long yields are directionally consistent with easing rate pressure.", "BLS + Treasury");
    if (inflationDir === "up" && yieldDir === "up") addFinding(agreement, "agree", "Rising price measures and higher long yields are directionally consistent with persistent rate pressure.", "BLS + Treasury");
    if (inflationDir === "down" && yieldDir === "up") addFinding(conflict, "conflict", "Price measures are cooling while long yields moved higher. Those signals do not support one simple macro story.", "BLS + Treasury");
    if (inflationDir === "up" && yieldDir === "down") addFinding(conflict, "conflict", "Price measures are rising while long yields moved lower. The macro evidence is pulling in different directions.", "BLS + Treasury");

    const support = positive.length, pressure = negative.length;
    let headline = "Mixed evidence · keep investigating";
    if (support >= pressure + 2) headline = "Evidence is leaning supportive, with caveats";
    else if (pressure >= support + 2) headline = "Evidence is leaning pressured, with caveats";
    else if (support && pressure) headline = "Support and pressure are both present";
    else if (support) headline = "Some supportive evidence is present";
    else if (pressure) headline = "Some pressure is present";

    const summary = support + " supportive factor" + (support === 1 ? "" : "s") +
      ", " + pressure + " pressure factor" + (pressure === 1 ? "" : "s") +
      ", " + conflict.length + " conflict" + (conflict.length === 1 ? "" : "s") +
      ". This is a research synthesis, not a trade recommendation.";

    if (!why.length) why.push("The connected evidence does not yet establish enough company/industry sensitivity to say which macro lanes matter most.");
    addFinding(watch, "neutral", "Re-check the current quote, the next completed session, any new SEC filing/event, and the next major macro/rates update before treating the read as stable.", "Soulaana");

    set("symbolImpactHeadline", headline);
    set("symbolImpactSummary", summary);
    set("symbolImpactWhy", why.join(" "));
    renderList("symbolImpactTailwinds", positive, "No clear source-backed tailwind is established yet.");
    renderList("symbolImpactHeadwinds", negative, "No clear source-backed headwind is established yet.");
    renderList("symbolImpactAgreement", agreement, "Independent evidence has not formed a strong agreement cluster yet.");
    renderList("symbolImpactConflict", conflict, "No material cross-source conflict is visible yet.");
    renderList("symbolImpactWatch", watch, "No additional evidence checkpoint is available yet.");

    const providerSoulaana = providerPacket && providerPacket.soulaana_research;
    const providerObservations = providerSoulaana && Array.isArray(providerSoulaana.observations)
      ? providerSoulaana.observations : [];
    const readableProviders = providerRows.filter(x => x && x.state === "SOURCE_BOUND" && x.soulaana_ai_use_reviewed === true);
    const heldForSoulaana = providerRows.filter(x => x && x.state === "SOURCE_BOUND" && x.soulaana_ai_use_reviewed !== true);

    const translated = providerObservations
      .map(x => x && x.finding)
      .filter(Boolean);
    const meanings = providerObservations
      .map(x => x && x.why_it_matters)
      .filter(Boolean);

    const soulaanaSees = byId("symbolSoulaanaSees");
    const soulaanaMeans = byId("symbolSoulaanaMeans");
    const soulaanaCaution = byId("symbolSoulaanaCaution");
    const soulaanaNext = byId("symbolSoulaanaNext");

    const governmentSee = governmentDossier && governmentDossier.official_summary
      ? governmentDossier.official_summary : "";
    const governmentMeaning = governmentDossier && governmentDossier.relevance_summary
      ? governmentDossier.relevance_summary : "";

    if (soulaanaSees) {
      const parts = [];
      if (governmentSee) parts.push(governmentSee);
      if (translated.length) parts.push(translated.slice(0, 2).join(" "));
      else parts.push(headline + ". " + summary);
      soulaanaSees.textContent = parts.join(" ");
    }
    if (soulaanaMeans) {
      const parts = [];
      if (governmentMeaning) parts.push(governmentMeaning);
      if (meanings.length) parts.push(meanings.slice(0, 2).join(" "));
      else if (why.length) parts.push(why.join(" "));
      soulaanaMeans.textContent = parts.join(" ");
    }
    if (soulaanaCaution) {
      if (heldForSoulaana.length) {
        soulaanaCaution.textContent =
          heldForSoulaana.map(x => String(x.provider).toUpperCase()).join(", ") +
          " returned owner-visible data but is not currently cleared for Soulaana AI-use. " +
          (conflict.length ? conflict[0].text : "I will not pretend I interpreted content I was not cleared to read.");
      } else {
        soulaanaCaution.textContent = conflict.length
          ? conflict[0].text + " I am keeping that disagreement visible instead of smoothing it over."
          : "Evidence can agree and still be incomplete. Missing current options/liquidity or issuer-specific evidence stays missing.";
      }
    }
    if (soulaanaNext) {
      const missing = providerObservations
        .map(x => x && x.what_is_missing)
        .filter(Boolean);
      soulaanaNext.textContent = missing.length
        ? missing[0]
        : (watch.length ? watch[0].text : "Wait for the next source-backed update.");
    }

    if (readableProviders.length && !translated.length) {
      addFinding(conflict, "conflict",
        "Provider rows are marked readable by Soulaana, but the provider-research translation packet returned no observation. That is a wiring defect, not a clean research state.",
        "Soulaana diagnostics");
    }
  }


  function card(label, value, note) {
    const item = document.createElement("div");
    item.className = "ob-symbol-metric";
    const l = document.createElement("span");
    l.textContent = label;
    const v = document.createElement("strong");
    v.textContent = value == null || value === "" ? "—" : String(value);
    item.append(l, v);
    if (note) {
      const n = document.createElement("small");
      n.textContent = note;
      item.append(n);
    }
    return item;
  }

  function fact(label, value) {
    const item = document.createElement("div");
    const l = document.createElement("span");
    l.textContent = label;
    const v = document.createElement("strong");
    v.textContent = value == null || value === "" ? "—" : String(value);
    item.append(l, v);
    return item;
  }


  function governmentCompanyDossier(providerPacket, keylessPacket, catalystPacket, secPacket, ticker, settings) {
    const providerRows = providerPacket && Array.isArray(providerPacket.provider_research)
      ? providerPacket.provider_research : [];
    const finnhub = sourceRow(providerRows, "finnhub");
    const alpha = sourceRow(providerRows, "alpha_vantage");
    const alphaProfile = alpha && alpha.state === "SOURCE_BOUND" && alpha.company_profile &&
      typeof alpha.company_profile === "object" ? alpha.company_profile : null;
    const industry = (finnhub && finnhub.industry) ||
      (alphaProfile && (alphaProfile.industry || alphaProfile.sector));
    const sensitivity = sectorSensitivity(industry);

    const identity = secPacket && secPacket.identity && typeof secPacket.identity === "object"
      ? secPacket.identity : null;
    const fundamentals = secPacket && secPacket.fundamentals && typeof secPacket.fundamentals === "object"
      ? secPacket.fundamentals : null;
    const events = secPacket && Array.isArray(secPacket.issuer_events) ? secPacket.issuer_events : [];
    const secExam = secPacket && secPacket.soulaana_sec_examination &&
      typeof secPacket.soulaana_sec_examination === "object"
      ? secPacket.soulaana_sec_examination : null;

    const publicRows = keylessPacket && Array.isArray(keylessPacket.sources)
      ? keylessPacket.sources : [];
    const bls = sourceRow(publicRows, "bls", "source");
    const treasury = sourceRow(publicRows, "treasury", "source");

    const providerBea = sourceRow(providerRows, "bea");
    const catalysts = catalystPacket && Array.isArray(catalystPacket.sources)
      ? catalystPacket.sources : [];
    const federalRegister = sourceRow(catalysts, "federal_register", "source");
    const eia = sourceRow(catalysts, "eia", "source");

    const officialBits = [];
    const dossierFacts = [];
    if (identity) {
      if (identity.security_name) officialBits.push("SEC identifies " + ticker + " as " + identity.security_name);
      if (identity.cik) dossierFacts.push(fact("SEC CIK", identity.cik));
      if (identity.exchange_code) dossierFacts.push(fact("SEC exchange", identity.exchange_code));
      if (identity.identity_status) dossierFacts.push(fact("SEC identity", String(identity.identity_status).replaceAll("_", " ")));
    }
    if (fundamentals && fundamentals.state === "SOURCE_BOUND") {
      const concepts = Array.isArray(fundamentals.reported_concepts) ? fundamentals.reported_concepts : [];
      dossierFacts.push(fact("SEC filing facts", String(concepts.length) + " attached"));
      officialBits.push(concepts.length + " source-bound SEC financial fact" + (concepts.length === 1 ? "" : "s") + " attached");
    }
    if (events.length) {
      dossierFacts.push(fact("Recent SEC events", String(events.length)));
      const latest = events[0];
      if (latest && latest.accepted_at) dossierFacts.push(fact("Latest SEC event", latest.accepted_at));
      officialBits.push(events.length + " recent cited SEC filing/event" + (events.length === 1 ? "" : "s") + " attached");
    }
    if (secExam && secExam.state === "SOURCE_BOUND" && Array.isArray(secExam.findings)) {
      dossierFacts.push(fact("Soulaana-reviewed SEC facts", String(secExam.findings.length)));
    }

    const relevant = [];
    if (sensitivity.rateSensitive) {
      relevant.push(treasury && treasury.state === "SOURCE_BOUND"
        ? "Treasury rates are live and relevant because this business is rate-sensitive."
        : "Treasury rates matter to this business, but the current official rate context is not source-bound.");
    }
    if (sensitivity.cyclical) {
      const pieces = [];
      if (bls && bls.state === "SOURCE_BOUND") pieces.push("BLS");
      if (providerBea && providerBea.state === "SOURCE_BOUND") pieces.push("BEA");
      relevant.push(
        pieces.length
          ? pieces.join(" + ") + " are active because this business is economically cyclical."
          : "BLS/BEA growth and labor context matter to this cyclical business, but they are not currently source-bound."
      );
    }
    if (sensitivity.energySensitive) {
      relevant.push(
        eia && eia.state === "SOURCE_BOUND"
          ? "EIA energy inventory context is active because this industry has direct energy sensitivity."
          : "EIA energy data would matter here, but the current EIA lane is not source-bound."
      );
    }
    if (federalRegister && federalRegister.state === "SOURCE_BOUND") {
      relevant.push("Federal Register SEC-related activity is available as regulatory backdrop; it is not treated as proof that this issuer is directly affected.");
    }
    if (!relevant.length) {
      relevant.push("The current company classification does not justify forcing a special Treasury, BLS/BEA, or EIA sensitivity label.");
    }

    const summary = officialBits.length
      ? officialBits.join(". ") + "."
      : "SEC issuer evidence is not attached to this Symbol read, so OB will not invent an official issuer dossier.";

    set("symbolGovernmentCompanySummary", summary);
    set("symbolGovernmentRelevance", relevant.join(" "));
    const mount = byId("symbolGovernmentCompanyFacts");
    if (mount) {
      if (dossierFacts.length) mount.replaceChildren(...dossierFacts.slice(0, 10));
      else mount.replaceChildren();
    }

    return {
      official_summary: summary,
      relevance_summary: relevant.join(" "),
      sec_identity_attached: !!identity,
      sec_fundamentals_attached: !!(fundamentals && fundamentals.state === "SOURCE_BOUND"),
      sec_events_attached: events.length,
      treasury_relevant: sensitivity.rateSensitive,
      cyclical_government_context_relevant: sensitivity.cyclical,
      energy_government_context_relevant: sensitivity.energySensitive,
      federal_register_available: !!(federalRegister && federalRegister.state === "SOURCE_BOUND"),
    };
  }

  function hydrateTopSymbolFacts(packet, ticker, settings) {
    if (!packet || packet.schema !== "OB_KEYED_PROVIDER_RESEARCH_V1") return;
    const rows = Array.isArray(packet.provider_research) ? packet.provider_research : [];
    const alpaca = sourceRow(rows, "alpaca");
    const finnhub = sourceRow(rows, "finnhub");
    const alpha = sourceRow(rows, "alpha_vantage");
    const finazon = sourceRow(rows, "finazon");
    const profile = alpha && alpha.state === "SOURCE_BOUND" && alpha.company_profile &&
      typeof alpha.company_profile === "object" ? alpha.company_profile : null;

    if (profile) {
      if (profile.name) set("symbolCompany", profile.name);
      const sectorLabel = [profile.sector, profile.industry].filter(Boolean).join(" · ");
      if (sectorLabel) set("symbolSector", sectorLabel);
      const heroState = [profile.exchange, profile.country, profile.currency].filter(Boolean).join(" · ");
      if (heroState) set("symbolMarketState", heroState);

      const cardNode = byId("symbolCompanyProfileCard");
      if (cardNode) cardNode.hidden = settings && settings.show_company_background === false;
      set("symbolCompanyProfileName", profile.name || ticker);
      set("symbolCompanyDescription", profile.description || "No reviewed business description was returned.");
      set("symbolCompanyProfileTrust", "Alpha Overview · owner-only research");

      const profileFacts = byId("symbolCompanyProfileFacts");
      if (profileFacts) {
        const profileItems = [];
        if (profile.asset_type) profileItems.push(fact("Asset type", profile.asset_type));
        if (profile.sector) profileItems.push(fact("Sector", profile.sector));
        if (profile.industry) profileItems.push(fact("Industry", profile.industry));
        if (profile.exchange) profileItems.push(fact("Exchange", profile.exchange));
        if (profile.country) profileItems.push(fact("Country", profile.country));
        if (profile.address) profileItems.push(fact("Address", profile.address));
        if (profile.fiscal_year_end) profileItems.push(fact("Fiscal year end", profile.fiscal_year_end));
        if (profile.latest_quarter) profileItems.push(fact("Latest reported quarter", profile.latest_quarter));
        if (profile.market_cap != null) profileItems.push(fact("Market cap", money(profile.market_cap)));
        if (profile.shares_outstanding != null) profileItems.push(fact("Shares outstanding", fmt(profile.shares_outstanding, 0)));
        if (profile.revenue_ttm != null) profileItems.push(fact("Revenue TTM", money(profile.revenue_ttm)));
        if (profile.eps != null) profileItems.push(fact("EPS", fmt(profile.eps, 2)));
        if (profile.pe_ratio != null) profileItems.push(fact("P/E", fmt(profile.pe_ratio, 2)));
        if (profile.profit_margin != null) profileItems.push(fact("Profit margin", pct(Number(profile.profit_margin) * 100)));
        if (profile.beta != null) profileItems.push(fact("Beta", fmt(profile.beta, 2)));
        if (profileItems.length) profileFacts.replaceChildren(...profileItems.slice(0, 14));
      }
    } else if (finnhub && finnhub.state === "SOURCE_BOUND") {
      if (finnhub.security_name) set("symbolCompany", finnhub.security_name);
      if (finnhub.industry) set("symbolSector", finnhub.industry);
      const heroState = [finnhub.exchange, finnhub.country, finnhub.currency].filter(Boolean).join(" · ");
      if (heroState) set("symbolMarketState", heroState);
    }

    const metrics = byId("symbolUnderlyingMetrics");
    if (metrics) {
      const items = [];
      if (alpaca && alpaca.state === "SOURCE_BOUND") {
        const q = alpaca.quote || {}, b = alpaca.bar || {};
        if (q.midpoint != null) items.push(card("Current midpoint", money(q.midpoint), "Alpaca IEX"));
        if (q.bid != null || q.ask != null) items.push(card("Bid / Ask", fmt(q.bid) + " / " + fmt(q.ask), "Alpaca IEX"));
        if (b.open != null) items.push(card("Minute open", money(b.open), "Latest IEX bar"));
        if (b.high != null && b.low != null) items.push(card("Minute range", money(b.low) + " – " + money(b.high), "Latest IEX bar"));
        if (b.volume != null) items.push(card("Minute volume", fmt(b.volume, 0), "Latest IEX bar"));
      } else if (finazon && finazon.state === "SOURCE_BOUND") {
        const t = finazon.last_trade || {}, s = finazon.session || {};
        if (t.price != null) items.push(card("Current trade", money(t.price), "Finazon"));
        if (s.o != null) items.push(card("Session open", money(s.o), "Finazon"));
        if (s.h != null && s.l != null) items.push(card("Session range", money(s.l) + " – " + money(s.h), "Finazon"));
        if (s.v != null) items.push(card("Session volume", fmt(s.v, 0), "Finazon"));
        if (finazon.daily_change_percent != null) items.push(card("Daily change", pct(finazon.daily_change_percent), "Finazon"));
      }
      if (alpha && alpha.state === "SOURCE_BOUND" && Array.isArray(alpha.bars) && alpha.bars.length) {
        const latest = alpha.bars[0];
        items.push(card("Last daily close", money(latest.close), latest.session_date));
        items.push(card("Daily range", money(latest.low) + " – " + money(latest.high), latest.session_date));
        items.push(card("Daily volume", fmt(latest.volume, 0), latest.session_date));
      }
      if (items.length) metrics.replaceChildren(...items.slice(0, 8));
    }

    const facts = byId("symbolStarFacts");
    if (facts) {
      const items = [];
      if (profile) {
        if (profile.exchange) items.push(fact("Exchange", profile.exchange));
        if (profile.industry) items.push(fact("Industry", profile.industry));
        if (profile.country) items.push(fact("Country", profile.country));
        if (profile.currency) items.push(fact("Currency", profile.currency));
        if (profile.week_52_low != null && profile.week_52_high != null) {
          items.push(fact("52-week range", money(profile.week_52_low) + " – " + money(profile.week_52_high)));
        }
      }
      if (finnhub && finnhub.state === "SOURCE_BOUND") {
        if (!profile && finnhub.exchange) items.push(fact("Exchange", finnhub.exchange));
        if (!profile && finnhub.industry) items.push(fact("Industry", finnhub.industry));
        if (finnhub.ipo_date) items.push(fact("IPO", finnhub.ipo_date));
        if (!profile && finnhub.country) items.push(fact("Country", finnhub.country));
        if (!profile && finnhub.currency) items.push(fact("Currency", finnhub.currency));
        if (finnhub.website) items.push(fact("Website", finnhub.website));
      }
      if (!profile && finazon && finazon.state === "SOURCE_BOUND") {
        if (finazon.low_52w != null && finazon.high_52w != null) {
          items.push(fact("52-week range", money(finazon.low_52w) + " – " + money(finazon.high_52w)));
        }
      }
      if (items.length) facts.replaceChildren(...items.slice(0, 10));
    }
  }

  function hydrateHeroFromAlpaca(row) {
    if (!row || row.state !== "SOURCE_BOUND") return;
    const q = row.quote || {};
    const b = row.bar || {};
    if (q.midpoint != null) {
      const metrics = byId("symbolUnderlyingMetrics");
      const first = metrics && metrics.querySelector(".ob-symbol-metric strong");
      if (first && (first.textContent === "—" || first.textContent === "$0.00")) {
        first.textContent = Number(q.midpoint).toLocaleString(undefined, {
          style:"currency", currency:"USD", maximumFractionDigits:2
        });
      }
    }
    set("symbolSource", "Alpaca IEX");
    set("symbolAsOf", q.timestamp || b.timestamp || row.as_of, "Unavailable");
    set("symbolFreshness", "current venue context");
    const chip = byId("symbolTruthChip");
    if (chip) {
      chip.className = "ob-symbol-chip ob-symbol-chip--current";
      chip.textContent = "Live · Alpaca IEX";
    }
  }

  function renderProviderResearch(packet, ticker) {
    if (!packet || packet.schema !== "OB_KEYED_PROVIDER_RESEARCH_V1" || packet.symbol !== ticker) {
      throw new Error("provider contract hold");
    }
    const rows = packet.provider_research || [];
    const alpaca = sourceRow(rows, "alpaca");
    const finnhub = sourceRow(rows, "finnhub");
    const alpha = sourceRow(rows, "alpha_vantage");
    const finazon = sourceRow(rows, "finazon");
    const bea = sourceRow(rows, "bea");

    if (alpaca && alpaca.state === "SOURCE_BOUND") {
      const q = alpaca.quote || {}, b = alpaca.bar || {};
      
      set("symbolResearchMarket",
        "Bid " + fmt(q.bid) + " · Ask " + fmt(q.ask) + " · Mid " + fmt(q.midpoint) +
        " · minute close " + fmt(b.close) + " · minute volume " + fmt(b.volume, 0) +
        ". IEX venue context; not SIP/NBBO.");
      hydrateHeroFromAlpaca(alpaca);
    } else if (finazon && finazon.state === "SOURCE_BOUND") {
      const t = finazon.last_trade || {}, s = finazon.session || {};
      
      set("symbolResearchMarket",
        "Last source trade " + fmt(t.price) + " · session " + fmt(s.l) + "–" + fmt(s.h) +
        " · daily change " + pct(finazon.daily_change_percent) +
        " · 52-week range " + fmt(finazon.low_52w) + "–" + fmt(finazon.high_52w) + ".");
    } else {
      
      set("symbolResearchMarket", "Neither Alpaca nor Finazon returned source-bound current context for this symbol.");
    }

    const alphaProfile = alpha && alpha.state === "SOURCE_BOUND" && alpha.company_profile &&
      typeof alpha.company_profile === "object" ? alpha.company_profile : null;
    if (alphaProfile) {
      const bits = [
        alphaProfile.name,
        alphaProfile.sector,
        alphaProfile.industry,
        alphaProfile.exchange,
        alphaProfile.country
      ].filter(Boolean);
      const summary = bits.join(" · ");
      const description = alphaProfile.description ? " " + alphaProfile.description.slice(0, 700) : "";
      set("symbolResearchCompany", (summary || "Alpha Company Overview returned.") + description);
    } else if (finnhub && finnhub.state === "SOURCE_BOUND") {
      const bits = [finnhub.industry, finnhub.exchange, finnhub.ipo_date && ("IPO " + finnhub.ipo_date)].filter(Boolean);
      set("symbolResearchCompany", bits.join(" · ") || "Company profile returned without extra classification.");
    } else {
      set("symbolResearchCompany", "No source-bound company profile returned for this symbol.");
    }

    if (alpha && alpha.state === "SOURCE_BOUND" && Array.isArray(alpha.bars) && alpha.bars.length) {
      const latest = alpha.bars[0], prior = alpha.bars[1];
      
      set("symbolResearchHistory",
        latest.session_date + " close " + fmt(latest.close) +
        (prior ? " · prior " + prior.session_date + " close " + fmt(prior.close) : "") +
        " · completed-session history only.");
    } else {
      
      set("symbolResearchHistory", "Alpha Vantage completed-session history is unavailable or held.");
    }

    if (bea && bea.state === "SOURCE_BOUND" && Array.isArray(bea.macro_series)) {
      const growth = bea.macro_series.find(x => x.series_id === "real_gdp_growth");
      const prices = bea.macro_series.find(x => x.series_id === "gdp_price_change");
      const nominal = bea.macro_series.find(x => x.series_id === "nominal_gdp");
      const real = bea.macro_series.find(x => x.series_id === "real_gdp");
      const g = growth && growth.observations && growth.observations[0];
      const p = prices && prices.observations && prices.observations[0];
      const n = nominal && nominal.observations && nominal.observations[0];
      const r = real && real.observations && real.observations[0];
      
      set("symbolResearchMacro",
        (g ? "Real GDP growth " + g.value + "% (" + g.period + "). " : "") +
        (p ? "GDP price change " + p.value + "% (" + p.period + "). " : "") +
        (n ? "Nominal GDP " + n.value + " " + nominal.unit + ". " : "") +
        (r ? "Real GDP " + r.value + " " + real.unit + "." : ""));
    } else {
      
      set("symbolResearchMacro", "No source-bound BEA macro context is available.");
    }

    return rows.filter(row => row && row.state === "SOURCE_BOUND").length;
  }

  function renderKeyless(packet, ticker) {
    if (!packet || packet.schema !== "OB_KEYLESS_PUBLIC_CONTEXT_V1" || packet.symbol !== ticker) {
      throw new Error("keyless contract hold");
    }
    const rows = packet.sources || [];
    const bls = sourceRow(rows, "bls", "source");
    const treasury = sourceRow(rows, "treasury", "source");
    const figi = sourceRow(rows, "openfigi", "source");

    if (bls && bls.state === "SOURCE_BOUND" && Array.isArray(bls.series)) {
      const parts = bls.series.filter(x => x && x.state === "SOURCE_BOUND").map(x =>
        x.label + " " + x.value + (x.unit === "percent" ? "%" : "") + " (" + x.period + ")"
      );
      
      set("symbolResearchBls", parts.join(" · ") || "BLS returned no displayable reviewed series.");
    } else {
      
      set("symbolResearchBls", "CPI, unemployment, payrolls and PPI are unavailable or held.");
    }

    if (treasury && treasury.state === "SOURCE_BOUND") {
      const rates = treasury.rates || {};
      const parts = ["Public debt " + fmt(treasury.value, 0) + " (" + treasury.period + ")"];
      if (rates.state === "SOURCE_BOUND") {
        const nominal = rates.nominal || {};
        const yields = nominal.yields_percent || {};
        const real = rates.real || {};
        const realYields = real.yields_percent || {};
        const derived = rates.derived || {};
        if (nominal.date) {
          parts.push(
            "Nominal yields " + nominal.date +
            ": 2Y " + (yields["2Y"] || "—") + "%, 10Y " + (yields["10Y"] || "—") +
            "%, 30Y " + (yields["30Y"] || "—") + "%"
          );
        }
        if (real.date) {
          parts.push(
            "Real yields " + real.date +
            ": 5Y " + (realYields["5Y"] || "—") + "%, 10Y " + (realYields["10Y"] || "—") +
            "%, 30Y " + (realYields["30Y"] || "—") + "%"
          );
        }
        if (derived.curve_shape) {
          parts.push(
            "2s10s curve " + String(derived.curve_shape).replaceAll("_"," ").toLowerCase() +
            " at " + (derived.two_ten_spread_bp || "—") + " bp" +
            (derived.curve_change ? ", " + String(derived.curve_change).replaceAll("_"," ").toLowerCase() : "")
          );
        }
        if (derived.ten_year_breakeven_percent) {
          parts.push("10Y breakeven approximation " + derived.ten_year_breakeven_percent + "%");
        }
      }
      
      set("symbolResearchTreasury", parts.join(" · "));
    } else {
      
      set("symbolResearchTreasury", "Debt and rate context are unavailable or held.");
    }

    if (figi && figi.state === "SOURCE_BOUND" && figi.value) {
      
      set("symbolResearchFigi", ticker + " maps to FIGI " + figi.value + ". Reference identity only; not issuer verification or market data.");
    } else {
      
      set("symbolResearchFigi", "No unambiguous reviewed FIGI mapping is available.");
    }
    return rows.filter(row => row && row.state === "SOURCE_BOUND").length;
  }

  function renderCatalysts(packet) {
    if (!packet || packet.schema !== "OB_OFFICIAL_CATALYST_RADAR_V1") throw new Error("catalyst contract hold");
    const mount = byId("symbolResearchCatalysts");
    if (!mount) return 0;
    mount.replaceChildren();
    let count = 0;
    (packet.sources || []).forEach(row => {
      if (!row || row.source === "sec_edgar" || !CATALYST_SOURCES.includes(row.source)) return;
      const card = document.createElement("article");
      card.className = "ob-symbol-research-note";
      const title = document.createElement("strong");
      title.textContent = String(row.label || row.source || "source").toUpperCase();
      card.append(title);
      if (row.state === "SOURCE_BOUND") {
        count += 1;
        const facts = Array.isArray(row.facts) ? row.facts : [];
        if (!facts.length) card.append(paragraph("No active source fact in the current response.", "ob-symbol-research-muted"));
        facts.forEach(fact => {
          const parts = [fact.title, fact.value, fact.period].filter(Boolean);
          card.append(paragraph(parts.join(" · ")));
        });
        const reviewed = packet.soulaana && Array.isArray(packet.soulaana.observations)
          ? packet.soulaana.observations.find(x => x && x.source === row.source) : null;
        if (reviewed && reviewed.how_to_interpret) {
          card.append(paragraph("Soulaana · " + reviewed.how_to_interpret, "ob-symbol-research-muted"));
        }
      } else {
        card.append(paragraph(String(row.state || "held").replaceAll("_"," "), "ob-symbol-research-hold"));
      }
      mount.append(card);
    });
    return count;
  }


  function filteredPackets(providerPacket, keylessPacket, catalystPacket, secPacket, settings) {
    const s = settings || {};
    let provider = providerPacket;
    if (providerPacket && Array.isArray(providerPacket.provider_research)) {
      provider = Object.assign({}, providerPacket, {
        provider_research: providerPacket.provider_research.map(row => {
          if (!row) return null;
          if (["alpaca","finazon","public"].includes(row.provider) && s.use_current_market_context === false) return null;
          if (row.provider === "alpha_vantage" && s.use_completed_session_history === false) {
            return Object.assign({}, row, {bars: []});
          }
          if (row.provider === "bea" && s.use_macro_context === false) return null;
          return row;
        }).filter(Boolean)
      });
    }
    let keyless = keylessPacket;
    if (keylessPacket && Array.isArray(keylessPacket.sources) && s.use_macro_context === false) {
      keyless = Object.assign({}, keylessPacket, {
        sources: keylessPacket.sources.filter(row => row && !["bls","treasury"].includes(row.source))
      });
    }
    return {
      provider,
      keyless,
      catalysts: s.use_official_catalysts === false ? null : catalystPacket,
      sec: s.use_sec_filings === false ? null : secPacket,
    };
  }

  function applyOwnerSettings(settings) {
    const s = settings || {};
    const evidence = document.querySelector(".ob-symbol-evidence-drawer");
    if (evidence) evidence.hidden = s.show_evidence_drawer === false;
    const accounting = document.querySelector(".ob-symbol-source-accounting-card");
    if (accounting) accounting.hidden = s.show_source_accounting === false;
    const companyProfile = byId("symbolCompanyProfileCard");
    if (companyProfile && s.show_company_background === false) companyProfile.hidden = true;
    document.body.classList.toggle("ob-symbol-compact-top", s.compact_symbol_top === true);
  }

  async function load() {
    const ticker = symbol();
    if (!ticker) return;
    set("symbolResearchStatus", "Pulling " + ticker + " research across every reviewed lane…");
    const results = await Promise.allSettled([
      json("/ob/research/providers.json?symbol=" + encodeURIComponent(ticker)),
      json("/ob/research/keyless.json?symbol=" + encodeURIComponent(ticker)),
      json("/ob/research/catalysts.json"),
      json("/ob/settings.json")
    ]);
    const settingsPacket = results[3].status === "fulfilled" ? results[3].value : null;
    const settings = settingsPacket && settingsPacket.schema === "OB_OWNER_SETTINGS_V1"
      ? settingsPacket.settings || {} : {};
    applyOwnerSettings(settings);

    let providerCount = 0, publicCount = 0, catalystCount = 0, live = false;
    if (results[0].status === "fulfilled") {
      try {
        providerCount = renderProviderResearch(results[0].value, ticker);
        if (settings.show_company_background !== false || settings.use_current_market_context !== false || settings.use_completed_session_history !== false) {
          hydrateTopSymbolFacts(results[0].value, ticker, settings);
        }
        live = results[0].value.live_prices_attached === true;
      } catch (_) {}
    }
    if (results[1].status === "fulfilled") {
      try { publicCount = renderKeyless(results[1].value, ticker); } catch (_) {}
    }
    if (results[2].status === "fulfilled") {
      try { catalystCount = renderCatalysts(results[2].value); } catch (_) {}
    }

    const total = providerCount + publicCount + catalystCount;
    const providerPacket = results[0].status === "fulfilled" ? results[0].value : null;
    const keylessPacket = results[1].status === "fulfilled" ? results[1].value : null;
    const catalystPacket = results[2].status === "fulfilled" ? results[2].value : null;
    const secPacket = serverResearch();
    const active = filteredPackets(providerPacket, keylessPacket, catalystPacket, secPacket, settings);
    const governmentDossier = governmentCompanyDossier(
      active.provider, active.keyless, active.catalysts, active.sec, ticker, settings
    );
    buildImpact(active.provider, active.keyless, active.catalysts, active.sec, ticker, governmentDossier);
    renderSourceAccounting(providerPacket, keylessPacket, catalystPacket, secPacket);

    if (settings.soulaana_show_missing === false) {
      const caution = byId("symbolSoulaanaCaution");
      const next = byId("symbolSoulaanaNext");
      if (caution && /missing|cannot|not cleared|unavailable/i.test(caution.textContent || "")) caution.textContent = "Missing-data commentary is hidden in Settings.";
      if (next && /missing|remain separate|unavailable/i.test(next.textContent || "")) next.textContent = "Missing-data commentary is hidden in Settings.";
    }
    set("symbolImpactFreshness", live ? "Current + fused context" : "Fused research context");

    if (!total) {
      set("symbolImpactHeadline", "Evidence is held");
      set("symbolImpactSummary", "The research routes answered, but no reviewed source returned source-bound content. I am not filling those gaps with guesses.");
      set("symbolImpactFreshness", "Research held");
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", load, {once:true});
  else load();

  let refreshTimer = null;
  async function scheduleFromSettings() {
    try {
      const packet = await json("/ob/settings.json");
      const settings = packet && packet.settings || {};
      if (refreshTimer) window.clearInterval(refreshTimer);
      if (settings.auto_refresh_symbol_research !== false) {
        const seconds = [15,30,60,120].includes(Number(settings.refresh_seconds)) ? Number(settings.refresh_seconds) : 30;
        refreshTimer = window.setInterval(function () {
          if (document.visibilityState === "visible") load();
        }, seconds * 1000);
      }
      if (settings.refresh_on_focus !== false) {
        document.addEventListener("visibilitychange", function () {
          if (document.visibilityState === "visible") load();
        });
      }
    } catch (_) {}
  }
  scheduleFromSettings();
})();
