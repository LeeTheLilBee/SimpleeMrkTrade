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
  const sourceDetails = node("details", "ob-keyless-evidence-drawer");
  sourceDetails.append(node("summary", "", "Show source records"), cards);
  const explain = node("div", "ob-catalyst-explanation");
  const transport = node("p", "ob-keyless-meta ob-catalyst-transport", "Source snapshot active.");
  const provenance = node("section", "ob-keyless-evidence-body");
  provenance.setAttribute("aria-label", "Soulaana evidence provenance and research triage");
  const provenanceDetails = node("details", "ob-keyless-evidence-drawer");
  provenanceDetails.append(node("summary", "", "Show provenance & timeline"), provenance);
  panel.append(status, explain, sourceDetails, provenanceDetails, transport);
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

  const periodKinds = Object.freeze({
    federal_register: "document_publication_date",
    cftc: "report_as_of_date", eia: "series_observation_period",
    world_bank: "annual_observation_year", nws: "alert_effective_time"
  });
  const changeStates = Object.freeze({
    FIRST_OBSERVED_IN_PROCESS: "First observed in this process",
    UNCHANGED_SINCE_LAST_VERIFIED_FETCH: "Unchanged since last verified fetch",
    CHANGED_SINCE_LAST_VERIFIED_FETCH: "Changed since last verified fetch"
  });
  function validProvenance(packet) {
    const x = packet.soulaana_provenance_triage;
    if (!x || x.schema !== "OB_SOULAANA_PROVENANCE_TRIAGE_V1" ||
        x.external_model_called !== false ||
        x.cross_source_causality_claimed !== false ||
        x.price_or_option_data_attached !== false ||
        x.ranking_performed !== false || x.execution_authorized !== false ||
        !Array.isArray(x.source_health) || x.source_health.length !== 6 ||
        !Array.isArray(x.event_timeline) || x.event_timeline.length > 12 ||
        x.timeline_count !== x.event_timeline.length ||
        !Array.isArray(x.series_comparisons) || x.series_comparisons.length > 2 ||
        x.comparison_count !== x.series_comparisons.length ||
        x.retrieval_not_publication !== true ||
        x.independent_upstream_families_not_reseller_count !== true) return false;
    if (!x.source_health.every((h, i) =>
        h && h.source === names[i] && h.source_reference === docs[h.source] &&
        h.state === packet.sources[i].state &&
        h.soulaana_content_approved === packet.sources[i].ai_use_approved &&
        h.validated_record_count === (h.state === "SOURCE_BOUND" ?
          packet.sources[i].facts.length : 0) &&
        typeof h.cache_hit === "boolean" &&
        (i === 5 ? h.period_kind === null :
          h.period_kind === periodKinds[h.source]))) return false;
    if (!x.event_timeline.every(t => t && periodKinds[t.source] &&
        t.period_kind === periodKinds[t.source] &&
        packet.sources.some(r => r.source === t.source &&
          r.ai_use_approved === true && r.state === "SOURCE_BOUND" &&
          r.facts.some(f => f.title === t.title && f.period === t.source_period &&
            f.reference === t.original_reference)) &&
        reference(t.source, t.original_reference) &&
        typeof t.title === "string" && t.title.length <= 250 &&
        typeof t.source_period === "string" && t.source_period.length <= 40 &&
        Object.prototype.hasOwnProperty.call(changeStates, t.change_since_last_verified_fetch) &&
        t.research_only === true && t.issuer_identity_proven === false &&
        t.quote_verified === false && t.trade_causality_claimed === false)) return false;
    if (!x.series_comparisons.every(r =>
        r && ["eia", "world_bank"].includes(r.source) &&
        packet.sources.some(s => s.source === r.source && s.ai_use_approved === true) &&
        r.source_reference === docs[r.source] && r.research_only === true &&
        r.causality_claimed === false && r.quote_verified === false &&
        ["UP", "DOWN", "UNCHANGED"].includes(r.direction) &&
        typeof r.difference_in_source_units === "string" &&
        r.difference_in_source_units.length <= 75)) return false;
    const ready = x.selection_readiness;
    return ready && ready.state === "SOURCE_CONTEXT_ONLY" &&
      ready.candidate_shortlist_authorized === false &&
      ready.issuer_identity_verified_in_this_corridor === false &&
      ready.live_equity_quote_verified_in_this_corridor === false &&
      ready.licensed_option_chain_verified_in_this_corridor === false &&
      ready.contract_liquidity_verified_in_this_corridor === false &&
      ready.capital_and_risk_policy_verified_in_this_corridor === false &&
      ready.owner_review_required === true &&
      Array.isArray(ready.next_evidence) && ready.next_evidence.length === 3 &&
      ready.next_evidence.every(t => typeof t === "string" && t.length <= 180);
  }

  function drawProvenance(packet) {
    provenance.replaceChildren();
    const x = packet.soulaana_provenance_triage;
    provenance.append(node("span", "ob-keyless-eyebrow", "SOURCE HEALTH · EVIDENCE TIMELINE"),
      node("h3", "", "What changed—and what is still missing"),
      node("p", "ob-keyless-meta",
        "Original source periods stay distinct from retrieval times. Source holds and absent publications cannot be treated as market signals."));
    const health = node("div", "ob-keyless-grid");
    x.source_health.forEach(h => {
      const card = node("article", "ob-keyless-card");
      card.append(node("strong", "", h.source.replaceAll("_", " ").toUpperCase()),
        node("p", "ob-keyless-meta", states[h.state] + " · " +
          h.validated_record_count + " validated records" +
          (h.cache_hit ? " · cached source receipt" : "")),
        node("p", "ob-keyless-meta",
          h.latest_source_period ? h.period_kind.replaceAll("_", " ") +
            ": " + h.latest_source_period : "No source period in this response"));
      health.append(card);
    });
    provenance.append(health, node("h3", "", "Source-backed event timeline"));
    if (!x.event_timeline.length) {
      provenance.append(node("p", "ob-keyless-meta",
        "No source content is independently approved for Soulaana's timeline."));
    }
    x.event_timeline.forEach(t => {
      const item = node("article", "ob-keyless-evidence-item");
      item.append(node("strong", "", t.title),
        node("p", "ob-keyless-meta", t.source.replaceAll("_", " ") + " · " +
          t.period_kind.replaceAll("_", " ") + ": " + t.source_period),
        node("p", "ob-keyless-meta", changeStates[t.change_since_last_verified_fetch]),
        safeLink(t.source, t.original_reference, "Original record ↗"));
      provenance.append(item);
    });
    if (x.series_comparisons.length) {
      provenance.append(node("h3", "", "Same-series changes"));
      x.series_comparisons.forEach(change => {
        provenance.append(node("p", "ob-keyless-meta",
          change.source.replaceAll("_", " ") + ": " + change.earlier_period +
          " → " + change.later_period + "; " + change.direction +
          " by " + change.difference_in_source_units + " source-reported units."));
      });
    }
    provenance.append(node("h3", "", "Shortlist readiness"),
      node("p", "ob-keyless-meta",
        "OFFICIAL RESEARCH ONLY · No verified current stock or options quotes, issuer-specific match, liquidity, capital clearance or trade candidate in this corridor."));
    x.selection_readiness.next_evidence.forEach(t =>
      provenance.append(node("p", "ob-keyless-meta", "• " + t)));
    provenance.append(node("p", "ob-keyless-footer", x.revision_note));
  }

  function validStream(hint) {
    return hint && hint.schema === "OB_EVENT_STREAM_HINT_V1" &&
      hint.path === "/ob/events/stream" &&
      hint.invalidation_only === true &&
      hint.content_attached === false &&
      hint.provider_payload_attached === false &&
      hint.provider_stream_attached === false &&
      hint.live_quote_payload_attached === false &&
      hint.broker_execution_authorized === false &&
      typeof hint.available === "boolean" &&
      typeof hint.epoch === "string" && /^[a-f0-9]{24}$/.test(hint.epoch) &&
      Number.isSafeInteger(hint.cursor) && hint.cursor >= 0;
  }

  function safeLink(source, url, label) {
    if (!reference(source, url)) return node("span", "ob-keyless-meta", "Source link held");
    const a = node("a", "ob-keyless-docs", label);
    a.href = url; a.target = "_blank"; a.rel = "noopener noreferrer";
    return a;
  }

  function draw(packet) {
    cards.replaceChildren();
    explain.replaceChildren();

    explain.append(
      node("span", "ob-keyless-eyebrow", "SOULAANA · CATALYST READ"),
      node("h3", "", "What matters"),
      node("p", "ob-keyless-lead", packet.soulaana.interpretation)
    );

    const takeawayWrap = node("div", "ob-keyless-takeaways");
    packet.soulaana.observations.slice(0, 4).forEach(e => {
      const first = Array.isArray(e.factual_findings) && e.factual_findings.length
        ? e.factual_findings[0]
        : e.how_to_interpret;
      takeawayWrap.append(node(
        "span",
        "ob-keyless-takeaway",
        e.source.replaceAll("_", " ").toUpperCase() + " · " + first
      ));
    });
    if (!packet.soulaana.observations.length) {
      takeawayWrap.append(node("span", "ob-keyless-takeaway", "No reviewed catalyst needs attention right now"));
    }
    explain.append(takeawayWrap);

    const readiness = packet.soulaana_provenance_triage.selection_readiness;
    if (readiness && Array.isArray(readiness.next_evidence) && readiness.next_evidence.length) {
      explain.append(node("p", "ob-keyless-next", "Next: " + readiness.next_evidence[0]));
    }

    packet.sources.forEach(r => {
      const card = node("article", "ob-keyless-card");
      const top = node("div", "ob-keyless-cardtop");
      top.append(node("h3", "", r.label),
        node("span", "ob-keyless-badge " + (r.state === "SOURCE_BOUND" ? "good" : "hold"),
          states[r.state]));
      card.append(top);

      if (r.state === "SOURCE_BOUND") {
        r.facts.slice(0, 3).forEach(f => {
          if (!f || typeof f.title !== "string" || typeof f.period !== "string") return;
          card.append(node("p", "ob-keyless-meta", f.period + " · " + f.title +
            (typeof f.value === "string" ? " · " + f.value : "")));
          if (reference(r.source, f.reference)) {
            card.append(safeLink(r.source, f.reference, "Original record ↗"));
          }
        });
      } else {
        card.append(node("p", "ob-keyless-meta", states[r.state]));
      }
      cards.append(card);
    });

    drawProvenance(packet);
    status.textContent = packet.soulaana.observation_count +
      " reviewed catalyst explanation" + (packet.soulaana.observation_count === 1 ? "" : "s") + ".";
  }
  let socket = null;
  let reconnectTask = null;
  let attempts = 0;
  let shutdown = false;
  let reloadInFlight = false;
  let lastPacket = null;

  function validEvent(event, expectedEpoch) {
    return event && event.schema === "OB_EVENT_STREAM_EVENT_V1" &&
      ["stream_ready", "research_context_changed", "source_status_changed",
       "market_snapshot_changed", "scanner_context_changed",
       "candidate_context_changed", "resync_required", "heartbeat"].includes(event.type) &&
      ["research", "system", "market", "scanner", "candidate"].includes(event.channel) &&
      event.epoch === expectedEpoch &&
      Number.isSafeInteger(event.cursor) && event.cursor >= 0 &&
      event.content_attached === false &&
      event.provider_payload_attached === false &&
      event.provider_stream_attached === false &&
      event.live_quote_payload_attached === false &&
      event.candidate_admitted === false && event.execution_authorized === false &&
      typeof event.needs_authenticated_snapshot === "boolean";
  }

  function scheduleReconnect() {
    if (shutdown || reconnectTask || !lastPacket ||
        !validStream(lastPacket.event_stream) || !lastPacket.event_stream.available) return;
    const delay = Math.min(30000, 1000 * Math.pow(2, Math.min(attempts++, 5)));
    reconnectTask = window.setTimeout(() => {
      reconnectTask = null;
      // Restore the authoritative snapshot first. A restarted server can have
      // a different process-local epoch and cursor; old deltas are never used.
      loadSnapshot(true);
    }, delay);
  }

  function connect(hint) {
    if (shutdown || socket || !validStream(hint) || !hint.available ||
        typeof window.WebSocket !== "function") return;
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const url = protocol + "//" + window.location.host + hint.path +
      "?epoch=" + encodeURIComponent(hint.epoch) + "&cursor=" + hint.cursor;
    const ws = new window.WebSocket(url);
    socket = ws;
    transport.textContent = "Protected WebSocket connecting. Official publishers still use their supported REST APIs.";
    ws.onopen = () => {
      if (socket !== ws) return;
      attempts = 0;
      transport.textContent = "Tower-authenticated Observatory event stream connected · notifications only; not a live quote feed.";
    };
    ws.onmessage = message => {
      if (socket !== ws) return;
      let event;
      try { event = JSON.parse(message.data); } catch (_) { ws.close(4400); return; }
      if (!validEvent(event, hint.epoch)) { ws.close(4400); return; }
      if (event.type === "resync_required" ||
          (event.type === "research_context_changed" &&
           event.snapshot_path === "/ob/research/catalysts.json")) {
        loadSnapshot(false);
      }
    };
    ws.onclose = event => {
      if (socket !== ws) return;
      socket = null;
      transport.textContent = "Protected stream disconnected; authoritative REST snapshot remains available.";
      if (![4400, 4403, 4429].includes(event.code)) scheduleReconnect();
    };
    ws.onerror = () => {
      if (socket === ws) transport.textContent =
        "WebSocket unavailable; authoritative REST snapshot remains available.";
    };
  }

  function loadSnapshot(connectAfter) {
    if (shutdown || reloadInFlight) return;
    reloadInFlight = true;
    fetch("/ob/research/catalysts.json", {
      method: "GET", credentials: "same-origin",
      headers: {"Accept": "application/json"}, cache: "no-store"
    }).then(response => {
      if (!response.ok) throw new Error("source held");
      return response.json();
    }).then(packet => {
      if (!valid(packet) || !validProvenance(packet) ||
          !validStream(packet.event_stream)) throw new Error("source contract hold");
      lastPacket = packet;
      draw(packet);
      if (!packet.event_stream.available) {
        transport.textContent = "REST delivery active · protected WebSocket deployment not enabled.";
        if (socket) { const previous = socket; socket = null; previous.close(); }
      } else if (!socket && (connectAfter || !reconnectTask)) {
        connect(packet.event_stream);
      }
    }).catch(() => {
      status.textContent = "Official Catalyst Radar is unavailable or access is held. No data asserted.";
      cards.replaceChildren(); explain.replaceChildren(); provenance.replaceChildren();
      lastPacket = null;
      transport.textContent = "Source access or schema held. The WebSocket will not bypass Tower's GET.";
      if (socket) { const previous = socket; socket = null; previous.close(); }
    }).finally(() => { reloadInFlight = false; });
  }

  window.addEventListener("pagehide", () => {
    shutdown = true;
    if (reconnectTask) window.clearTimeout(reconnectTask);
    if (socket) { const previous = socket; socket = null; previous.close(); }
  });
  loadSnapshot(true);
})();
