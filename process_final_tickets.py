import json
import sys
from pathlib import Path

# Fix Windows console utf-8 print issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def process_tickets(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initial Validation Counters
    init_distinct_osmId = len(set(item['osmId'] for item in data if 'osmId' in item))
    init_total_osmIdOut = 0
    init_total_tickets = 0
    init_total_prices = 0

    merged_dict = {}

    for item in data:
        osm_id = item.get("osmId")
        if not osm_id:
            continue
            
        if osm_id not in merged_dict:
            merged_dict[osm_id] = {
                "osmId": osm_id,
                "out": []
            }
            
        out_list = item.get("out", [])
        
        for out_item in out_list:
            init_total_osmIdOut += 1
            
            # Process tickets and prices inside this out_item
            processed_tickets = []
            for ticket in out_item.get("tickets", []):
                init_total_tickets += 1
                processed_prices = []
                for price in ticket.get("prices", []):
                    init_total_prices += 1
                    
                    new_price = {}
                    fee_obj = {}
                    for k, v in price.items():
                        if k.startswith("feeType"):
                            fee_obj[k] = v
                        else:
                            new_price[k] = v
                    
                    if fee_obj:
                        new_price["fee"] = fee_obj
                        
                    processed_prices.append(new_price)
                
                new_ticket = dict(ticket)
                new_ticket["prices"] = processed_prices
                processed_tickets.append(new_ticket)
                
            new_out_item = dict(out_item)
            new_out_item["tickets"] = processed_tickets
            merged_dict[osm_id]["out"].append(new_out_item)

    # Convert to list
    final_data = list(merged_dict.values())

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    # Final Validation Counters
    final_distinct_osmId = len(set(item['osmId'] for item in final_data if 'osmId' in item))
    final_total_osmIdOut = 0
    final_total_tickets = 0
    final_total_prices = 0

    for item in final_data:
        for out_item in item.get("out", []):
            final_total_osmIdOut += 1
            for ticket in out_item.get("tickets", []):
                final_total_tickets += 1
                for price in ticket.get("prices", []):
                    final_total_prices += 1

    print("--- VALIDATION REPORT ---")
    print(f"Distinct osmId: Initial = {init_distinct_osmId}, Final = {final_distinct_osmId} -> {'OK' if init_distinct_osmId == final_distinct_osmId else 'MISMATCH'}")
    print(f"Total osmIdOut: Initial = {init_total_osmIdOut}, Final = {final_total_osmIdOut} -> {'OK' if init_total_osmIdOut == final_total_osmIdOut else 'MISMATCH'}")
    print(f"Total tickets:  Initial = {init_total_tickets}, Final = {final_total_tickets} -> {'OK' if init_total_tickets == final_total_tickets else 'MISMATCH'}")
    print(f"Total prices:   Initial = {init_total_prices}, Final = {final_total_prices} -> {'OK' if init_total_prices == final_total_prices else 'MISMATCH'}")
    
    if (init_distinct_osmId == final_distinct_osmId and
        init_total_osmIdOut == final_total_osmIdOut and
        init_total_tickets == final_total_tickets and
        init_total_prices == final_total_prices):
        print("\nSUCCESS: All data matched perfectly. Restructuring completed.")
        print(f"Saved to: {output_file}")
    else:
        print("\nWARNING: Data mismatch found!")

if __name__ == "__main__":
    input_path = Path(r"ticket_submission.json")
    output_path = Path(r"final_ticket_submission.json")
    process_tickets(input_path, output_path)
