"""Read-only, bounded SEC EDGAR transport. No broker or market-price authority.

Only three official JSON endpoints are reachable. No arbitrary URLs or redirects.
No persistent cache, no key, no browser requests. Call only after Tower's owner
gate and an explicit operator review of the public research configuration.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import re
from threading import Lock
from time import monotonic, sleep
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

CONTACT = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_\x60{|}~-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+$")
CIK = re.compile(r"^[0-9]{10}$")
SEC_TICKERS = "https://www.sec.gov/files/company_tickers_exchange.json"
SEC_API = "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"
SEC_ACCESS = "https://www.sec.gov/about/developer-resources"


class SECResearchUnavailable(RuntimeError):
    """A sanitized failure: never expose transport response or contact details."""


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class EDGARPublicClient:
    """One sequential SEC request at a time and <= 2 requests/sec per process.

    This is intentionally below SEC's published 10 requests/sec aggregate limit.
    Multiple deployed instances must use a shared throttle before activation.
    """

    def __init__(self, contact_email: str, *, opener=None, clock=monotonic,
                 sleeper=sleep, spacing_seconds: float = 0.6):
        if (not isinstance(contact_email, str) or len(contact_email) > 254
                or not CONTACT.fullmatch(contact_email)
                or contact_email.lower().endswith((".invalid", ".example", ".test"))):
            raise ValueError("A real, valid SEC public-collector contact email is required")
        if not 0.5 <= spacing_seconds <= 30:
            raise ValueError("SEC throttle must be at most two requests/sec")
        self._contact = contact_email
        self._opener = opener if opener is not None else build_opener(_NoRedirect())
        self._clock = clock
        self._sleep = sleeper
        self._spacing = spacing_seconds
        self._lock = Lock()
        self._last_request = None

    def _get_json(self, url: str, *, max_bytes: int) -> tuple[dict, datetime]:
        # Exact endpoint allowlist. Untrusted URLs and arbitrary filing URLs
        # must never reach this transport.
        parts = urlsplit(url)
        allowed = (
            url == SEC_TICKERS
            or bool(re.fullmatch(r"/submissions/CIK[0-9]{10}\.json", parts.path)
                    and parts.scheme == "https" and parts.netloc == "data.sec.gov")
            or bool(re.fullmatch(r"/api/xbrl/companyfacts/CIK[0-9]{10}\.json", parts.path)
                    and parts.scheme == "https" and parts.netloc == "data.sec.gov")
        )
        if not allowed or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError("Unapproved SEC endpoint")
        req = Request(url, headers={
            "User-Agent": "Simplee World Observatory public research (" + self._contact + ")",
            "Accept": "application/json",
            "Accept-Encoding": "identity",
        })
        with self._lock:
            now = self._clock()
            if self._last_request is not None:
                remaining = self._spacing - (now - self._last_request)
                if remaining > 0:
                    self._sleep(remaining)
            # Count failed attempts too; do not hammer SEC on 403 or 429.
            self._last_request = self._clock()
            try:
                with self._opener.open(req, timeout=10) as response:
                    if response.geturl() != url or response.status != 200:
                        raise SECResearchUnavailable("SEC_SOURCE_UNAVAILABLE")
                    kind = response.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
                    if kind not in {"application/json", "text/json", "application/octet-stream"}:
                        raise SECResearchUnavailable("SEC_UNEXPECTED_CONTENT")
                    raw = response.read(max_bytes + 1)
                    observed_at = datetime.now(timezone.utc)
            except (HTTPError, URLError, TimeoutError, OSError) as exc:
                raise SECResearchUnavailable("SEC_SOURCE_UNAVAILABLE") from None
        if len(raw) > max_bytes:
            raise SECResearchUnavailable("SEC_RESPONSE_TOO_LARGE")
        try:
            document = json.loads(raw.decode("utf-8"))
        except (UnicodeError, ValueError):
            raise SECResearchUnavailable("SEC_INVALID_JSON") from None
        if not isinstance(document, dict):
            raise SECResearchUnavailable("SEC_INVALID_DOCUMENT")
        return document, observed_at

    def ticker_directory(self) -> tuple[dict, datetime]:
        return self._get_json(SEC_TICKERS, max_bytes=12_000_000)

    def submissions(self, cik: str) -> tuple[dict, datetime]:
        if not isinstance(cik, str) or not CIK.fullmatch(cik):
            raise ValueError("Exact zero-padded CIK required")
        return self._get_json(f"https://data.sec.gov/submissions/CIK{cik}.json",
                              max_bytes=20_000_000)

    def companyfacts(self, cik: str) -> tuple[dict, datetime]:
        if not isinstance(cik, str) or not CIK.fullmatch(cik):
            raise ValueError("Exact zero-padded CIK required")
        return self._get_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
                              max_bytes=40_000_000)
