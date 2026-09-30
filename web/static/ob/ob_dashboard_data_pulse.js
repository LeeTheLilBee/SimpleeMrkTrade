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
    })
  ]).then(results => {
    const keyless = results[0].status === "fulfilled" ? results[0].value : null;
    const catalysts = results[1].status === "fulfilled" ? results[1].value : null;
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

    mount.replaceChildren(...nodes);
  }).catch(() => {
    mount.replaceChildren(chip("Data status · held", "hold"));
  });
})();
