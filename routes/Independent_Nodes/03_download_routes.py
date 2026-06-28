import json
import time
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).parent

INPUT_FILE = SCRIPT_DIR / "origin_candidates.json"

OUTPUT_DIR = SCRIPT_DIR / "routes"
OUTPUT_DIR.mkdir(exist_ok=True)

SUMMARY_FILE = SCRIPT_DIR / "route_summary.json"

REQUEST_DELAY = 2.5


def get_route(lat1, lon1, lat2, lon2):
    url = (
        f"http://router.project-osrm.org/route/v1/driving/"
        f"{lon1},{lat1};{lon2},{lat2}"
    )

    params = {
        "overview": "full",
        "geometries": "geojson"
    }

    r = requests.get(
        url,
        params=params,
        timeout=60
    )

    r.raise_for_status()

    data = r.json()

    if data.get("code") != "Ok":
        raise ValueError(data)

    route = data["routes"][0]

    return {
        "paths": [{
            "distance": route["distance"],
            "time": int(route["duration"] * 1000),
            "points": route["geometry"]
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