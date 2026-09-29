/* Owner-only official research, separate from quotes, broker and existing keyless status.
   All text from public APIs is inserted via textContent, never HTML. */
(function () {
  "use strict";
  const root = document.getElementById("obKeylessContextRoot");
  if (!root) return;
  const names = ["federal_register", "cftc", "eia", "world_bank", "nws", "sec_edgar"];
  const docs = Object.freeze({
    federal_register: "https://www.federalregister.gov/developers/documentation/api/v1",
    cftc: "https://publicreporting.cftc.gov/stories/s/r4w3-av2u",
    eia: "https://www.eia.gov/opendata/",
    world_bank: "https://data.worldbank.org/indicator/NY.GDP.MKTP.CD",
    nws: "https://www.weather.gov/documentation/services-web-api",
    sec_edgar: "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"
  });
  const states = Object.freeze({
    REVIEW_HOLD: "Rights review not active",
    KEY_REQUIRED: "Free EIA key required",
    SOURCE_HOLD: "Source unavailable or validation held",
    SOURCE_BOUND: "Official evidence read",
    NO_PUBLICATION: "No validated publication in this request",
    EXISTING_PROTECTED_CORRIDOR: "Existing SEC Symbol Research"
  });
  function node(tag, cls, value) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (value !== undefined) n.textContent = String(value);
    return n;
  }
  function reference(source, url) {
    if (source === "federal_register" && typeof url === "string") {
      return /^https:\/\/www\.federalregister\.gov\/(?:d\/|documents\/)[A-Za-z0-9/_-]{8,260}$/.test(url);
    }
    if (source === "nws" && typeof url === "string") {
      return /^https:\/\/(?:api|alerts)\.weather\.gov\/[A-Za-z0-9/:._?=%-]{1,240}$/.test(url);
    }
    return Object.prototype.hasOwnProperty.call(docs, source) && url === docs[source];
  }
  const panel = node("section", "ob-keyless-soulaana");
  panel.setAttribute("aria-label", "Official Market Catalyst Radar and Soulaana source translation");
  panel.append(node("span", "ob-keyless-eyebrow", "OFFICIAL CATALYST RADAR · COMMERCIAL RIGHTS GATED"),
    node("h2", "", "Soulaana's public-source intelligence"),
    node("p", "ob-keyless-intro",
      "Federal Register, CFTC, EIA, World Bank and NWS. Separate source permissions; SEC filings remain in existing Symbol Research. No stock or option quote."));
  const status = node("p", "ob-keyless-status", "Checking protected official-source corridor…");
  status.setAttribute("role", "status");
  const cards = node("div", "ob-keyless-grid");
  const explain = node("div", "ob-keyless-soulaana-register");
  panel.append(status, cards, explain);
  root.append(panel);

  function valid(packet) {
    return packet && packet.schema === "OB_OFFICIAL_CATALYST_RADAR_V1" &&
      packet.source_only === true && packet.context_only === true &&
      packet.prices_attached === false && packet.options_chain_attached === false &&
      packet.live_quote_verified === false && packet.candidate_admitted === false &&
      packet.broker_execution_authorized === false && packet.paid_resources === false &&
      Array.isArray(packet.sources) && packet.sources.length === 6 &&
      packet.sources.every((r, i) =>
        r && r.source === names[i] && r.source_reference === docs[r.source] &&
        typeof r.state === "string" && Object.prototype.hasOwnProperty.call(states, r.state) &&
        r.source_only === true && r.quote_eligible === false &&
        r.candidate_admitted === false && r.execution_authorized === false &&
        typeof r.ai_use_approved === "boolean" &&
        Array.isArray(r.facts) && r.facts.length <= 3 &&
        (!r.ai_use_approved || r.state === "SOURCE_BOUND")) &&
      packet.soulaana && packet.soulaana.schema === "OB_SOULAANA_OFFICIAL_CATALYST_V1" &&
      packet.soulaana.channel === "OFFICIAL_REVIEWED_CATALYSTS" &&
      packet.soulaana.external_model_called === false &&
      packet.soulaana.blanket_ai_authority === false &&
      packet.soulaana.quote_verified === false &&
      packet.soulaana.broker_execution_authorized === false &&
      packet.soulaana.candidate_admitted === false &&
      Array.isArray(packet.soulaana.observations) &&
      packet.soulaana.observation_count === packet.soulaana.observations.length &&
      packet.soulaana.observations.length <= 5 &&
      packet.soulaana.observations.every(e =>
        e && packet.sources.some(r => r.source === e.source &&
          r.state === "SOURCE_BOUND" && r.ai_use_approved === true &&
          r.source_reference === e.source_reference) &&
        e.source_specific_ai_reviewed === true && e.external_model_called === false &&
        e.quote_verified === false && e.execution_authorized === false &&
        e.causality_claimed === false && Array.isArray(e.factual_findings) &&
        e.factual_findings.length <= 3 &&
        e.factual_findings.every(x => typeof x === "string" && x.length <= 550) &&
        typeof e.how_to_interpret === "string" && e.how_to_interpret.length <= 450);
  }

  function safeLink(source, url, label) {
    if (!reference(source, url)) return node("span", "ob-keyless-meta", "Source link held");
    const a = node("a", "ob-keyless-docs", label);
    a.href = url; a.target = "_blank"; a.rel = "noopener noreferrer";
    return a;
  }

  function draw(packet) {
    cards.replaceChildren(); explain.replaceChildren();
    packet.sources.forEach(r => {
      const card = node("article", "ob-keyless-card");
      const top = node("div", "ob-keyless-cardtop");
      top.append(node("h3", "", r.label),
        node("span", "ob-keyless-badge " + (r.state === "SOURCE_BOUND" ? "good" : "hold"),
          states[r.state]));
      card.append(top);
      if (r.state === "SOURCE_BOUND") {
        if (!r.facts.length) card.append(node("p", "ob-keyless-meta",
          "No matching observations in this snapshot; this does not establish overall safety."));
        r.facts.forEach(f => {
          if (!f || typeof f.title !== "string" || typeof f.period !== "string" ||
              f.title.length > 250 || f.period.length > 40) return;
          const item = node("p", "ob-keyless-meta", f.period + " · " +
            (f.stage ? f.stage + " · " : "") + f.title +
            (typeof f.value === "string" ? " · " + f.value : ""));
          card.append(item);
          if (reference(r.source, f.reference)) card.append(safeLink(r.source, f.reference, "Original record ↗"));
        });
        card.append(node("p", "ob-keyless-meta", "Retrieved: " + (r.retrieved_at || "unavailable")));
      } else if (r.source === "sec_edgar") {
        card.append(node("p", "ob-keyless-meta",
          "Use existing protected Symbol Research for SEC filings; this radar does not re-fetch EDGAR."));
      } else {
        card.append(node("p", "ob-keyless-meta",
          "No approved source observation is present. No placeholder, stale value or substitute feed."));
      }
      card.append(safeLink(r.source, r.source_reference, "Source documentation ↗"));
      cards.append(card);
    });
    explain.append(node("h3", "", "What Soulaana actually examined"),
      node("p", "ob-keyless-meta", packet.soulaana.interpretation));
    if (!packet.soulaana.observations.length) {
      explain.append(node("p", "ob-keyless-meta",
        "No source has both validated evidence and an independent Soulaana-content review."));
    }
    packet.soulaana.observations.forEach(e => {
      const item = node("article", "ob-keyless-evidence-item");
      item.append(node("strong", "", e.source.replaceAll("_", " ").toUpperCase()));
      e.factual_findings.forEach(t => item.append(node("p", "", t)));
      item.append(node("p", "ob-keyless-meta", e.how_to_interpret),
        safeLink(e.source, e.source_reference, "Original source ↗"));
      explain.append(item);
    });
    explain.append(node("p", "ob-keyless-footer",
      "Source publication time is not retrieval time. Deterministic, reviewed evidence explanations only; no external model call, quote, forecast, causality or execution permission."));
    status.textContent = packet.soulaana.observation_count + " independently reviewed source explanations available.";
  }
  fetch("/ob/research/catalysts.json", {
    method: "GET", credentials: "same-origin",
    headers: {"Accept": "application/json"}, cache: "no-store"
  }).then(response => {
    if (!response.ok) throw new Error("source held");
    return response.json();
  }).then(packet => {
    if (!valid(packet)) throw new Error("source contract hold");
    draw(packet);
  }).catch(() => {
    status.textContent = "Official Catalyst Radar is unavailable or access is held. No data asserted.";
    cards.replaceChildren(); explain.replaceChildren();
  });
})();
