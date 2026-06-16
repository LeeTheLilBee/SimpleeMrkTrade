// OBSERVATORY_V20_NOTIFICATIONS_SETTINGS_DRAWERS_JS

(function () {
  const SETTINGS_KEY = "ob.v20.settings";
  const READ_KEY = "ob.v20.readNotifications";

  const defaultSettings = {
    themeVariant: "cosmic",
    starGlow: "normal",
    motion: "full",
    soulaanaIntensity: "auntie",
    missionLayout: "full"
  };

  const notifications = [
    {
      id: "manual-live-mu",
      title: "Manual Live candidate ready",
      body: "MU CALL · Moderate risk · Review Trade Center before any broker action.",
      time: "Now",
      type: "manual",
      href: "/ob/trade-center"
    },
    {
      id: "sector-crowding",
      title: "Sector crowding watch",
      body: "Semiconductors are bright, but OB wants correlation and repeat-risk visible before escalation.",
      time: "Recent",
      type: "risk",
      href: "/ob/market-map"
    },
    {
      id: "review-receipt",
      title: "Review receipt pending",
      body: "Manual Live and review records should be classified as official, test, private proof, or quarantined.",
      time: "Today",
      type: "review",
      href: "/ob/review-center"
    },
    {
      id: "tower-boundary",
      title: "Tower boundary reminder",
      body: "Live Automated remains locked. OB can explain, prepare, and record. Owner places manually at broker.",
      time: "Always",
      type: "tower",
      href: "/ob/owner-console"
    }
  ];

  function loadSettings() {
    try {
      return { ...defaultSettings, ...JSON.parse(localStorage.getItem(SETTINGS_KEY) || "{}") };
    } catch (error) {
      return { ...defaultSettings };
    }
  }

  function saveSettings(settings) {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    applySettings(settings);
  }

  function loadRead() {
    try {
      return JSON.parse(localStorage.getItem(READ_KEY) || "[]");
    } catch (error) {
      return [];
    }
  }

  function saveRead(readIds) {
    localStorage.setItem(READ_KEY, JSON.stringify(Array.from(new Set(readIds))));
    updateNotificationBadges();
  }

  function unreadCount() {
    const read = loadRead();
    return notifications.filter(item => !read.includes(item.id)).length;
  }

  function applySettings(settings) {
    document.body.setAttribute("data-ob-theme-variant", settings.themeVariant);
    document.body.setAttribute("data-ob-star-glow", settings.starGlow);
    document.body.setAttribute("data-ob-motion", settings.motion);
    document.body.setAttribute("data-ob-soulaana-intensity", settings.soulaanaIntensity);
    document.body.setAttribute("data-ob-mission-layout", settings.missionLayout);
  }

  function closeDrawer() {
    const existing = document.getElementById("obAppDrawerBackdrop");
    if (existing) existing.remove();
  }

  function drawerShell(title, subtitle, body) {
    closeDrawer();

    const backdrop = document.createElement("div");
    backdrop.id = "obAppDrawerBackdrop";
    backdrop.className = "ob-drawer-backdrop open";

    const drawer = document.createElement("div");
    drawer.className = "ob-app-drawer";

    drawer.innerHTML = `
      <div class="ob-app-drawer-head">
        <div>
          <strong>${title}</strong>
          <span>${subtitle}</span>
        </div>
        <button class="ob-app-drawer-close" id="obAppDrawerClose">×</button>
      </div>

      ${body}
    `;

    backdrop.appendChild(drawer);
    document.body.appendChild(backdrop);

    document.getElementById("obAppDrawerClose").addEventListener("click", closeDrawer);
    backdrop.addEventListener("click", function (event) {
      if (event.target === backdrop) closeDrawer();
    });
  }

  function openNotificationsDrawer() {
    const read = loadRead();

    const body = `
      <div class="ob-drawer-section gold">
        <span>Soulaana</span>
        <strong>Notifications are here to send you back to review, not to rush you into action. If it matters, open the room and read the full context.</strong>
      </div>

      <div class="ob-notification-list" style="margin-top: 12px;">
        ${notifications.map(item => {
          const isUnread = !read.includes(item.id);
          return `
            <div class="ob-notification-card ${isUnread ? "unread" : ""}">
              <div class="ob-notification-top">
                <div class="ob-notification-title">${item.title}</div>
                <div class="ob-notification-time">${item.time}</div>
              </div>

              <div class="ob-notification-body">${item.body}</div>

              <div class="ob-notification-actions">
                <button class="ob-drawer-button" data-notification-open="${item.href}" data-notification-read="${item.id}">
                  Open room
                </button>
                <button class="ob-drawer-button aqua" data-notification-read="${item.id}">
                  Mark read
                </button>
              </div>
            </div>
          `;
        }).join("")}
      </div>

      <div class="ob-notification-actions" style="margin-top: 12px;">
        <button class="ob-drawer-button" id="obMarkAllNotificationsRead">Mark all read</button>
        <button class="ob-drawer-button aqua" id="obOpenTradeCenterFromNotifications">Open Trade Center</button>
        <button class="ob-drawer-button red" id="obCloseNotifications">Close</button>
      </div>
    `;

    drawerShell("Notifications", "Short, safe alerts. Full context lives inside the protected OB rooms.", body);

    document.querySelectorAll("[data-notification-read]").forEach(button => {
      button.addEventListener("click", function () {
        const id = this.getAttribute("data-notification-read");
        saveRead([...loadRead(), id]);

        const openHref = this.getAttribute("data-notification-open");
        if (openHref) {
          window.location.href = openHref;
        } else {
          openNotificationsDrawer();
        }
      });
    });

    const markAll = document.getElementById("obMarkAllNotificationsRead");
    if (markAll) {
      markAll.addEventListener("click", function () {
        saveRead(notifications.map(item => item.id));
        openNotificationsDrawer();
      });
    }

    const openTrade = document.getElementById("obOpenTradeCenterFromNotifications");
    if (openTrade) {
      openTrade.addEventListener("click", function () {
        window.location.href = "/ob/trade-center";
      });
    }

    const close = document.getElementById("obCloseNotifications");
    if (close) {
      close.addEventListener("click", closeDrawer);
    }
  }

  function settingSelect(id, label, value, options) {
    return `
      <div class="ob-setting-card">
        <label for="${id}">${label}</label>
        <select id="${id}">
          ${options.map(option => `
            <option value="${option.value}" ${option.value === value ? "selected" : ""}>${option.label}</option>
          `).join("")}
        </select>
      </div>
    `;
  }

  function openSettingsDrawer() {
    const settings = loadSettings();

    const body = `
      <div class="ob-drawer-section gold">
        <span>Settings</span>
        <strong>These preferences affect the OB visual layer only. Tower still owns access, identity, billing, permissions, and locks.</strong>
      </div>

      <div class="ob-settings-grid" style="margin-top: 12px;">
        ${settingSelect("obSettingTheme", "Theme feel", settings.themeVariant, [
          { value: "cosmic", label: "Cosmic default" },
          { value: "quiet", label: "Quiet dark" },
          { value: "high_contrast", label: "High contrast glass" }
        ])}

        ${settingSelect("obSettingGlow", "Star glow", settings.starGlow, [
          { value: "calm", label: "Calm glow" },
          { value: "normal", label: "Normal glow" },
          { value: "bright", label: "Bright star glow" }
        ])}

        ${settingSelect("obSettingMotion", "Motion", settings.motion, [
          { value: "full", label: "Full motion" },
          { value: "reduced", label: "Reduced motion" }
        ])}

        ${settingSelect("obSettingSoulaana", "Soulaana intensity", settings.soulaanaIntensity, [
          { value: "clear", label: "Clear and simple" },
          { value: "auntie", label: "Auntie guidance" },
          { value: "strict", label: "Strict auntie" }
        ])}

        ${settingSelect("obSettingMissionLayout", "Mission bar", settings.missionLayout, [
          { value: "full", label: "Full mission context" },
          { value: "compact", label: "Compact mission context" }
        ])}
      </div>

      <div class="ob-settings-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        Change the room lighting if you need to, but do not change the rules. Pretty is not permission. The Tower still holds the lock.
      </div>

      <div class="ob-notification-actions" style="margin-top: 12px;">
        <button class="ob-drawer-button" id="obSaveSettings">Save settings</button>
        <button class="ob-drawer-button aqua" id="obResetSettings">Reset defaults</button>
        <button class="ob-drawer-button red" id="obCloseSettings">Close</button>
      </div>
    `;

    drawerShell("Settings", "Theme, star glow, motion, Soulaana intensity, and mission display options.", body);

    const save = document.getElementById("obSaveSettings");
    if (save) {
      save.addEventListener("click", function () {
        const next = {
          themeVariant: document.getElementById("obSettingTheme").value,
          starGlow: document.getElementById("obSettingGlow").value,
          motion: document.getElementById("obSettingMotion").value,
          soulaanaIntensity: document.getElementById("obSettingSoulaana").value,
          missionLayout: document.getElementById("obSettingMissionLayout").value
        };

        saveSettings(next);
        openSettingsDrawer();
      });
    }

    const reset = document.getElementById("obResetSettings");
    if (reset) {
      reset.addEventListener("click", function () {
        saveSettings({ ...defaultSettings });
        openSettingsDrawer();
      });
    }

    const close = document.getElementById("obCloseSettings");
    if (close) {
      close.addEventListener("click", closeDrawer);
    }
  }

  function updateNotificationBadges() {
    const count = unreadCount();
    document.querySelectorAll("[data-ob-notifications-trigger]").forEach(button => {
      const label = count > 0 ? `Notifications <span class="ob-notify-badge">${count}</span>` : "Notifications";
      button.innerHTML = label;
    });
  }

  function wireRouteChips() {
    document.querySelectorAll(".ob-route-chip").forEach(chip => {
      const text = chip.textContent.trim().toLowerCase();

      if (text.includes("settings")) {
        chip.classList.add("clickable");
        chip.setAttribute("data-ob-settings-trigger", "true");
        chip.onclick = openSettingsDrawer;
      }

      if (text.includes("notifications")) {
        chip.classList.add("clickable");
        chip.setAttribute("data-ob-notifications-trigger", "true");
        chip.onclick = openNotificationsDrawer;
      }
    });

    updateNotificationBadges();
  }

  function buildFloatButtons() {
    if (document.getElementById("obNotifyFloat")) return;

    const wrap = document.createElement("div");
    wrap.id = "obNotifyFloat";
    wrap.className = "ob-notify-float";

    wrap.innerHTML = `
      <button class="ob-notify-float-button" data-ob-notifications-trigger="true">Notifications</button>
      <button class="ob-notify-float-button" data-ob-settings-trigger="true">Settings</button>
    `;

    document.body.appendChild(wrap);

    wrap.querySelector("[data-ob-notifications-trigger]").addEventListener("click", openNotificationsDrawer);
    wrap.querySelector("[data-ob-settings-trigger]").addEventListener("click", openSettingsDrawer);
  }

  function boot() {
    applySettings(loadSettings());

    setTimeout(function () {
      wireRouteChips();
      buildFloatButtons();
      updateNotificationBadges();
    }, 90);
  }

  document.addEventListener("DOMContentLoaded", boot);

  window.OB_NOTIFICATIONS_SETTINGS_V20 = {
    notifications,
    loadSettings,
    saveSettings,
    openNotificationsDrawer,
    openSettingsDrawer,
    unreadCount
  };
})();
