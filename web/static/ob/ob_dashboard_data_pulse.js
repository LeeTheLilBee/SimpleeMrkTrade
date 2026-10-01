// Dashboard Data Pulse — status only. Full research belongs in Settings → Market Data Desk.
(function () {
  "use strict";

  const mount = document.getElementById("obDataPulseChips");
  if (!mount) return;

  function chip(label, state) {
    const el = document.createElement("span");
    el.className = "ob-data-chip" + (state ? " " + state : "");
    el.textContent = label;
    return el;
  }

  function safeCountSources(packet, expectedSchema, expectedLength) {
    if (!packet || packet.schema !== expectedSchema || !Array.isArray(packet.sources) ||
        packet.sources.length !== expectedLength) return null;
    return packet.sources.filter(row => row && row.state === "SOURCE_BOUND").length;
  }

  function keylessReviewed(packet) {
    const brief = packet && packet.soulaana_evidence_brief;
    return brief && Number.isSafeInteger(brief.observation_count) && brief.observation_count >= 0
      ? brief.observation_count : null;
  }

  function catalystReviewed(packet) {
    const brief = packet && packet.soulaana;
    return brief && Number.isSafeInteger(brief.observation_count) && brief.observation_count >= 0
      ? brief.observation_count : null;
  }

  Promise.allSettled([
    fetch("/ob/research/keyless.json", {
      credentials: "same-origin", cache: "no-store",
      headers: {"Accept": "application/json"}
    }).then(r => {
      if (!r.ok) throw new Error("keyless held");
      return r.json();
    }),
    fetch("/ob/research/catalysts.json", {
      credentials: "same-origin", cache: "no-store",
      headers: {"Accept": "application/json"}
    }).then(r => {
      if (!r.ok) throw new Error("catalyst held");
      return r.json();
    }),
    fetch("/ob/engine-feed-snapshot.json", {
      credentials: "same-origin", cache: "no-store",
      headers: {"Accept": "application/json"}
    }).then(r => {
      if (!r.ok) throw new Error("market scan held");
      return r.json();
    })
  ]).then(results => {
    const keyless = results[0].status === "fulfilled" ? results[0].value : null;
    const catalysts = results[1].status === "fulfilled" ? results[1].value : null;
    const market = results[2].status === "fulfilled" ? results[2].value : null;
    const sourceCount = safeCountSources(keyless, "OB_KEYLESS_PUBLIC_CONTEXT_V1", 4);
    const catalystCount = safeCountSources(catalysts, "OB_OFFICIAL_CATALYST_RADAR_V1", 6);

    const reviewedParts = [keylessReviewed(keyless), catalystReviewed(catalysts)]
      .filter(value => value !== null);
    const reviewed = reviewedParts.length
      ? reviewedParts.reduce((sum, value) => sum + value, 0)
      : null;

    const nodes = [];
    nodes.push(sourceCount === null
      ? chip("Public sources · held", "hold")
      : chip("Public sources · " + sourceCount + "/4", sourceCount ? "good" : ""));
    nodes.push(catalystCount === null
      ? chip("Catalysts · held", "hold")
      : chip("Catalysts · " + catalystCount + "/6", catalystCount ? "good" : ""));
    nodes.push(reviewed === null
      ? chip("Soulaana · checking", "")
      : chip("Soulaana · " + reviewed + " reviewed", reviewed ? "good" : ""));
    const marketCount = market && market.market_data_state === "source_bound_research_scan" &&
      Array.isArray(market.symbols) ? market.symbols.length : null;
    nodes.push(marketCount === null
      ? chip("Alpaca scan · held", "hold")
      : chip("Alpaca scan · " + marketCount + " surfaced", marketCount ? "good" : ""));

    mount.replaceChildren(...nodes);

    const catalystLabel = document.getElementById("obCatalystLabel");
    const catalystList = document.getElementById("obCatalystList");
    if (catalystLabel) {
      const observations = catalysts && catalysts.soulaana && Array.isArray(catalysts.soulaana.observations)
        ? catalysts.soulaana.observations : [];
      catalystLabel.textContent = observations.length
        ? observations.length + " reviewed catalyst" + (observations.length === 1 ? "" : "s")
        : "No reviewed catalyst needs attention.";
      if (catalystList) {
        catalystList.replaceChildren(...observations.slice(0,3).map(item => {
          const row = document.createElement("div");
          row.className = "ob-command-line";
          const finding = Array.isArray(item.factual_findings) && item.factual_findings.length
            ? item.factual_findings[0] : item.how_to_interpret || item.source;
          row.textContent = String(item.source || "source").replaceAll("_"," ").toUpperCase() + " · " + finding;
          return row;
        }));
      }
    }

    const changedLabel = document.getElementById("obChangedLabel");
    const changedSummary = document.getElementById("obChangedSummary");
    if (changedLabel && changedSummary) {
      const timeline = catalysts && catalysts.soulaana_provenance_triage &&
        Array.isArray(catalysts.soulaana_provenance_triage.event_timeline)
        ? catalysts.soulaana_provenance_triage.event_timeline : [];
      const changed = timeline.filter(item =>
        item && item.change_since_last_verified_fetch === "CHANGED_SINCE_LAST_VERIFIED_FETCH");
      changedLabel.textContent = changed.length
        ? changed.length + " reviewed change" + (changed.length === 1 ? "" : "s")
        : "No reviewed change is demanding attention.";
      changedSummary.textContent = changed.length
        ? String(changed[0].title || "Reviewed source context changed.")
        : "Soulaana has no new source-backed change to surface.";
    }
  }).catch(() => {
    mount.replaceChildren(chip("Data status · held", "hold"));
    const catalystLabel = document.getElementById("obCatalystLabel");
    const changedLabel = document.getElementById("obChangedLabel");
    if (catalystLabel) catalystLabel.textContent = "Catalyst context held.";
    if (changedLabel) changedLabel.textContent = "Change context held.";
  });
})();
