// OBSERVATORY_V20_NOTIFICATIONS_SETTINGS_DRAWERS_JS

(function () {
  const SETTINGS_KEY = "ob.v20.settings";
  const READ_KEY = "ob.beta.x111.read.v1";



  const defaultSettings = {
    themeVariant: "cosmic",
    starGlow: "normal",
    motion: "full",
    soulaanaIntensity: "auntie"
  };

  // All historical V20 demo notifications are retired. Read only the new canonical
  // beta intelligence projection, or show the genuinely empty state.
  let notifications = [];
  function refreshNotifications() {
    const api = window.OBBetaExperience;
    const rows = api && typeof api.alertRows === "function" ? api.alertRows() : [];
    notifications = rows.map(item => ({
      id: item.id, title: item.title, body: item.detail,
      time: item.as_of, type: item.kind, href: item.href,
      dismissible: item.dismissible
    }));
    return notifications;
  }

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
      return JSON.parse(sessionStorage.getItem(READ_KEY) || "[]");
    } catch (error) {
      return [];
    }
  }

  function saveRead(readIds) {
    sessionStorage.setItem(READ_KEY, JSON.stringify(Array.from(new Set(readIds)).filter(id => !String(id).startsWith("source:"))));
    updateNotificationBadges();
  }

  function unreadCount() {
    const read = loadRead();
    return refreshNotifications().filter(item => !item.dismissible || !read.includes(item.id)).length;
  }

  function applySettings(settings) {
    document.body.setAttribute("data-ob-theme-variant", settings.themeVariant);
    document.body.setAttribute("data-ob-star-glow", settings.starGlow);
    document.body.setAttribute("data-ob-motion", settings.motion);
    document.body.setAttribute("data-ob-soulaana-intensity", settings.soulaanaIntensity);

    /*
      Legacy mission-layout state is retired everywhere.
      Owner Capital Lanes use their own owner-only context.
    */
    document.body.removeAttribute(
      "data-ob-mission-layout"
    );
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
    refreshNotifications();
    const read = loadRead();

    const body = `
      <div class="ob-drawer-section gold">
        <span>Soulaana</span>
        <strong>Notifications are here to send you back to review, not to rush you into action. If it matters, open the room and read the full context.</strong>
      </div>

      <div class="ob-notification-list" style="margin-top: 12px;">
        ${notifications.length ? notifications.map(item => {
          const isUnread = !item.dismissible || !read.includes(item.id);
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
                ${item.dismissible ? '<button class="ob-drawer-button aqua" data-notification-read="' + item.id + '">Acknowledge</button>' : '<span>Safety hold · cannot dismiss</span>'}
              </div>
            </div>
          `;
        }).join("") : '<div class="ob-notification-card"><strong>No verified alerts right now.</strong><p>Previous demonstration tickers and placeholder candidates are retired.</p></div>'}
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
        if (!String(id).startsWith("source:")) saveRead([...loadRead(), id]);

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
        saveRead(notifications.filter(item => item.dismissible).map(item => item.id));
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
        <strong>
          These preferences affect the OB visual layer only.
          Tower still owns access, identity, permissions, and locks.
        </strong>
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

        ${settingSelect(
          "obSettingSoulaana",
          "Soulaana intensity",
          settings.soulaanaIntensity,
          [
            { value: "clear", label: "Clear and simple" },
            { value: "auntie", label: "Auntie guidance" },
            { value: "strict", label: "Strict auntie" }
          ]
        )}
      </div>

      <div class="ob-settings-note">
        <strong style="color: var(--ob-gold);">Soulaana:</strong><br>
        Change the room lighting if you need to.
        Appearance never changes permission.
      </div>

      <div class="ob-notification-actions" style="margin-top: 12px;">
        <button class="ob-drawer-button" id="obSaveSettings">
          Save settings
        </button>

        <button class="ob-drawer-button aqua" id="obResetSettings">
          Reset defaults
        </button>

        <button class="ob-drawer-button red" id="obCloseSettings">
          Close
        </button>
      </div>
    `;

    drawerShell(
      "Settings",
      "Theme, star glow, motion, and Soulaana intensity.",
      body
    );

    const save =
      document.getElementById(
        "obSaveSettings"
      );

    if (save) {
      save.addEventListener(
        "click",
        function () {
          const next = {
            themeVariant:
              document.getElementById(
                "obSettingTheme"
              ).value,

            starGlow:
              document.getElementById(
                "obSettingGlow"
              ).value,

            motion:
              document.getElementById(
                "obSettingMotion"
              ).value,

            soulaanaIntensity:
              document.getElementById(
                "obSettingSoulaana"
              ).value
          };

          saveSettings(next);
          openSettingsDrawer();
        }
      );
    }

    const reset =
      document.getElementById(
        "obResetSettings"
      );

    if (reset) {
      reset.addEventListener(
        "click",
        function () {
          saveSettings({
            ...defaultSettings
          });

          openSettingsDrawer();
        }
      );
    }

    const close =
      document.getElementById(
        "obCloseSettings"
      );

    if (close) {
      close.addEventListener(
        "click",
        closeDrawer
      );
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
    if (document.getElementById("obNotifyFloat") || window.OBBetaExperience) return;

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
    get notifications() { return refreshNotifications(); },
    loadSettings,
    saveSettings,
    openNotificationsDrawer,
    openSettingsDrawer,
    unreadCount
  };
})();
