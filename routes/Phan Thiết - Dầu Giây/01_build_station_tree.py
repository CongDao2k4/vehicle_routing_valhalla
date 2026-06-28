import json
import pandas as pd
from pathlib import Path
import unicodedata

def normalize_text(text):
    if text is None:
        return ""
    return unicodedata.normalize("NFC", str(text).strip())

SCRIPT_DIR = Path(__file__).parent

CSV_FILE = SCRIPT_DIR / "merged_Phan Thiết - Dầu Giây.csv"

OUTPUT_FILE = SCRIPT_DIR / "station_tree.json"

df = pd.read_csv(CSV_FILE)

df = df[
    [
        "epass_name",
        "origin_osm_name",
        "origin_osm_id",
        "origin_osm_latitude",
        "origin_osm_longitude"
    ]
]

df = df.drop_duplicates(
    subset=[
        "origin_osm_id",
        "origin_osm_latitude",
        "origin_osm_longitude"
    ]
)

tree = {}

for _, row in df.iterrows():
    epass = normalize_text(row["epass_name"])
    origin = normalize_text(row["origin_osm_name"])

    tree.setdefault(epass, {})
    tree[epass].setdefault(origin, [])

    tree[epass][origin].append(
        {
            "osm_id": str(row["origin_osm_id"]),
            "lat": float(row["origin_osm_latitude"]),
            "lon": float(row["origin_osm_longitude"])
        }
    )

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        tree,
        f,
        ensure_ascii=False,
        indent=2
    )

print("saved:", OUTPUT_FILE)