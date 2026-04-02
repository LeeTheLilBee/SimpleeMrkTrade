from typing import Dict


def build_thesis(signal: Dict, decision: Dict) -> Dict:
    direction = signal.get("direction", "unknown")
    setup = signal.get("setup_type", "setup")
    symbol = signal.get("symbol", "")

    statement = f"{symbol} is showing a {setup} setup with {direction.lower()} bias."

    return {
        "thesis_statement": statement
    }
