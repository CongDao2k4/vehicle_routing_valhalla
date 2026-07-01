import os
import json
import shutil
import subprocess
import sys
import io

# Force stdout to output UTF-8 to prevent encoding issues in Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

dir_path = os.path.dirname(os.path.abspath(__file__))
gia_ve_path = os.path.join(dir_path, "new_epass", "gia_ve.json")
backup_path = os.path.join(dir_path, "new_epass", "gia_ve.json.bak")

# 1. Backup original file
print("Backing up gia_ve.json...")
shutil.copy(gia_ve_path, backup_path)

try:
    # 2. Read and parse original
    with open(gia_ve_path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if content.startswith("["):
            records = json.loads(content)
        else:
            if content.endswith(","):
                content = content[:-1]
            records = json.loads("[" + content + "]")

    # 3. Apply changes for testing
    print("Modifying records for testing...")
    
    # Change price: modify first record (Cao Bồ - Liêm Tuyền) feeType1 from 48160 to 50000
    for r in records:
        if r.get("stageName") == "Cao Bồ - Liêm Tuyền" and r.get("ticketType") == 1:
            print(f"-> Modifying feeType1 of Cao Bồ - Liêm Tuyền: {r['feeType1']} -> 50000")
            r["feeType1"] = 50000
            
            # Deletion Test 3: Delete feeType5 from this record to test field deletion detection
            print("-> Deleting feeType5 from Cao Bồ - Liêm Tuyền record")
            del r["feeType5"]
            break

    # Deletion Test 1: Delete all records for EDGE "Cao Bồ - Vực Vòng"
    original_len = len(records)
    records = [r for r in records if r.get("stageName") != "Cao Bồ - Vực Vòng"]
    print(f"-> Deletion Test 1: Removed EDGE 'Cao Bồ - Vực Vòng' records (removed {original_len - len(records)} entries)")

    # Deletion Test 2: Delete ticketType 5 (Vé quý) from "Cầu Giẽ Hà Nam - Pháp Vân"
    original_len = len(records)
    records = [r for r in records if not (r.get("stageName") == "Cầu Giẽ Hà Nam - Pháp Vân" and r.get("ticketType") == 5)]
    print(f"-> Deletion Test 2: Removed ticketType 5 (Vé quý) from 'Cầu Giẽ Hà Nam - Pháp Vân' (removed {original_len - len(records)} entries)")

    # Add a new CLOSED edge ticket with a new station "Nút Giao Thử Nghiệm"
    new_edge_ticket = {
        "ticketType": 1,
        "ticketTypeName": "Vé lượt",
        "routeName": "Cao tốc Pháp Vân – Cầu Giẽ",
        "stationType": 0,
        "stationTypeName": "CLOSED",
        "stageName": "Cao Bồ - Nút Giao Thử Nghiệm",
        "stationInName": "Cao Bồ",
        "stationOutName": "Nút Giao Thử Nghiệm",
        "priceType": 1,
        "priceTypeName": "Giá thường",
        "feeType1": 10000,
        "feeType2": 15000,
        "feeType3": 20000,
        "feeType4": 25000,
        "feeType5": 30000
    }
    records.append(new_edge_ticket)
    print("-> Added new EDGE: Cao Bồ -> Nút Giao Thử Nghiệm")

    # Add a new OPEN node ticket with a new station "Trạm Thu Phí Thử Nghiệm"
    new_node_ticket = {
        "ticketType": 1,
        "ticketTypeName": "Vé lượt",
        "routeName": "Cao tốc Pháp Vân – Cầu Giẽ",
        "stationType": 1,
        "stationTypeName": "OPEN",
        "stationName": "Trạm Thu Phí Thử Nghiệm",
        "priceType": 1,
        "priceTypeName": "Giá thường",
        "feeType1": 12000,
        "feeType2": 18000,
        "feeType3": 24000,
        "feeType4": 30000,
        "feeType5": 40000
    }
    records.append(new_node_ticket)
    print("-> Added new NODE: Trạm Thu Phí Thử Nghiệm")

    # Save modified json
    with open(gia_ve_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=4)

    # 4. Run build_graph.py
    print("\nRunning build_graph.py with modified data...")
    result = subprocess.run(["python", os.path.join(dir_path, "build_graph.py")], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(result.stdout)
    if result.stderr:
        print("Error details:")
        print(result.stderr)

finally:
    # 5. Restore original file
    print("Restoring original gia_ve.json...")
    shutil.move(backup_path, gia_ve_path)
    print("Restore complete.")
    
    # 6. Re-run build_graph.py to restore nodes.json, edges.json, tickets.json original state
    print("\nRestoring original graph files (nodes.json, edges.json, tickets.json)...")
    subprocess.run(["python", os.path.join(dir_path, "build_graph.py")], capture_output=True)
    print("Restore of graph files complete.")
