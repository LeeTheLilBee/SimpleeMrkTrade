/* OBSIM046–050: browser controls for protected Tower-hosted SYNTHETIC rehearsal ONLY. */
(() => {
  "use strict";
  const root = document.getElementById("localRehearsalMount");
  if (!root || root.dataset.obCsrf === undefined) return;
  // A new hosted rehearsal is a new authorization boundary. The server
  // rotates this per-workspace token and returns the successor ONLY on the
  // explicitly authorized /new mutation; never store it persistently.
  let token = root.dataset.obCsrf;
  const $ = (id) => document.getElementById(id);
  const controls = ["refresh", "sample", "tick", "pause", "resume", "stop", "new", "evidence"];
  let busy = false;
  let last = null;
  let connected = false;

  function say(message) { $("feedback").textContent = message; }
  function metric(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number.toLocaleString(undefined, { maximumFractionDigits: 2 }) : "—";
  }
  async function api(path, method = "GET", payload = null) {
    const options = {
      method,
      credentials: "same-origin",
      cache: "no-store",
      headers: { "X-OB-Rehearsal-Token": token, "Accept": "application/json" }
    };
    if (method !== "GET") {
      options.headers["Content-Type"] = "application/json";
      options.body = JSON.stringify(payload === null ? {} : payload);
    }
    const response = await fetch(path, options);
    const result = await response.json();
    if (!response.ok) throw new Error(result && result.status ? String(result.status) : "Local endpoint unavailable");
    return result;
  }
  function renderLanes(lanes) {
    const mount = $("laneCards");
    mount.replaceChildren();
    ["CONTROL", "INTEGRATED", "EXPERIMENTAL"].forEach((key) => {
      const card = document.createElement("article");
      card.className = "lane";
      const head = document.createElement("h3");
      head.textContent = key.charAt(0) + key.slice(1).toLowerCase();
      card.appendChild(head);
      const info = lanes && typeof lanes === "object" ? lanes[key] : null;
      if (!info) {
        const p = document.createElement("p");
        p.textContent = "No accepted simulated report yet.";
        card.appendChild(p);
      } else {
        [["Equity", info.equity], ["Cash", info.cash], ["Realized P&L", info.realized_pnl], ["Unrealized P&L", info.unrealized_pnl], ["Trades", info.trades]].forEach(([label, value]) => {
          const p = document.createElement("p");
          const strong = document.createElement("strong");
          strong.textContent = metric(value);
          p.append(document.createTextNode(label + ": "), strong);
          card.appendChild(p);
        });
      }
      mount.appendChild(card);
    });
  }
  function render(data) {
    last = data;
    connected = true;
    $("sessionState").textContent = data.state || "Guarded";
    $("tickCount").textContent = metric(data.accepted_ticks);
    $("sourceKind").textContent = data.declared_source_kind || "Unverified";
    const due = data.due || {};
    $("dueStatus").textContent = due.state === "WAIT_INTERVAL" ?
      Math.max(0, Math.ceil(Number(due.due_in_seconds) || 0)) + "s remaining" :
      due.state === "READY_FOR_EXPLICIT_INPUT" ? "Ready for input" : (due.state || "Unavailable");
    $("lastHash").textContent = data.last_report_hash || "No report";
    renderLanes(data.last_lanes);
    updateControls();
  }
  function updateControls() {
    const state = last && last.state;
    const due = last && last.due && last.due.state;
    const active = connected && !busy;
    $("tick").disabled = !active || state !== "RUNNING" || due !== "READY_FOR_EXPLICIT_INPUT";
    $("pause").disabled = !active || state !== "RUNNING";
    $("resume").disabled = !active || state !== "PAUSED";
    $("stop").disabled = !active || state === "STOPPED";
    $("refresh").disabled = busy;
    $("sample").disabled = busy;
    $("new").disabled = !active || state !== "STOPPED";
    $("evidence").disabled = !active || state !== "STOPPED";
  }
  async function refresh() {
    if (busy) return;
    try { render(await api("/ob/owner-rehearsal/status.json")); }
    catch (_) {
      connected = false;
      updateControls();
      say("Protected status unavailable or session expired. Re-enter from Tower; prior volatile reports may no longer exist.");
    }
  }
  async function mutate(path, payload, success) {
    if (busy) return;
    busy = true;
    updateControls();
    try {
      const result = await api(path, "POST", payload);
      if (path === "/ob/owner-rehearsal/new.json") {
        if (
          !result
          || result.previous_token_revoked !== true
          || typeof result.new_rehearsal_token !== "string"
          || result.new_rehearsal_token.length < 32
          || result.new_rehearsal_token === token
        ) {
          // Do not keep using an old token against a potentially new workspace.
          connected = false;
          throw new Error("Session token rotation not confirmed; re-enter from Tower");
        }
        token = result.new_rehearsal_token;
        root.dataset.obCsrf = token;
      }
      render(result);
      say(success(result));
    } catch (error) {
      say("Request not confirmed (" + error.message + "). Refresh protected status before retrying; the volatile session may have been lost.");
    } finally {
      busy = false;
      await refresh();
      updateControls();
    }
  }

  $("refresh").addEventListener("click", refresh);
  $("sample").addEventListener("click", async () => {
    if (busy) return;
    try {
      const sample = await api("/ob/owner-rehearsal/sample.json");
      $("inputJson").value = JSON.stringify(sample, null, 2);
      say("Synthetic fixture loaded for review. The marks and 10,000 units are fictional; adjust source kind and unique IDs for any later manually authored input.");
    } catch (_) { say("Synthetic sample unavailable. No simulation report has been submitted."); }
  });
  $("tick").addEventListener("click", async () => {
    let data;
    try {
      data = JSON.parse($("inputJson").value);
      if (!data || typeof data !== "object" || Array.isArray(data)) throw new Error("object");
    } catch (_) { say("Enter one complete owner-authored JSON object before submitting."); return; }
    await mutate("/ob/owner-rehearsal/tick.json", data, (result) =>
      "One simulated report accepted: " + result.accepted_ticks +
      ". Historical/synthetic only; no broker order or live account permission."
    );
  });
  $("pause").addEventListener("click", () => mutate("/ob/owner-rehearsal/pause.json", {}, () =>
    "Paused. No missing 30-second reports will be backfilled."
  ));
  $("resume").addEventListener("click", () => mutate("/ob/owner-rehearsal/resume.json", {}, () =>
    "Resumed. A fresh 30-second interval is required before explicit input."
  ));
  $("stop").addEventListener("click", () => mutate("/ob/owner-rehearsal/stop.json", {}, (result) =>
    "Sealed " + result.archive_tick_count + " report(s) as " + result.archive_state +
    ". Report-only recovery never restores a trading session."
  ));
  $("evidence").addEventListener("click", async () => {
    if (busy || !connected || !last || last.state !== "STOPPED") return;
    busy = true;
    updateControls();
    try {
      const packet = await api("/ob/owner-rehearsal/evidence.json");
      if (
        packet.schema_version !== "OBSIM_OWNER_EPHEMERAL_FINAL_EVIDENCE_V1"
        || packet.report_state !== "OWNER_DOWNLOADED_FINALIZED_REPORT_ONLY"
        || packet.source_kind !== "SYNTHETIC"
        || packet.durable_server_archive !== false
        || packet.manual_live_authorized !== false
        || !Array.isArray(packet.reports)
        || typeof packet.packet_hash !== "string"
      ) throw new Error("Final report envelope rejected");
      const blob = new Blob([JSON.stringify(packet, null, 2)], {
        type: "application/json"
      });
      const localUrl = URL.createObjectURL(blob);
      try {
        const link = document.createElement("a");
        const safeId = String(packet.session_id || "session").replace(/[^a-zA-Z0-9-]/g, "");
        link.href = localUrl;
        link.download = "ob-proof-demo-" + safeId + ".json";
        document.body.appendChild(link);
        link.click();
        link.remove();
        say("Owner report-only packet prepared for local download. Verify your device saved it before resetting: volatile server reports will disappear. This is not broker/Tower attestation.");
      } finally {
        URL.revokeObjectURL(localUrl);
      }
    } catch (error) {
      say("Final evidence export was NOT confirmed (" + error.message + "). Keep this volatile rehearsal open and check its status.");
    } finally {
      busy = false;
      await refresh();
      updateControls();
    }
  });
  $("new").addEventListener("click", () => mutate("/ob/owner-rehearsal/new.json", {}, () =>
    "New owner-started SYNTHETIC session. The previous finalized volatile report is no longer retained; save finalized evidence first."
  ));
  refresh();
  // A countdown display is NOT an unattended report, source poll or tick.
  setInterval(() => {
    if (document.visibilityState === "visible" && !busy) refresh();
  }, 5000);
})();
