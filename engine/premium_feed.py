import json
from pathlib import Path

FILE = "data/premium_feed.json"

def write_premium_feed_item(item):
    if not item.get("pro_lines"):
        item["pro_lines"] = [
            item.get("summary", "The system evaluated this setup but did not attach a deeper read."),
        ]

    if not item.get("elite_lines"):
        item["elite_lines"] = []

    # existing save logic continues...
