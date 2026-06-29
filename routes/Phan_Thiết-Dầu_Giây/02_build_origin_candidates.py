import json
from pathlib import Path
import unicodedata

def normalize_text(text):
    if text is None:
        return ""
    return unicodedata.normalize("NFC", str(text).strip())

SCRIPT_DIR = Path(__file__).parent

TREE_FILE = SCRIPT_DIR / "station_tree.json"
EDGES_FILE = SCRIPT_DIR / "edges.json"

OUTPUT_FILE = SCRIPT_DIR / "origin_candidates.json"

with open(TREE_FILE, encoding="utf-8") as f:
    tree = json.load(f)
    print("\n===== TREE KEYS =====")
    for k in sorted(tree.keys()):
        print(repr(k))
    print("=====================\n")

with open(EDGES_FILE, encoding="utf-8") as f:
    edges = json.load(f)
    print("\n===== MISSING DEBUG =====")

    for edge in edges:

        source_epass = normalize_text(edge["source"])

        if source_epass not in tree:

            print(f"\nMissing: {repr(source_epass)}")

            for k in tree.keys():

                if "QL" in source_epass and "QL" in k:
                    print("  candidate:", repr(k))

                if "TL" in source_epass and "TL" in k:
                    print("  candidate:", repr(k))
results = []

for edge in edges:

    source_epass = normalize_text(edge["source"])
    target_epass = normalize_text(edge["target"])

    if source_epass not in tree:
        print( f"[MISSING SOURCE] {repr(source_epass)}")
        continue

    if target_epass not in tree:
        print( f"[MISSING TARGET] {repr(target_epass)}")
        continue

    source_origins = tree[source_epass]
    target_origins = tree[target_epass]

    for source_origin_name, source_booths in source_origins.items():

        for target_origin_name, target_booths in target_origins.items():

            results.append(
                {
                    "source_epass": source_epass,
                    "target_epass": target_epass,

                    "source_origin_osm_name":
                        source_origin_name,

                    "target_origin_osm_name":
                        target_origin_name,

                    "source_booths":
                        source_booths,

                    "target_booths":
                        target_booths
                }
            )

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )

print("saved:", OUTPUT_FILE)