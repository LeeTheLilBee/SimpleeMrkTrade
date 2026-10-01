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
  function sourceRow(rows, id) {
    return Array.isArray(rows) ? rows.find(row => row && row.provider === id) || null : null;
  }
  function paragraph(text, cls) {
    const p = document.createElement("p");
    if (cls) p.className = cls;
    p.textContent = text;
    return p;
  }
  function renderSoulaana(packet) {
    const mount = byId("symbolResearchSoulaana");
    if (!mount) return;
    mount.replaceChildren();
    const brief = packet && packet.soulaana_research;
    const observations = brief && Array.isArray(brief.observations) ? brief.observations : [];
    if (!observations.length) {
      mount.append(paragraph("I have connection status, but no provider content cleared for explanation on this symbol yet.", "ob-symbol-research-muted"));
      return;
    }
    observations.forEach(item => {
      const card = document.createElement("article");
      card.className = "ob-symbol-research-note";
      const title = document.createElement("strong");
      title.textContent = String(item.provider || "source").toUpperCase();
      card.append(title, paragraph(item.finding || "No finding supplied."));
      if (item.why_it_matters) card.append(paragraph("Why it matters · " + item.why_it_matters, "ob-symbol-research-muted"));
      if (item.what_is_missing) card.append(paragraph("Still missing · " + item.what_is_missing, "ob-symbol-research-hold"));
      mount.append(card);
    });
  }
  function hydrateHeroFromAlpaca(row) {
    if (!row || row.state !== "SOURCE_BOUND") return;
    const q = row.quote || {};
    const b = row.bar || {};
    const midpoint = q.midpoint;
    if (midpoint != null) {
      const metrics = byId("symbolUnderlyingMetrics");
      if (metrics) {
        const first = metrics.querySelector(".ob-symbol-metric strong");
        if (first && (first.textContent === "—" || first.textContent === "$0.00")) {
          first.textContent = Number(midpoint).toLocaleString(undefined, {style:"currency",currency:"USD",maximumFractionDigits:2});
        }
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
  async function load() {
    const ticker = symbol();
    if (!ticker) return;
    set("symbolResearchStatus", "Pulling " + ticker + " research through Tower…");
    try {
      const response = await fetch("/ob/research/providers.json?symbol=" + encodeURIComponent(ticker), {
        credentials: "same-origin",
        cache: "no-store",
        headers: {"Accept":"application/json"}
      });
      if (!response.ok) throw new Error("HTTP " + response.status);
      const packet = await response.json();
      if (!packet || packet.schema !== "OB_KEYED_PROVIDER_RESEARCH_V1" || packet.symbol !== ticker) {
        throw new Error("contract hold");
      }

      const rows = packet.provider_research || [];
      const alpaca = sourceRow(rows, "alpaca");
      const finnhub = sourceRow(rows, "finnhub");
      const alpha = sourceRow(rows, "alpha_vantage");
      const finazon = sourceRow(rows, "finazon");
      const bea = sourceRow(rows, "bea");

      if (alpaca && alpaca.state === "SOURCE_BOUND") {
        const q = alpaca.quote || {};
        const b = alpaca.bar || {};
        set("symbolResearchMarketTitle", "Alpaca IEX · current");
        set("symbolResearchMarket",
          "Bid " + fmt(q.bid) + " · Ask " + fmt(q.ask) + " · Mid " + fmt(q.midpoint) +
          " · Minute close " + fmt(b.close) + " · Volume " + fmt(b.volume, 0) +
          ". Venue-limited IEX context; not SIP/NBBO.");
        hydrateHeroFromAlpaca(alpaca);
      } else if (finazon && finazon.state === "SOURCE_BOUND") {
        const t = finazon.last_trade || {};
        const s = finazon.session || {};
        set("symbolResearchMarketTitle", "Finazon · venue-limited");
        set("symbolResearchMarket",
          "Last trade " + fmt(t.price) + " · Session " + fmt(s.l) + "–" + fmt(s.h) +
          " · Change " + pct(finazon.daily_change_percent) + ". Not SIP/NBBO.");
      } else {
        set("symbolResearchMarketTitle", "Current market lane held");
        set("symbolResearchMarket", "No source-bound current market context is available for this symbol.");
      }

      if (finnhub && finnhub.state === "SOURCE_BOUND") {
        set("symbolResearchCompanyTitle", finnhub.security_name || ticker);
        const bits = [finnhub.industry, finnhub.exchange].filter(Boolean);
        set("symbolResearchCompany", bits.length ? bits.join(" · ") : "Company profile returned without industry/exchange detail.");
        if (finnhub.security_name) set("symbolCompany", finnhub.security_name);
        if (finnhub.industry) set("symbolSector", finnhub.industry);
      } else {
        set("symbolResearchCompanyTitle", "Company profile held");
        set("symbolResearchCompany", "No source-bound company profile is available from the connected research lane.");
      }

      if (alpha && alpha.state === "SOURCE_BOUND" && Array.isArray(alpha.bars) && alpha.bars.length) {
        const latest = alpha.bars[0];
        const prior = alpha.bars[1];
        set("symbolResearchHistoryTitle", "Completed daily sessions");
        set("symbolResearchHistory",
          latest.session_date + " close " + fmt(latest.close) +
          (prior ? " · prior " + prior.session_date + " close " + fmt(prior.close) : "") +
          " · historical context, not a live quote.");
      } else {
        set("symbolResearchHistoryTitle", "History lane held");
        set("symbolResearchHistory", "No validated completed-session history is available from the connected provider.");
      }

      if (bea && bea.state === "SOURCE_BOUND" && Array.isArray(bea.macro_series)) {
        const growth = bea.macro_series.find(x => x.series_id === "real_gdp_growth");
        const prices = bea.macro_series.find(x => x.series_id === "gdp_price_change");
        const g = growth && growth.observations && growth.observations[0];
        const p = prices && prices.observations && prices.observations[0];
        set("symbolResearchMacroTitle", "BEA · official U.S. backdrop");
        set("symbolResearchMacro",
          (g ? "Real GDP growth " + g.value + "% (" + g.period + "). " : "") +
          (p ? "GDP price change " + p.value + "% (" + p.period + ")." : ""));
      } else {
        set("symbolResearchMacroTitle", "Macro lane held");
        set("symbolResearchMacro", "No source-bound BEA macro context is available right now.");
      }

      const boundCount = rows.filter(row => row && row.state === "SOURCE_BOUND").length;
      set("symbolResearchStatus", boundCount + " source-backed research lane" + (boundCount === 1 ? "" : "s") + " available for " + ticker + ".");
      set("symbolResearchFreshness", packet.live_prices_attached ? "Current + research" : "Research only");
      renderSoulaana(packet);
    } catch (error) {
      set("symbolResearchStatus", "Tower could not supply symbol research. No data was invented.");
      set("symbolResearchFreshness", "Research held");
      const mount = byId("symbolResearchSoulaana");
      if (mount) mount.replaceChildren(paragraph("The research request is held. I’m not filling the gaps with guesses.", "ob-symbol-research-hold"));
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load, {once:true});
  } else {
    load();
  }
  window.setInterval(function () {
    if (document.visibilityState === "visible") load();
  }, 20000);
})();
