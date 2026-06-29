import json
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

INPUT_FILE = SCRIPT_DIR / "origin_edges.json"

# CSV_FILE = SCRIPT_DIR / "merged_Cam Lâm - Vĩnh Hảo.csv"
CSV_FILE = SCRIPT_DIR / f"merged_{SCRIPT_DIR.name}.csv"

OUTPUT_FILE = SCRIPT_DIR / "edges_expanded.json"

df = pd.read_csv(CSV_FILE)

osm_lookup = {}

for _, row in df.iterrows():

    osm_lookup[str(row["origin_osm_id"])] = {
        "lat": float(row["origin_osm_latitude"]),
        "lon": float(row["origin_osm_longitude"])
    }

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

final_edges = []

for row in data:
    source_osm_id = row["source_osm_id"]
    target_osm_id = row["target_osm_id"]

    source_coord = osm_lookup.get(source_osm_id)
    target_coord = osm_lookup.get(target_osm_id)

    osm_url = None

    if source_coord and target_coord:

        osm_url = (
            "https://www.openstreetmap.org/directions"
            "?engine=fossgis_valhalla_car"
            f"&route="
            f"{source_coord['lat']},{source_coord['lon']};"
            f"{target_coord['lat']},{target_coord['lon']}"
        )

    edge_id = (
        f"{row['source']}|"
        f"{row['target']}"
    )

    origin_edge_id = (
        f"{row['source']}|"
        f"{row['target']}|"
        f"{row['source_origin_osm_name']}|"
        f"{row['target_origin_osm_name']}"
    )

    final_edges.append({

        "edgeId":
            edge_id,

        "originEdgeId":
            origin_edge_id,

        "source":
            row["source"],

        "target":
            row["target"],

        "sourceOriginOsmName":
            row["source_origin_osm_name"],

        "targetOriginOsmName":
            row["target_origin_osm_name"],

        "sourceOsmId":
            row["source_osm_id"],

        "targetOsmId":
            row["target_osm_id"],

        "distance_m":
            row["distance_m"],

        "time_ms":
            row["time_ms"],

        "route_count":
            row.get(
                "route_count",
                None
            ),

        "runner_up_distance":
            row.get(
                "runner_up_distance",
                None
            ),
        
        "osm_route_url":
            osm_url,
        
        "osm_node_url":
            f"https://www.openstreetmap.org/node/{source_osm_id}",

        "target_osm_node_url":
            f"https://www.openstreetmap.org/node/{target_osm_id}"
    })

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        final_edges,
        f,
        ensure_ascii=False,
        indent=2
    )

print(
    f"saved {len(final_edges)} edges"
)