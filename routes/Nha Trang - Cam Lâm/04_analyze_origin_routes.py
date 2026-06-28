import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

INPUT_FILE = SCRIPT_DIR / "route_summary.json"

OUTPUT_FILE = SCRIPT_DIR / "origin_edges.json"

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:
    routes = json.load(f)

groups = {}

for route in routes:

    key = (
        route["source_epass"],
        route["target_epass"],
        route["source_origin_osm_name"],
        route["target_origin_osm_name"]
    )

    groups.setdefault(
        key,
        []
    ).append(route)

winners = []

for key, route_list in groups.items():

    sorted_routes = sorted(
        route_list,
        key=lambda x: x["distance_m"]
    )

    winner = sorted_routes[0]

    runner_up = None

    if len(sorted_routes) > 1:
        runner_up = sorted_routes[1]["distance_m"]

    winners.append({

        "source":
            key[0],

        "target":
            key[1],

        "source_origin_osm_name":
            key[2],

        "target_origin_osm_name":
            key[3],

        "source_osm_id":
            winner["source_osm_id"],

        "target_osm_id":
            winner["target_osm_id"],

        "distance_m":
            winner["distance_m"],

        "time_ms":
            winner["time_ms"],

        "route_count":
            len(route_list),

        "runner_up_distance":
            runner_up
    })

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        winners,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"Saved {len(winners)} origin winners"
)