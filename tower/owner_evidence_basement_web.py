"""Protected backstage evidence catalog for the Tower owner / TWR151-TWR155."""

from __future__ import annotations

from html import escape
from typing import Any

from flask import jsonify

from tower.hosted_owner_release_review_web import (
    _page,
    _step_up_required,
)
from tower.hosted_owner_release_walkthrough_web import (
    HOSTED_CERTIFICATION_JSON_PATH,
    HOSTED_READINESS_JSON_PATH,
    HOSTED_WALKTHROUGH_PATH,
)
from tower.hosted_release_prerequisite_certification_web import (
    PREREQUISITE_CERTIFICATION_JSON_PATH,
    PREREQUISITE_PAGE_PATH,
    PREREQUISITE_VERIFICATION_JSON_PATH,
)


EVIDENCE_BASEMENT_PATH = (
    "/tower/owner/evidence"
)

EVIDENCE_BASEMENT_JSON_PATH = (
    "/tower/owner/evidence.json"
)

EVIDENCE_BASEMENT_MARKER = (
    "tower-owner-evidence-basement-twr151-155"
)


def evidence_basement_manifest(
) -> dict[str, Any]:

    resources = [
        (
            "hosted_readiness_walkthrough",
            "Hosted readiness walkthrough",
            HOSTED_WALKTHROUGH_PATH,
            "walkthrough",
        ),
        (
            "hosted_readiness_projection",
            "Hosted readiness projection",
            HOSTED_READINESS_JSON_PATH,
            "evidence_json",
        ),
        (
            "hosted_walkthrough_certification",
            "Hosted walkthrough certification",
            HOSTED_CERTIFICATION_JSON_PATH,
            "certification_json",
        ),
        (
            "release_prerequisite_certificate",
            "Release prerequisite certificate",
            PREREQUISITE_PAGE_PATH,
            "certificate",
        ),
        (
            "release_prerequisite_verification",
            "Prerequisite verification projection",
            PREREQUISITE_VERIFICATION_JSON_PATH,
            "evidence_json",
        ),
        (
            "release_prerequisite_certification",
            "Prerequisite certification projection",
            PREREQUISITE_CERTIFICATION_JSON_PATH,
            "certification_json",
        ),
    ]

    return {
        "schema_version":
            "tower.owner-evidence-basement.v1",

        "surface":
            "owner_evidence_basement",

        "backstage":
            True,

        "primary_owner_surface":
            False,

        "read_only":
            True,

        "step_up_required":
            True,

        "proof_is_product":
            False,

        "evidence_is_operation":
            False,

        "execution_authority":
            False,

        "resource_count":
            len(
                resources
            ),

        "resources": [
            {
                "resource_id":
                    resource_id,

                "label":
                    label,

                "path":
                    path,

                "kind":
                    kind,

                "backstage":
                    True,

                "primary_navigation":
                    False,

                "read_only":
                    True,

                "execution_authority":
                    False,
            }
            for (
                resource_id,
                label,
                path,
                kind,
            )
            in resources
        ],
    }


def owner_evidence_basement_html(
    manifest: dict[str, Any] | None = None,
) -> str:

    manifest = (
        manifest
        or evidence_basement_manifest()
    )

    rows = []

    for resource in manifest[
        "resources"
    ]:

        label = escape(
            str(
                resource[
                    "label"
                ]
            )
        )

        path = escape(
            str(
                resource[
                    "path"
                ]
            )
        )

        kind = escape(
            str(
                resource[
                    "kind"
                ]
            ).replace(
                "_",
                " ",
            )
        )

        rows.append(
            f"""
            <article class="card">
              <span class="label">
                {kind}
              </span>

              <strong class="value">
                {label}
              </strong>

              <p class="quiet">
                Backstage evidence only. This resource does not execute,
                deploy, promote, trade, move capital, or unlock a live mode.
              </p>

              <a
                class="button"
                href="{path}"
                data-tower-backstage-evidence="true"
              >
                Open evidence
              </a>
            </article>
            """
        )

    body = f"""
    <section
      class="hero"
      data-tower-evidence-basement="{EVIDENCE_BASEMENT_MARKER}"
    >
      <span class="eyebrow">
        Tower · backstage
      </span>

      <h1>
        Evidence Basement
      </h1>

      <p class="quiet">
        Proof, walkthroughs, readiness details, and certification records
        live here. They remain available for inspection without becoming
        the normal owner operating experience.
      </p>

      <span class="chip">
        BACKSTAGE · READ ONLY
      </span>
    </section>

    <section class="card">
      <span class="eyebrow">
        Boundary
      </span>

      <p>
        Tower operations happen on operational owner surfaces.
        Evidence supports those operations; it does not replace them.
      </p>

      <p class="notice">
        Nothing in the Evidence Basement grants release execution,
        broker submission, capital movement, Manual Live, or Live Auto.
      </p>
    </section>

    <section
      class="grid"
      data-tower-evidence-resource-count="{manifest['resource_count']}"
    >
      {''.join(rows)}
    </section>
    """

    return _page(
        "Tower · Evidence Basement",
        body,
        back="/tower/owner-dashboard",
    )


def register_tower_owner_evidence_basement_routes(
    app,
):

    marker = (
        "_tower_owner_evidence_basement_routes_twr151_155"
    )

    if getattr(
        app,
        marker,
        False,
    ):
        return app

    @app.get(
        EVIDENCE_BASEMENT_PATH
    )
    def tower_owner_evidence_basement_page():

        denied = (
            _step_up_required()
        )

        if denied is not None:
            return denied

        return (
            owner_evidence_basement_html()
        )

    @app.get(
        EVIDENCE_BASEMENT_JSON_PATH
    )
    def tower_owner_evidence_basement_json():

        denied = (
            _step_up_required()
        )

        if denied is not None:
            return denied

        return jsonify(
            evidence_basement_manifest()
        )

    setattr(
        app,
        marker,
        True,
    )

    return app
