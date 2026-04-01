from typing import Dict, Any, List

from engine_v2.real_constellation_library import (
    REAL_CONSTELLATIONS,
    SECTOR_CONSTELLATION_PREFERENCES,
)


def _safe_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _pick_constellation(bucket: str, star_count: int) -> str:
    bucket = str(bucket or "general")
    prefs = SECTOR_CONSTELLATION_PREFERENCES.get(bucket, SECTOR_CONSTELLATION_PREFERENCES["general"])
    if not prefs:
        prefs = ["cassiopeia"]

    index = max(0, min(len(prefs) - 1, (star_count - 1) % len(prefs)))
    return prefs[index]


def map_tiles_to_constellation(bucket: str, tiles: List[Dict[str, Any]]) -> Dict[str, Any]:
    raw_tiles = [t for t in _safe_list(tiles) if isinstance(t, dict)]

    deduped = {}
    for tile in raw_tiles:
        symbol = str(tile.get("symbol", "") or "").upper().strip()
        if not symbol:
            continue

        existing = deduped.get(symbol)
        if not existing:
            deduped[symbol] = tile
            continue

        existing_score = (
            existing.get("size_score", 1),
            existing.get("glow_intensity", 0),
            existing.get("score", 0),
        )
        new_score = (
            tile.get("size_score", 1),
            tile.get("glow_intensity", 0),
            tile.get("score", 0),
        )

        if new_score > existing_score:
            deduped[symbol] = tile

    tiles = sorted(
        list(deduped.values()),
        key=lambda t: (
            t.get("size_score", 1),
            t.get("glow_intensity", 0),
            t.get("score", 0),
        ),
        reverse=True,
    )

    constellation_name = _pick_constellation(bucket, len(tiles))
    template = REAL_CONSTELLATIONS[constellation_name]

    points = template.get("points", [])
    connections = template.get("connections", [])

    mapped_stars = []
    for tile, point in zip(tiles, points):
        mapped_stars.append({
            "symbol": tile.get("symbol"),
            "company_name": tile.get("company_name"),
            "destination": tile.get("destination"),
            "lane": tile.get("lane"),
            "bucket": tile.get("bucket"),
            "direction": tile.get("direction"),
            "pressure_level": tile.get("pressure_level"),
            "glow_intensity": tile.get("glow_intensity"),
            "size_score": tile.get("size_score"),
            "score": tile.get("score"),
            "structure": tile.get("structure", ""),
            "target_dte": tile.get("target_dte", ""),
            "x": point.get("x"),
            "y": point.get("y"),
            "rank": point.get("rank"),
        })

    line_segments = []
    for a_idx, b_idx in connections:
        if a_idx < len(mapped_stars) and b_idx < len(mapped_stars):
            a = mapped_stars[a_idx]
            b = mapped_stars[b_idx]
            line_segments.append({
                "x1": a["x"],
                "y1": a["y"],
                "x2": b["x"],
                "y2": b["y"],
            })

    overflow_tiles = tiles[len(points):]
    overflow = []
    for i, tile in enumerate(overflow_tiles):
        overflow.append({
            "symbol": tile.get("symbol"),
            "company_name": tile.get("company_name"),
            "destination": tile.get("destination"),
            "lane": tile.get("lane"),
            "bucket": tile.get("bucket"),
            "direction": tile.get("direction"),
            "pressure_level": tile.get("pressure_level"),
            "glow_intensity": tile.get("glow_intensity"),
            "size_score": tile.get("size_score"),
            "score": tile.get("score"),
            "structure": tile.get("structure", ""),
            "target_dte": tile.get("target_dte", ""),
            "x": 82 + ((i * 7) % 12),
            "y": 20 + ((i * 13) % 60),
            "rank": 99 + i,
        })

    return {
        "bucket": bucket,
        "constellation": constellation_name,
        "label": template.get("label", constellation_name.title()),
        "stars": mapped_stars,
        "overflow": overflow,
        "lines": line_segments,
    }
