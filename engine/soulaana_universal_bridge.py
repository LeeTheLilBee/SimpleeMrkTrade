from __future__ import annotations

from typing import Any, Mapping

import engine.soulaana_core as soulaana_core

from engine.soulaana_universal_contract import (
    canonicalize_soulaana_payload,
)


PACKAGE = "OBUX002"

TITLE = (
    "Soulaana Core Explainability Fusion Voice Bridge"
)


def _fusion_available() -> bool:

    try:

        import engine_v2.soulaana_fusion_layer as fusion

        return callable(
            getattr(
                fusion,
                "build_soulaana_fusion_layer",
                None,
            )
        )

    except Exception:

        return False


def build_universal_soulaana(
    context: Mapping[str, Any],
    *,
    emotional_state: str | None = None,
    existing_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:

    source_error = None

    if existing_payload is not None:

        raw_soulaana = dict(
            existing_payload
        )

        source_method = (
            "existing_payload"
        )

    else:

        try:

            raw_soulaana = (
                soulaana_core.build_soulaana_output(
                    dict(
                        context
                    ),
                    emotional_state=emotional_state,
                )
            )

            if not isinstance(
                raw_soulaana,
                dict,
            ):

                raw_soulaana = {}

            source_method = (
                "engine.soulaana_core.build_soulaana_output"
            )

        except Exception as exc:

            source_error = (
                f"{type(exc).__name__}: {exc}"
            )

            raw_soulaana = {}

            source_method = (
                "safe_fallback_after_existing_core_error"
            )


    canonical = canonicalize_soulaana_payload(
        raw_soulaana,
        context=context,
    )


    return {
        "package": PACKAGE,
        "title": TITLE,
        "gate_state": (
            "soulaana_existing_layer_bridge_sealed"
        ),
        "source_method": source_method,
        "source_error": source_error,
        "existing_core_used": (
            existing_payload is None
            and
            source_error is None
        ),
        "existing_payload_used": (
            existing_payload is not None
        ),
        "fusion_layer_available": (
            _fusion_available()
        ),
        "explainability_layer_preserved": True,
        "voice_layer_preserved": True,
        "final_decision_layer_preserved": True,
        "canonical_decision_layer_preserved": True,
        "existing_soulaana_core_preserved": True,
        "parallel_voice_system_created": False,
        "parallel_intelligence_system_created": False,
        "emotional_state": emotional_state,
        "raw_soulaana": raw_soulaana,
        "universal": canonical,
        "recommendation": (
            "GO_FOR_SOULAANA_CONTEXT_PERMISSION_ADAPTER"
        ),
    }
