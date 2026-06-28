import json
import csv
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

TICKETS_FILE = SCRIPT_DIR / "tickets.json"
CSV_FILE = SCRIPT_DIR / "merged_Independent_Nodes.csv"
OUTPUT_FILE = SCRIPT_DIR / "ticket_submission.json"

def main():
    # 1. Load tickets and map by refId (which is epass_name)
    with open(TICKETS_FILE, "r", encoding="utf-8") as f:
        tickets_data = json.load(f)

    ticket_map = {}
    for entry in tickets_data:
        ref_id = entry.get("refId")
        if ref_id and isinstance(ref_id, str):
            ticket_map[ref_id] = entry.get("tickets", [])

    # 2. Load CSV and extract origin_osm_id by epass_name
    submission_dict = {}
    
    unique_origin_ids = set()
    missing_ticket_epass = set()

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            epass_name = row.get("epass_name")
            origin_osm_id = row.get("origin_osm_id")

            if not epass_name or not origin_osm_id:
                continue
                
            origin_osm_id_str = str(origin_osm_id)

            if origin_osm_id_str in unique_origin_ids:
                continue

            unique_origin_ids.add(origin_osm_id_str)

            tickets = ticket_map.get(epass_name)
            if tickets is None:
                missing_ticket_epass.add(epass_name)
                continue

            # 3. Process data
            submission_dict[origin_osm_id_str] = {
                "osmId": origin_osm_id_str,
                "out": [
                    {
                        "tickets": tickets,
                        "osmIdOut": origin_osm_id_str
                    }
                ]
            }

    # 4. Output the submission data
    submission_list = list(submission_dict.values())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(submission_list, f, ensure_ascii=False, indent=4)

    print(f"Generated {OUTPUT_FILE.name} with {len(submission_list)} unique toll booths (origin_osm_id).")

    # 5. Validate the completeness
    print("\n--- VALIDATION REPORT ---")
    print(f"Total unique origin_osm_id in CSV: {len(unique_origin_ids)}")
    print(f"Total origin_osm_id mapped in ticket_submission.json: {len(submission_list)}")
    
    if len(unique_origin_ids) == len(submission_list):
        print("SUCCESS: 100% matched! No missing gates.")
    else:
        diff = len(unique_origin_ids) - len(submission_list)
        print(f"WARNING: Data mismatch! {diff} gates are missing tickets.")
        if missing_ticket_epass:
            print("   -> Missing due to the following epass_names not found in tickets.json:")
            for epass in missing_ticket_epass:
                print(f"      - {epass}")

if __name__ == "__main__":
    main()
