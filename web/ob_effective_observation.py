from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class EffectiveObservationState(str, Enum):
    TRUSTED = "TRUSTED"
    USABLE = "USABLE"
    CAUTION = "CAUTION"
    QUARANTINED = "QUARANTINED"
    UNUSABLE = "UNUSABLE"
    UNKNOWN = "UNKNOWN"


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ObservationLayerState:
    source_authority: str
    freshness: str
    corroboration: str
    quality: str
    anomaly: str
    disposition: str


@dataclass(frozen=True)
class EffectiveObservationAssessment:
    state: EffectiveObservationState
    confidence: ConfidenceLevel
    layers: ObservationLayerState
    reasons: tuple[str, ...]
    limitations: tuple[str, ...]


def _normalized(value: Any) -> str:
    if value is None:
        return "UNKNOWN"

    raw = getattr(
        value,
        "value",
        value,
    )

    text = str(raw).strip().upper()

    return text if text else "UNKNOWN"


def _contains_unknown(
    layers: ObservationLayerState,
) -> bool:
    return any(
        value == "UNKNOWN"
        for value in (
            layers.source_authority,
            layers.freshness,
            layers.corroboration,
            layers.quality,
            layers.anomaly,
            layers.disposition,
        )
    )


def synthesize_effective_observation(
    *,
    source_authority: Any,
    freshness: Any,
    corroboration: Any,
    quality: Any,
    anomaly: Any,
    disposition: Any,
) -> EffectiveObservationAssessment:
    """
    Combine already-decided observation authority layers.

    This function DOES NOT override any upstream authority.

    It does not:
      - change source authority
      - make stale data fresh
      - erase disagreement
      - repair invalid data
      - suppress anomalies
      - grant execution permission
    """

    layers = ObservationLayerState(
        source_authority=_normalized(source_authority),
        freshness=_normalized(freshness),
        corroboration=_normalized(corroboration),
        quality=_normalized(quality),
        anomaly=_normalized(anomaly),
        disposition=_normalized(disposition),
    )

    reasons: list[str] = []
    limitations: list[str] = []

    # ----------------------------------------------------------------------------------------------------------
    # HARD UNUSABLE CONDITIONS
    # ----------------------------------------------------------------------------------------------------------

    if layers.quality == "INVALID":
        reasons.append(
            "Observation quality is INVALID."
        )

        limitations.append(
            "Invalid observations cannot be treated as usable market truth."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.UNUSABLE,
            confidence=ConfidenceLevel.NONE,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    if layers.anomaly == "IMPOSSIBLE":
        reasons.append(
            "Observation anomaly state is IMPOSSIBLE."
        )

        limitations.append(
            "Impossible observations cannot participate as usable current truth."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.UNUSABLE,
            confidence=ConfidenceLevel.NONE,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    if layers.disposition == "REJECT":
        reasons.append(
            "Observation disposition is REJECT."
        )

        limitations.append(
            "Rejected observations cannot flow forward as effective observations."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.UNUSABLE,
            confidence=ConfidenceLevel.NONE,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    # ----------------------------------------------------------------------------------------------------------
    # QUARANTINE CONDITIONS
    # ----------------------------------------------------------------------------------------------------------

    if (
        layers.disposition == "QUARANTINE"
        or layers.anomaly == "OUTLIER"
    ):
        reasons.append(
            "Observation requires quarantine."
        )

        limitations.append(
            "Quarantined observations remain visible as evidence but are not settled truth."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.QUARANTINED,
            confidence=ConfidenceLevel.LOW,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    # ----------------------------------------------------------------------------------------------------------
    # SEVERE CONFIDENCE LIMITERS
    # ----------------------------------------------------------------------------------------------------------

    severe_limiters = []

    if layers.freshness in {
        "STALE",
        "EXPIRED",
    }:
        severe_limiters.append(
            f"freshness={layers.freshness}"
        )

    if layers.corroboration in {
        "MATERIAL_DISAGREEMENT",
        "CONFLICTED",
    }:
        severe_limiters.append(
            f"corroboration={layers.corroboration}"
        )

    if severe_limiters:

        reasons.extend(
            severe_limiters
        )

        limitations.append(
            "At least one upstream authority layer prevents this observation from being treated as settled current truth."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.CAUTION,
            confidence=ConfidenceLevel.LOW,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    # ----------------------------------------------------------------------------------------------------------
    # UNKNOWN
    # ----------------------------------------------------------------------------------------------------------

    if _contains_unknown(layers):

        reasons.append(
            "One or more upstream observation authority layers are UNKNOWN."
        )

        limitations.append(
            "Missing authority evidence prevents a stronger effective-state conclusion."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.UNKNOWN,
            confidence=ConfidenceLevel.UNKNOWN,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    # ----------------------------------------------------------------------------------------------------------
    # MODERATE CAUTION CONDITIONS
    # ----------------------------------------------------------------------------------------------------------

    moderate_limiters = []

    if layers.freshness == "AGING":
        moderate_limiters.append(
            "freshness=AGING"
        )

    if layers.corroboration == "MINOR_DISAGREEMENT":
        moderate_limiters.append(
            "corroboration=MINOR_DISAGREEMENT"
        )

    if layers.quality == "DEGRADED":
        moderate_limiters.append(
            "quality=DEGRADED"
        )

    if layers.anomaly == "SUSPECT":
        moderate_limiters.append(
            "anomaly=SUSPECT"
        )

    if layers.disposition == "REVIEW":
        moderate_limiters.append(
            "disposition=REVIEW"
        )

    if moderate_limiters:

        reasons.extend(
            moderate_limiters
        )

        limitations.append(
            "Observation may be used for guarded analysis but requires visible caution."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.CAUTION,
            confidence=ConfidenceLevel.MODERATE,
            layers=layers,
            reasons=tuple(reasons),
            limitations=tuple(limitations),
        )

    # ----------------------------------------------------------------------------------------------------------
    # TRUSTED
    # ----------------------------------------------------------------------------------------------------------

    trusted_source = layers.source_authority in {
        "AUTHORITATIVE",
        "CORROBORATING",
    }

    trusted_freshness = (
        layers.freshness == "FRESH"
    )

    trusted_corroboration = (
        layers.corroboration == "CORROBORATED"
    )

    trusted_quality = (
        layers.quality == "VALID"
        and layers.anomaly == "NORMAL"
        and layers.disposition == "ACCEPT"
    )

    if (
        trusted_source
        and trusted_freshness
        and trusted_corroboration
        and trusted_quality
    ):

        reasons.append(
            "All major observation authority layers support normal current use."
        )

        return EffectiveObservationAssessment(
            state=EffectiveObservationState.TRUSTED,
            confidence=ConfidenceLevel.HIGH,
            layers=layers,
            reasons=tuple(reasons),
            limitations=(),
        )

    # ----------------------------------------------------------------------------------------------------------
    # USABLE
    # ----------------------------------------------------------------------------------------------------------

    reasons.append(
        "Observation passes all hard safety boundaries but lacks full corroborated high-confidence support."
    )

    limitations.append(
        "Usable does not mean corroborated, authoritative, or executable."
    )

    return EffectiveObservationAssessment(
        state=EffectiveObservationState.USABLE,
        confidence=ConfidenceLevel.MODERATE,
        layers=layers,
        reasons=tuple(reasons),
        limitations=tuple(limitations),
    )


def may_be_used_for_normal_reasoning(
    assessment: EffectiveObservationAssessment,
) -> bool:
    return assessment.state in {
        EffectiveObservationState.TRUSTED,
        EffectiveObservationState.USABLE,
    }


def requires_visible_caution(
    assessment: EffectiveObservationAssessment,
) -> bool:
    return assessment.state is EffectiveObservationState.CAUTION


def must_remain_quarantined(
    assessment: EffectiveObservationAssessment,
) -> bool:
    return assessment.state is EffectiveObservationState.QUARANTINED


def must_not_be_used_as_observation_truth(
    assessment: EffectiveObservationAssessment,
) -> bool:
    return assessment.state in {
        EffectiveObservationState.UNUSABLE,
        EffectiveObservationState.UNKNOWN,
    }


def effective_observation_snapshot(
    assessment: EffectiveObservationAssessment,
) -> dict[str, object]:
    return {
        "state": assessment.state.value,
        "confidence": assessment.confidence.value,
        "layers": {
            "source_authority": assessment.layers.source_authority,
            "freshness": assessment.layers.freshness,
            "corroboration": assessment.layers.corroboration,
            "quality": assessment.layers.quality,
            "anomaly": assessment.layers.anomaly,
            "disposition": assessment.layers.disposition,
        },
        "reasons": list(
            assessment.reasons
        ),
        "limitations": list(
            assessment.limitations
        ),
    }
