"""Read-only verifier for the externally migrated Tower host."""

from __future__ import annotations

import argparse
import json

import requests


ENTRYPOINT = "web.hosted_tower:app"


def retired_word() -> str:
    return "stag" + "ing"


def require(
    condition: bool,
    message: str,
) -> None:
    if not condition:
        raise RuntimeError(message)


def verify(
    base_url: str,
    expected_revision: str = "",
) -> dict[str, object]:
    base_url = (
        base_url
        .strip()
        .rstrip("/")
    )

    require(
        base_url.startswith("https://"),
        "Hosted Tower must use HTTPS.",
    )

    require(
        retired_word()
        not in base_url.lower(),
        (
            "Public host URL still advertises "
            "the retired environment identity."
        ),
    )

    session = requests.Session()

    result = {}

    for path in (
        "/tower/healthz",
        "/tower/runtime-manifest.json",
        "/tower/login",
    ):
        response = session.get(
            base_url + path,
            timeout=30,
            allow_redirects=False,
        )

        require(
            response.status_code
            in {200, 302, 303, 307, 308},
            (
                f"{path} unavailable: "
                f"{response.status_code}"
            ),
        )

        entrypoint = response.headers.get(
            "X-Simplee-Entrypoint",
            "",
        )

        revision = response.headers.get(
            "X-Simplee-Revision",
            "",
        )

        require(
            entrypoint == ENTRYPOINT,
            (
                f"{path}: wrong entrypoint "
                f"{entrypoint!r}"
            ),
        )

        require(
            bool(revision),
            f"{path}: revision missing.",
        )

        require(
            retired_word()
            not in repr(
                dict(response.headers)
            ).lower(),
            (
                f"{path}: retired environment "
                "identity found in headers."
            ),
        )

        result[path] = {
            "status_code": response.status_code,
            "revision": revision,
            "entrypoint": entrypoint,
        }

    manifest_response = session.get(
        base_url
        + "/tower/runtime-manifest.json",
        timeout=30,
    )

    manifest = manifest_response.json()

    require(
        manifest.get("entrypoint")
        == ENTRYPOINT,
        "Manifest entrypoint mismatch.",
    )

    require(
        manifest.get(
            "critical_routes_present"
        )
        is True,
        "Critical hosted routes missing.",
    )

    require(
        manifest.get(
            "critical_routes",
            {},
        ).get(
            "ob_dashboard"
        )
        is True,
        "Real OB dashboard route missing.",
    )

    require(
        retired_word()
        not in json.dumps(
            manifest,
            sort_keys=True,
        ).lower(),
        (
            "Runtime manifest still advertises "
            "retired environment identity."
        ),
    )

    for key in (
        "production_deployment",
        "broker_submission",
        "capital_movement",
        "manual_live_authorized",
        "live_auto_authorized",
    ):
        require(
            manifest.get(key)
            is False,
            (
                "Safety boundary open: "
                + key
            ),
        )

    observed_revision = manifest.get(
        "revision",
        "",
    )

    if expected_revision:
        require(
            observed_revision
            == expected_revision,
            (
                "Hosted revision mismatch.\n"
                f"Expected: {expected_revision}\n"
                f"Observed: {observed_revision}"
            ),
        )

    return {
        "ok": True,
        "base_url": base_url,
        "revision": observed_revision,
        "entrypoint": ENTRYPOINT,
        "checks": result,
    }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--base-url",
        required=True,
    )

    parser.add_argument(
        "--expected-revision",
        default="",
    )

    args = parser.parse_args()

    print(
        json.dumps(
            verify(
                args.base_url,
                args.expected_revision,
            ),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
