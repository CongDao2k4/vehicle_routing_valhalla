import json
import time
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).parent

INPUT_FILE = SCRIPT_DIR / "origin_candidates.json"

OUTPUT_DIR = SCRIPT_DIR / "routes"
OUTPUT_DIR.mkdir(exist_ok=True)

SUMMARY_FILE = SCRIPT_DIR / "route_summary.json"

REQUEST_DELAY = 0.5


def decode_polyline6(encoded):
    """Decodes a polyline6 string into a list of (lon, lat) coordinates."""
    coordinates = []
    index = 0
    len_encoded = len(encoded)
    lat = 0
    lon = 0

    while index < len_encoded:
        # Read latitude
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if not (b & 0x20):
                break
        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        # Read longitude
        shift = 0
        result = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if not (b & 0x20):
                break
        dlon = ~(result >> 1) if (result & 1) else (result >> 1)
        lon += dlon

        coordinates.append([lon / 1e6, lat / 1e6])

    return coordinates


def get_route(lat1, lon1, lat2, lon2):
    valhalla_json = {
        "locations": [
            {"lat": lat1, "lon": lon1, "radius": 5},
            {"lat": lat2, "lon": lon2, "radius": 5}
        ],
        "costing": "auto",
        "directions_options": {
            "units": "km",
            "language": "en"
        }
    }

    # url = "https://valhalla1.openstreetmap.de/route"
    url = "http://localhost:8002/route"
    params = {
        "json": json.dumps(valhalla_json, separators=(',', ':'))
    }

    r = requests.get(
        url,
        params=params,
        timeout=60
    )

    r.raise_for_status()

    data = r.json()

    if "trip" not in data or data["trip"].get("status") != 0:
        raise ValueError(data)

    trip = data["trip"]
    leg = trip["legs"][0]

    # Valhalla summary.length is in km, convert to meters
    distance_m = leg["summary"]["length"] * 1000.0
    # Valhalla summary.time is in seconds, convert to milliseconds
    time_ms = int(leg["summary"]["time"] * 1000)

    # Decode shape (polyline6) to coordinates [[lon, lat], ...]
    coords = decode_polyline6(leg["shape"])

    return {
        "paths": [{
            "distance": distance_m,
            "time": time_ms,
            "points": {
                "type": "LineString",
                "coordinates": coords
            }
        }]
    }



with open(INPUT_FILE, encoding="utf-8") as f:
    origin_candidates = json.load(f)

summary = []

for item in origin_candidates:

    source_epass = item["source_epass"]
    target_epass = item["target_epass"]

    source_origin = item["source_origin_osm_name"]
    target_origin = item["target_origin_osm_name"]

    print(
        f"\n{source_epass} [{source_origin}]"
        f" -> "
        f"{target_epass} [{target_origin}]"
    )

    for source_booth in item["source_booths"]:

        for target_booth in item["target_booths"]:

            source_osm_id = source_booth["osm_id"]
            target_osm_id = target_booth["osm_id"]

            candidate_id = (
                f"{source_epass}|{target_epass}|"
                f"{source_origin}|{target_origin}|"
                f"{source_osm_id}|{target_osm_id}"
            )

            safe_filename = (
                candidate_id
                .replace("|", "_")
                .replace("/", "_")
            )

            output_file = (
                OUTPUT_DIR /
                f"{safe_filename}.json"
            )

            try:

                if output_file.exists():

                    with open(
                        output_file,
                        "r",
                        encoding="utf-8"
                    ) as f:
                        route_json = json.load(f)

                    print(
                        f"SKIP {candidate_id}"
                    )

                else:

                    route_json = get_route(
                        source_booth["lat"],
                        source_booth["lon"],
                        target_booth["lat"],
                        target_booth["lon"]
                    )

                    with open(
                        output_file,
                        "w",
                        encoding="utf-8"
                    ) as f:
                        json.dump(
                            route_json,
                            f,
                            ensure_ascii=False,
                            indent=2
                        )

                    time.sleep(
                        REQUEST_DELAY
                    )

                path = route_json["paths"][0]

                summary.append({

                    "candidate_id":
                        candidate_id,

                    "source_epass":
                        source_epass,

                    "target_epass":
                        target_epass,

                    "source_origin_osm_name":
                        source_origin,

                    "target_origin_osm_name":
                        target_origin,

                    "source_osm_id":
                        source_osm_id,

                    "target_osm_id":
                        target_osm_id,

                    "distance_m":
                        path["distance"],

                    "time_ms":
                        path["time"],

                    "point_count":
                        len(
                            path["points"][
                                "coordinates"
                            ]
                        ),

                    "file":
                        str(output_file)
                })

                print(
                    f"OK {candidate_id}"
                )

            except Exception as e:

                print(
                    f"FAIL {candidate_id}: {e}"
                )

with open(
    SUMMARY_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        summary,
        f,
        ensure_ascii=False,
        indent=2
    )

print()
print(
    f"Saved {len(summary)} routes"
)