"""Shared secret-safe provider/plugin verification diagnostics for The Observatory.

Provider adapters may classify a failure, but they must never return raw provider
bodies, raw exception text, credential-bearing URLs, secrets, account identifiers,
or arbitrary upstream strings to browser-visible status surfaces.

This vocabulary is deliberately transport-agnostic so REST, WebSocket, MQTT,
streaming HTTP and broker/provider plugins can use the same owner-facing contract.
"""
from __future__ import annotations

SAFE_PROBE_CODES = frozenset({
    "NOT_CONFIGURED",
    "NOT_TESTED",
    "READ_ONLY_CHECK_PASSED",
    "RATE_LIMITED",
    "ACCESS_REJECTED",
    "REQUEST_REJECTED",
    "PROVIDER_UNAVAILABLE",
    "NETWORK_HOLD",
    "REDIRECT_HOLD",
    "RESPONSE_TOO_LARGE",
    "RESPONSE_PARSE_HOLD",
    "RESPONSE_SHAPE_HOLD",
    "PROVIDER_MESSAGE",
})

SAFE_PROBE_MESSAGES = {
    "NOT_CONFIGURED": "No credential is connected for this provider.",
    "NOT_TESTED": "Credential is present but has not been verified yet.",
    "READ_ONLY_CHECK_PASSED": (
        "Read-only credential check passed. This verifies access only; it does not "
        "prove market-data, commercial, display, AI, retention, or trading rights."
    ),
    "RATE_LIMITED": (
        "The provider reported a request/rate limit. The credential may still be valid; "
        "wait for the provider limit window before testing again."
    ),
    "ACCESS_REJECTED": (
        "The provider rejected access. Check the credential, account activation, "
        "subscription, product entitlement, or provider-side permissions."
    ),
    "REQUEST_REJECTED": (
        "The provider rejected the fixed verification request. No alternate endpoint "
        "was attempted automatically."
    ),
    "PROVIDER_UNAVAILABLE": (
        "The provider returned a server-side failure. This looks like an upstream "
        "availability problem rather than proof that the credential is invalid."
    ),
    "NETWORK_HOLD": (
        "Tower could not complete the provider connection. The credential was not "
        "declared invalid; retry after the network/provider path is healthy."
    ),
    "REDIRECT_HOLD": (
        "The provider attempted an unexpected redirect, so Tower stopped verification "
        "rather than forwarding a credential to another location."
    ),
    "RESPONSE_TOO_LARGE": (
        "The provider response exceeded the verification safety limit and was rejected."
    ),
    "RESPONSE_PARSE_HOLD": (
        "The provider returned a response Tower could not safely parse as the expected format."
    ),
    "RESPONSE_SHAPE_HOLD": (
        "The provider answered, but the response did not match the expected verification schema."
    ),
    "PROVIDER_MESSAGE": (
        "The provider returned a bounded status/message instead of the expected data. "
        "No raw provider text is displayed or logged."
    ),
}


def normalize_probe_code(code: object) -> str:
    """Accept only the fixed diagnostic vocabulary; never surface arbitrary strings."""
    return code if isinstance(code, str) and code in SAFE_PROBE_CODES else "PROVIDER_MESSAGE"


def probe_message(code: object) -> str:
    return SAFE_PROBE_MESSAGES[normalize_probe_code(code)]


def classify_http_status(status: object) -> str:
    """Classify an HTTP status without reading or surfacing provider response text."""
    try:
        value = int(status)
    except (TypeError, ValueError):
        return "REQUEST_REJECTED"
    if value == 429:
        return "RATE_LIMITED"
    if value in {401, 403}:
        return "ACCESS_REJECTED"
    if 500 <= value <= 599:
        return "PROVIDER_UNAVAILABLE"
    return "REQUEST_REJECTED"


def classify_provider_message(message: object) -> str:
    """Classify a provider message while discarding the message itself.

    This helper only uses generic indicator words. The caller must not persist,
    render, log, or re-raise the original provider text.
    """
    if not isinstance(message, str):
        return "PROVIDER_MESSAGE"
    lowered = message.lower()
    rate_markers = (
        "rate limit", "call frequency", "calls per", "requests per", "request limit",
        "too many requests", "quota", "25 requests", "per day", "per minute",
    )
    if any(marker in lowered for marker in rate_markers):
        return "RATE_LIMITED"
    access_markers = (
        "api key", "apikey", "token", "unauthorized", "forbidden", "authentication",
        "entitlement", "subscription", "premium", "permission", "access denied",
    )
    if any(marker in lowered for marker in access_markers):
        return "ACCESS_REJECTED"
    return "PROVIDER_MESSAGE"
