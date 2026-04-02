from typing import Dict


def assign_correlation(signal: Dict) -> Dict:
    sector = signal.get("sector", "unknown")

    cluster_map = {
        "Energy": "energy_cluster",
        "Technology": "tech_cluster",
        "Healthcare": "health_cluster",
    }

    cluster = cluster_map.get(sector, "general_cluster")

    return {
        "correlation_cluster": cluster
    }
