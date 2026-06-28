import os
import sys
import json
from pathlib import Path

# Fix Windows console utf-8 print issues
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    routes_dir = Path(r"routes")
    output_file = Path(r"ticket_submission_restricted.json")
    
    subdirs = [d for d in routes_dir.iterdir() if d.is_dir()]
    
    has_ticket = []
    missing_ticket = []
    merged_data = []
    
    for d in subdirs:
        ticket_file = d / "ticket_submission_restricted.json"
        if ticket_file.exists():
            has_ticket.append(d.name)
            try:
                with open(ticket_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    merged_data.extend(data)
            except Exception as e:
                print(f"Error reading file {ticket_file}: {e}")
        else:
            missing_ticket.append(d.name)
            
    print(f"Total subdirectories: {len(subdirs)}")
    print(f"Directories WITH ticket_submission_restricted.json: {len(has_ticket)}")
    print(f"Directories WITHOUT ticket_submission_restricted.json: {len(missing_ticket)}")
    
    if missing_ticket:
        print("\n--- DIRECTORIES WITHOUT ticket_submission_restricted.json ---")
        for m in missing_ticket:
            print(f" - {m}")
            
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=4)
        
    print(f"\nSuccessfully merged into: {output_file}")
    print(f"Total objects in merged file: {len(merged_data)}")

if __name__ == '__main__':
    main()
