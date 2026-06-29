import json
from pathlib import Path
import unicodedata

def normalize_text(text):
    if text is None:
        return ""
    return unicodedata.normalize("NFC", str(text).strip())

SCRIPT_DIR = Path(__file__).parent

TICKETS_FILE = SCRIPT_DIR / "tickets.json"
EDGES_FILE = SCRIPT_DIR / "edges_expanded.json"
OUTPUT_FILE = SCRIPT_DIR / "ticket_submission.json"

with open("tickets.json", encoding="utf-8") as f:
    tickets = json.load(f)

for item in tickets[:20]:
    print(repr(item["refId"]))

def main():
    # 1. Load tickets and map by (refId[0], refId[1]) matching their names
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        tickets_data = json.load(f)

    ticket_map = {}
    for entry in tickets_data:
        ref_id = entry.get("refId", [])
        if len(ref_id) >= 2:
            source = normalize_text(ref_id[0])
            target = normalize_text(ref_id[1])
            # Map tickets using the station names. Ignore osmId from tickets.json.
            ticket_map[(source, target)] = entry.get("tickets", [])

    print()
    print("===== SAMPLE TICKET KEYS =====")
    for i, k in enumerate(ticket_map.keys()):
        print(repr(k))
        if i >= 10:
            break
    print("==============================")
    print()

    # 2. Load edges
    with open(EDGES_FILE, "r", encoding="utf-8") as f:
        edges_data = json.load(f)

    # 3. Process data
    submission_dict = {}
    
    # Track unique combinations of (sourceOsmId, targetOsmId) to prevent duplication
    processed_pairs = set()

    for edge in edges_data:
        source = normalize_text(edge.get("source"))
        target = normalize_text(edge.get("target"))

        source_osm_id = edge.get("sourceOsmId")
        target_osm_id = edge.get("targetOsmId")

        if not all([source, target, source_osm_id, target_osm_id]):
            continue

        pair_key = (source_osm_id, target_osm_id)
        if pair_key in processed_pairs:
            continue

        # Look up tickets using the station names from edges_expanded.json
        tickets = ticket_map.get((source, target))
        if tickets is None:
            print(f"[WARN] No tickets found for {source} -> {target}")
            continue

        processed_pairs.add(pair_key)

        if source_osm_id not in submission_dict:
            submission_dict[source_osm_id] = {
                "osmId": source_osm_id,
                "out": []
            }

        submission_dict[source_osm_id]["out"].append({
            "tickets": tickets,
            "osmIdOut": target_osm_id
        })

    # 4. Output the submission data
    submission_list = list(submission_dict.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(submission_list, f, ensure_ascii=False, indent=4)

    print(f"Generated {OUTPUT_FILE.name} with {len(submission_list)} unique source OsmIds and {len(processed_pairs)} target connections.")

    # 5. Validate the completeness
    total_expanded_edges = len(edges_data)
    total_submitted_tickets = sum(len(item["out"]) for item in submission_list)

    print("\n--- BÁO CÁO KIỂM TRA (VALIDATION) ---")
    print(f"Tổng số routes trong edges_expanded.json: {total_expanded_edges}")
    print(f"Tổng số routes đã map vé trong ticket_submission.json: {total_submitted_tickets}")
    
    if total_expanded_edges == total_submitted_tickets:
        print("✅ THÀNH CÔNG: Dữ liệu khớp 100%! Không bị sót tuyến nào.")
    else:
        print(f"❌ CẢNH BÁO: Lệch dữ liệu! Có {total_expanded_edges - total_submitted_tickets} tuyến chưa được map vé.")
        print("   -> Nguyên nhân có thể do vé của cặp trạm đó bị thiếu trong file tickets.json.")

if __name__ == "__main__":
    main()
