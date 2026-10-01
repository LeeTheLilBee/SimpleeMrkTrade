(function () {
  "use strict";

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
      set("symbolResearchMarketTitle", "Alpaca IEX · current");
      set("symbolResearchMarket",
        "Bid " + fmt(q.bid) + " · Ask " + fmt(q.ask) + " · Mid " + fmt(q.midpoint) +
        " · minute close " + fmt(b.close) + " · minute volume " + fmt(b.volume, 0) +
        ". IEX venue context; not SIP/NBBO.");
      hydrateHeroFromAlpaca(alpaca);
    } else if (finazon && finazon.state === "SOURCE_BOUND") {
      const t = finazon.last_trade || {}, s = finazon.session || {};
      set("symbolResearchMarketTitle", "Finazon · current context");
      set("symbolResearchMarket",
        "Last source trade " + fmt(t.price) + " · session " + fmt(s.l) + "–" + fmt(s.h) +
        " · daily change " + pct(finazon.daily_change_percent) +
        " · 52-week range " + fmt(finazon.low_52w) + "–" + fmt(finazon.high_52w) + ".");
    } else {
      set("symbolResearchMarketTitle", "Current market lane held");
      set("symbolResearchMarket", "Neither Alpaca nor Finazon returned source-bound current context for this symbol.");
    }

    if (finnhub && finnhub.state === "SOURCE_BOUND") {
      set("symbolResearchCompanyTitle", finnhub.security_name || ticker);
      const bits = [finnhub.industry, finnhub.exchange, finnhub.ipo_date && ("IPO " + finnhub.ipo_date)].filter(Boolean);
      set("symbolResearchCompany", bits.join(" · ") || "Company profile returned without extra classification.");
      if (finnhub.security_name) set("symbolCompany", finnhub.security_name);
      if (finnhub.industry) set("symbolSector", finnhub.industry);
    } else {
      set("symbolResearchCompanyTitle", "Company profile held");
      set("symbolResearchCompany", "Finnhub did not return a source-bound profile for this symbol.");
    }

    if (alpha && alpha.state === "SOURCE_BOUND" && Array.isArray(alpha.bars) && alpha.bars.length) {
      const latest = alpha.bars[0], prior = alpha.bars[1];
      set("symbolResearchHistoryTitle", "Alpha Vantage · completed sessions");
      set("symbolResearchHistory",
        latest.session_date + " close " + fmt(latest.close) +
        (prior ? " · prior " + prior.session_date + " close " + fmt(prior.close) : "") +
        " · completed-session history only.");
    } else {
      set("symbolResearchHistoryTitle", "History lane held");
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
      set("symbolResearchMacroTitle", "BEA · U.S. economy");
      set("symbolResearchMacro",
        (g ? "Real GDP growth " + g.value + "% (" + g.period + "). " : "") +
        (p ? "GDP price change " + p.value + "% (" + p.period + "). " : "") +
        (n ? "Nominal GDP " + n.value + " " + nominal.unit + ". " : "") +
        (r ? "Real GDP " + r.value + " " + real.unit + "." : ""));
    } else {
      set("symbolResearchMacroTitle", "BEA macro lane held");
      set("symbolResearchMacro", "No source-bound BEA macro context is available.");
    }

    const mount = byId("symbolResearchSoulaana");
    if (mount) {
      mount.replaceChildren();
      const observations = packet.soulaana_research && Array.isArray(packet.soulaana_research.observations)
        ? packet.soulaana_research.observations : [];
      observations.forEach(item => {
        const card = document.createElement("article");
        card.className = "ob-symbol-research-note";
        const title = document.createElement("strong");
        title.textContent = String(item.provider || "source").toUpperCase();
        card.append(title, paragraph(item.finding || "No finding supplied."));
        if (item.why_it_matters) card.append(paragraph("Why it matters · " + item.why_it_matters, "ob-symbol-research-muted"));
        if (Array.isArray(item.what_would_confirm) && item.what_would_confirm.length) {
          card.append(paragraph("Would confirm · " + item.what_would_confirm.join(" "), "ob-symbol-research-muted"));
        }
        if (Array.isArray(item.what_would_conflict) && item.what_would_conflict.length) {
          card.append(paragraph("Would conflict · " + item.what_would_conflict.join(" "), "ob-symbol-research-muted"));
        }
        if (item.what_is_missing) card.append(paragraph("Still missing · " + item.what_is_missing, "ob-symbol-research-hold"));
        mount.append(card);
      });
      if (!observations.length) mount.append(paragraph("No connected provider content is cleared for explanation right now.", "ob-symbol-research-muted"));
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
      set("symbolResearchBlsTitle", "BLS · labor + inflation");
      set("symbolResearchBls", parts.join(" · ") || "BLS returned no displayable reviewed series.");
    } else {
      set("symbolResearchBlsTitle", "BLS lane held");
      set("symbolResearchBls", "CPI, unemployment, payrolls and PPI are unavailable or held.");
    }

    if (treasury && treasury.state === "SOURCE_BOUND") {
      const rates = treasury.rates || {};
      const parts = ["Public debt " + treasury.value + " (" + treasury.period + ")"];
      if (rates.state === "SOURCE_BOUND") {
        if (rates.nominal) parts.push("Nominal curve " + JSON.stringify(rates.nominal));
        if (rates.real) parts.push("Real curve " + JSON.stringify(rates.real));
        if (rates.derived) parts.push("Derived " + JSON.stringify(rates.derived));
      }
      set("symbolResearchTreasuryTitle", "U.S. Treasury");
      set("symbolResearchTreasury", parts.join(" · "));
    } else {
      set("symbolResearchTreasuryTitle", "Treasury lane held");
      set("symbolResearchTreasury", "Debt and rate context are unavailable or held.");
    }

    if (figi && figi.state === "SOURCE_BOUND" && figi.value) {
      set("symbolResearchFigiTitle", "OpenFIGI · matched");
      set("symbolResearchFigi", ticker + " maps to FIGI " + figi.value + ". Reference identity only; not issuer verification or market data.");
    } else {
      set("symbolResearchFigiTitle", "OpenFIGI · " + String((figi && figi.state) || "held").replaceAll("_"," "));
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
      if (!row || row.source === "sec_edgar") return;
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

  async function load() {
    const ticker = symbol();
    if (!ticker) return;
    set("symbolResearchStatus", "Pulling " + ticker + " research across every reviewed lane…");
    const results = await Promise.allSettled([
      json("/ob/research/providers.json?symbol=" + encodeURIComponent(ticker)),
      json("/ob/research/keyless.json?symbol=" + encodeURIComponent(ticker)),
      json("/ob/research/catalysts.json")
    ]);

    let providerCount = 0, publicCount = 0, catalystCount = 0, live = false;
    if (results[0].status === "fulfilled") {
      try {
        providerCount = renderProviderResearch(results[0].value, ticker);
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
    set("symbolResearchStatus",
      total + " source-backed research lane" + (total === 1 ? "" : "s") +
      " feeding this room · provider + public reference + catalyst context.");
    set("symbolResearchFreshness", live ? "Current + deep research" : "Deep research");

    if (!total) {
      set("symbolResearchStatus", "Research routes answered, but no reviewed source returned source-bound content. No gaps were filled with guesses.");
      set("symbolResearchFreshness", "Research held");
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", load, {once:true});
  else load();

  window.setInterval(function () {
    if (document.visibilityState === "visible") load();
  }, 30000);
})();
