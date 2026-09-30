"""Shared provider diagnostic contract: useful owner states without secret leakage."""
import pytest

from tower.ob_provider_diagnostics import (
    SAFE_PROBE_CODES,
    classify_http_status,
    classify_provider_message,
    normalize_probe_code,
    probe_message,
)


def test_safe_vocabulary_has_owner_actionable_states():
    expected = {
        "NOT_CONFIGURED", "NOT_TESTED", "READ_ONLY_CHECK_PASSED",
        "RATE_LIMITED", "ACCESS_REJECTED", "REQUEST_REJECTED",
        "PROVIDER_UNAVAILABLE", "NETWORK_HOLD", "REDIRECT_HOLD",
        "RESPONSE_TOO_LARGE", "RESPONSE_PARSE_HOLD",
        "RESPONSE_SHAPE_HOLD", "PROVIDER_MESSAGE",
    }
    assert SAFE_PROBE_CODES == expected
    for code in expected:
        assert isinstance(probe_message(code), str)
        assert len(probe_message(code)) >= 20


@pytest.mark.parametrize("status, expected", [
    (401, "ACCESS_REJECTED"),
    (403, "ACCESS_REJECTED"),
    (429, "RATE_LIMITED"),
    (500, "PROVIDER_UNAVAILABLE"),
    (503, "PROVIDER_UNAVAILABLE"),
    (400, "REQUEST_REJECTED"),
    (418, "REQUEST_REJECTED"),
])
def test_http_status_classification(status, expected):
    assert classify_http_status(status) == expected


@pytest.mark.parametrize("message, expected", [
    ("Thank you for using Alpha Vantage. Our standard API rate limit is 25 requests per day.", "RATE_LIMITED"),
    ("Too many requests", "RATE_LIMITED"),
    ("Invalid API key", "ACCESS_REJECTED"),
    ("Premium endpoint requires subscription", "ACCESS_REJECTED"),
    ("Permission denied for this token", "ACCESS_REJECTED"),
    ("Scheduled maintenance", "PROVIDER_MESSAGE"),
    (None, "PROVIDER_MESSAGE"),
])
def test_provider_message_is_classified_then_discarded(message, expected):
    assert classify_provider_message(message) == expected


def test_arbitrary_upstream_text_can_never_become_browser_status():
    raw = "upstream-secret=DO_NOT_RENDER account=12345 https://provider.example?apikey=secret"
    assert normalize_probe_code(raw) == "PROVIDER_MESSAGE"
    safe = probe_message(raw)
    assert "DO_NOT_RENDER" not in safe
    assert "12345" not in safe
    assert "apikey" not in safe
