
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def build_private_outer_shell(
    *,
    reason_code: str = "observatory_private",
    message: str = "The Observatory is private.",
    path: str = "/",
    status_code: int = 403,
    show_waitlist_hint: bool = False,
) -> Tuple[str, int]:
    safe_reason = _safe_str(reason_code, "observatory_private")
    safe_message = _safe_str(message, "The Observatory is private.")
    safe_path = _safe_str(path, "/")
    hint = ""
    if show_waitlist_hint:
        hint = "<p class='hint'>Access is invitation-only. Approved users enter through cleared Tower corridors.</p>"

    html = f"""
    <!doctype html>
    <html lang='en'>
    <head>
      <meta charset='utf-8'>
      <meta name='viewport' content='width=device-width, initial-scale=1'>
      <title>The Observatory</title>
      <style>
        :root {{ color-scheme: dark; }}
        body {{
          margin: 0;
          min-height: 100vh;
          display: grid;
          place-items: center;
          background:
            radial-gradient(circle at 20% 10%, rgba(129, 140, 248, .18), transparent 34%),
            radial-gradient(circle at 80% 20%, rgba(250, 204, 21, .11), transparent 30%),
            linear-gradient(145deg, #02030a, #080b1f 45%, #030712);
          color: #f8fafc;
          font-family: Arial, sans-serif;
        }}
        .shell {{
          width: min(780px, calc(100vw - 34px));
          border: 1px solid rgba(255,255,255,.16);
          border-radius: 28px;
          padding: 32px;
          background: rgba(8, 13, 31, .78);
          box-shadow: 0 28px 90px rgba(0,0,0,.48);
          backdrop-filter: blur(18px);
        }}
        .kicker {{
          color: #facc15;
          font-size: .78rem;
          letter-spacing: .2em;
          text-transform: uppercase;
          font-weight: 900;
        }}
        h1 {{
          margin: .65rem 0 1rem;
          font-size: clamp(2rem, 6vw, 4rem);
          line-height: .92;
        }}
        p {{
          color: #dbeafe;
          line-height: 1.58;
          font-size: 1rem;
        }}
        .panel {{
          margin-top: 22px;
          border-radius: 20px;
          padding: 16px;
          background: rgba(255,255,255,.07);
          border: 1px solid rgba(255,255,255,.12);
        }}
        .code {{
          display: inline-block;
          margin-top: 8px;
          color: #bae6fd;
          font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
          font-size: .86rem;
        }}
        .hint {{
          color: #fef3c7;
        }}
      </style>
    </head>
    <body>
      <main class='shell'>
        <div class='kicker'>THE OBSERVATORY</div>
        <h1>Private sky. Locked door.</h1>
        <p>Soulaana: The real system does not live in public. If you are meant to enter, The Tower will clear your corridor.</p>
        <div class='panel'>
          <strong>{safe_reason}</strong>
          <p>{safe_message}</p>
          <span class='code'>{safe_path}</span>
        </div>
        {hint}
      </main>
    </body>
    </html>
    """
    return html, int(status_code)


def build_no_access_payload(path: str = "/") -> Dict[str, Any]:
    return {
        "ok": True,
        "status": "locked",
        "reason_code": "observatory_private_outer_shell",
        "path": _safe_str(path, "/"),
        "generated_at": _utc_now(),
        "human_reason": "The Observatory public surface is only a harmless locked shell.",
        "soulaana_translation": "Soulaana: No clearance, no corridor. The real Observatory stays behind The Tower.",
    }
