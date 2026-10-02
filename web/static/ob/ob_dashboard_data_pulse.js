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

  function fetchJson(path) {
    return fetch(path, {
      credentials: "same-origin", cache: "no-store",
      headers: {"Accept": "application/json"}
    }).then(response => {
      const contentType = String(response.headers.get("content-type") || "").toLowerCase();
      if (response.redirected || /\/tower\/(login|access-home|launch\/observatory|step-up\/observatory)/.test(response.url)) {
        const error = new Error("tower verification required");
        error.code = "TOWER_VERIFICATION_REQUIRED";
        throw error;
      }
      if (!response.ok) throw new Error("source request held");
      if (!contentType.includes("application/json")) {
        throw new Error("source contract hold");
      }
      return response.json();
    });
  }

  Promise.allSettled([
    fetchJson("/ob/research/keyless.json"),
    fetchJson("/ob/research/catalysts.json"),
    fetchJson("/ob/engine-feed-snapshot.json")
  ]).then(results => {
    const towerVerificationRequired = results.some(result =>
      result.status === "rejected" &&
      result.reason &&
      result.reason.code === "TOWER_VERIFICATION_REQUIRED"
    );
    if (towerVerificationRequired) {
      mount.replaceChildren(
        chip("Tower verification · renew", "hold"),
        chip("Public research · paused", ""),
        chip("Catalysts · paused", ""),
        chip("Market scan · paused", "")
      );
      const catalystLabel = document.getElementById("obCatalystLabel");
      const changedLabel = document.getElementById("obChangedLabel");
      if (catalystLabel) catalystLabel.textContent =
        "Tower verification expired; catalyst context is paused.";
      if (changedLabel) changedLabel.textContent =
        "Tower verification expired; source-change context is paused.";
      return;
    }
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
      ? chip("Public research · contract hold", "hold")
      : chip("Public research · " + sourceCount + "/4", sourceCount ? "good" : ""));
    nodes.push(catalystCount === null
      ? chip("Catalysts · contract hold", "hold")
      : chip("Catalysts · " + catalystCount + "/6", catalystCount ? "good" : ""));
    nodes.push(reviewed === null
      ? chip("Soulaana · checking", "")
      : chip("Soulaana · " + reviewed + " reviewed", reviewed ? "good" : ""));
    const marketCount = market && market.market_data_state === "source_bound_research_scan" &&
      Array.isArray(market.symbols) ? market.symbols.length : null;
    nodes.push(marketCount === null
      ? chip("Market scan · contract hold", "hold")
      : chip("Market scan · " + marketCount + " surfaced", marketCount ? "good" : ""));

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
