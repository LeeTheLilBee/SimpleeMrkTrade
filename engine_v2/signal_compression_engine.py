from typing import Dict


def suggest_signal_compression(meta: Dict) -> Dict:
    signal_quality = meta.get("signal_quality", {})
    state = signal_quality.get("signal_quality_state")

    if state == "crowded":
        return {
            "compression_mode": "moderate",
            "reason": "quality is becoming compressed across the board",
        }

    if state == "noisy":
        return {
            "compression_mode": "strong",
            "reason": "too many low-quality signals are active",
        }

    return {
        "compression_mode": "light",
        "reason": "signal hierarchy remains healthy",
    }
