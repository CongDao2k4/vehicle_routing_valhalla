import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

INPUT_FILE = SCRIPT_DIR / "origin_edges.json"

OUTPUT_FILE = SCRIPT_DIR / "origin_edges_restricted.json"

with open(INPUT_FILE, encoding="utf-8") as f:
    origin_edges = json.load(f)

groups = {}

for row in origin_edges:

    key = (
        row["source"],
        row["target"]
    )

    groups.setdefault(
        key,
        []
    ).append(row)

restricted = []

for key, items in groups.items():

    sorted_items = sorted(
        items,
        key=lambda x: x["distance_m"]
    )

    winner = sorted_items[0]

    runner_up = None

    if len(sorted_items) > 1:
        runner_up = sorted_items[1]["distance_m"]

    winner["origin_pair_count"] = len(items)

    winner["origin_runner_up_distance"] = (
        runner_up
    )

    restricted.append(winner)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        restricted,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"saved {len(restricted)} restricted edges"
)