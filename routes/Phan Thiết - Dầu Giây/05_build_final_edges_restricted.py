import json
import pandas as pd
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

INPUT_FILE = SCRIPT_DIR / "origin_edges_restricted.json"

CSV_FILE = SCRIPT_DIR / "merged_Phan Thiết - Dầu Giây.csv"

OUTPUT_FILE = SCRIPT_DIR / "edges_expanded_restricted.json"

# =====================================================
# Load coordinate lookup
# =====================================================

df = pd.read_csv(CSV_FILE)

osm_lookup = {}

for _, row in df.iterrows():

    osm_lookup[str(row["origin_osm_id"])] = {
        "lat": float(row["origin_osm_latitude"]),
        "lon": float(row["origin_osm_longitude"])
    }

# =====================================================
# Load restricted edges
# =====================================================

with open(INPUT_FILE, encoding="utf-8") as f:
    data = json.load(f)

final_edges = []

# =====================================================
# Build output
# =====================================================

for row in data:

    source_osm_id = str(row["source_osm_id"])
    target_osm_id = str(row["target_osm_id"])

    source_coord = osm_lookup.get(source_osm_id)
    target_coord = osm_lookup.get(target_osm_id)

    osm_url = None
    google_maps_url = None

    if source_coord and target_coord:

        osm_url = (
            "https://www.openstreetmap.org/directions"
            "?engine=fossgis_valhalla_car"
            f"&route="
            f"{source_coord['lat']},{source_coord['lon']};"
            f"{target_coord['lat']},{target_coord['lon']}"
        )

        google_maps_url = (
            "https://www.google.com/maps/dir/"
            f"{source_coord['lat']},"
            f"{source_coord['lon']}/"
            f"{target_coord['lat']},"
            f"{target_coord['lon']}"
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

    confidence = None

    runner_up = row.get(
        "origin_runner_up_distance"
    )

    if (
        runner_up is not None
        and row["distance_m"] > 0
    ):
        confidence = round(
            runner_up /
            row["distance_m"],
            2
        )

    final_edges.append({

        # ==========================
        # IDs
        # ==========================

        "edgeId":
            edge_id,

        "originEdgeId":
            origin_edge_id,

        # ==========================
        # Epass
        # ==========================

        "source":
            row["source"],

        "target":
            row["target"],

        # ==========================
        # Origin station
        # ==========================

        "sourceOriginOsmName":
            row["source_origin_osm_name"],

        "targetOriginOsmName":
            row["target_origin_osm_name"],

        # ==========================
        # Winner booths
        # ==========================

        "sourceOsmId":
            source_osm_id,

        "targetOsmId":
            target_osm_id,

        # ==========================
        # Routing metrics
        # ==========================

        "distance_m":
            row["distance_m"],

        "time_ms":
            row["time_ms"],

        # ==========================
        # Booth competition
        # ==========================

        "route_count":
            row.get(
                "route_count"
            ),

        "runner_up_distance":
            row.get(
                "runner_up_distance"
            ),

        # ==========================
        # Origin pair competition
        # ==========================

        "origin_pair_count":
            row.get(
                "origin_pair_count"
            ),

        "origin_runner_up_distance":
            row.get(
                "origin_runner_up_distance"
            ),

        "confidence":
            confidence,

        # ==========================
        # Coordinates
        # ==========================

        "sourceLat":
            source_coord["lat"]
            if source_coord else None,

        "sourceLon":
            source_coord["lon"]
            if source_coord else None,

        "targetLat":
            target_coord["lat"]
            if target_coord else None,

        "targetLon":
            target_coord["lon"]
            if target_coord else None,

        # ==========================
        # Review URLs
        # ==========================

        "osm_route_url":
            osm_url,

        "google_maps_url":
            google_maps_url,

        "osm_node_url":
            f"https://www.openstreetmap.org/node/{source_osm_id}",

        "target_osm_node_url":
            f"https://www.openstreetmap.org/node/{target_osm_id}"
    })

# =====================================================
# Save
# =====================================================

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
    f"saved {len(final_edges)} restricted edges"
)