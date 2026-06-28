import pandas as pd
import json
from pathlib import Path

def main():
    base_dir = Path(__file__).parent.parent
    
    # --- THỐNG KÊ CSV ---
    csv_path = base_dir / 'origin_csv/tram_thu_phi_complete_epass.csv'
    df = pd.read_csv(csv_path)
    
    csv_total_rows = len(df)
    csv_null_osm_id = df['osm_id'].isna().sum()
    
    csv_names = set()
    for name in df['epass_name']:
        if pd.notna(name):
            n = str(name).strip()
            if n:
                csv_names.add(n)
                
    # --- THỐNG KÊ JSON ---
    json_names = set()
    
    # nodes.json
    nodes_path = base_dir / 'nodes.json'
    nodes_total = 0
    nodes_null_osm = 0
    if nodes_path.exists():
        with open(nodes_path, 'r', encoding='utf-8') as f:
            nodes = json.load(f)
            nodes_total = len(nodes)
            for node in nodes:
                if node.get("stationOsmId") is None:
                    nodes_null_osm += 1
                n = node.get("stationName", "").strip()
                if n: json_names.add(n)
                    
    # edges.json
    edges_path = base_dir / 'edges.json'
    edges_total = 0
    edges_null_osm = 0
    if edges_path.exists():
        with open(edges_path, 'r', encoding='utf-8') as f:
            edges = json.load(f)
            edges_total = len(edges)
            for edge in edges:
                if edge.get("sourceOsmId") is None or edge.get("targetOsmId") is None:
                    edges_null_osm += 1
                src = edge.get("source", "").strip()
                tgt = edge.get("target", "").strip()
                if src: json_names.add(src)
                if tgt: json_names.add(tgt)
                
    # tickets.json
    tickets_path = base_dir / 'tickets.json'
    tickets_total = 0
    tickets_null_osm = 0
    if tickets_path.exists():
        with open(tickets_path, 'r', encoding='utf-8') as f:
            tickets = json.load(f)
            tickets_total = len(tickets)
            for ticket in tickets:
                osm_id_val = ticket.get("osmId")
                # Trong tickets.json, osmId có thể là null (None), chuỗi, hoặc mảng [None, None]
                if osm_id_val is None:
                    tickets_null_osm += 1
                elif isinstance(osm_id_val, list) and (osm_id_val[0] is None or osm_id_val[1] is None):
                    # Nâng cao: Đếm null nếu mảng có chứa null
                    tickets_null_osm += 1
                    
                ref_type = ticket.get("refType")
                ref_id = ticket.get("refId")
                if ref_type == "NODE" and isinstance(ref_id, str):
                    n = ref_id.strip()
                    if n: json_names.add(n)
                elif ref_type == "EDGE" and isinstance(ref_id, list):
                    for r in ref_id:
                        n = str(r).strip()
                        if n: json_names.add(n)
                        
    # --- Tính toán chênh lệch ---
    in_json_not_in_csv = json_names - csv_names
    in_csv_not_in_json = csv_names - json_names
    
    # --- IN BÁO CÁO ---
    print("\n" + "=" * 80)
    print("BÁO CÁO CHI TIẾT DỮ LIỆU JSON VÀ CSV".center(80))
    print("=" * 80)
    
    print("[1] TỔNG QUAN TỆP CSV")
    print(f"  - Tổng số dòng trong CSV: {csv_total_rows}")
    print(f"  - Tổng số tên trạm (cột epass_name unique): {len(csv_names)}")
    print(f"  - Số dòng bị thiếu (NULL) cột osm_id: {csv_null_osm_id}")
    print("-" * 80)
    
    print("[2] TỔNG QUAN CÁC TỆP JSON")
    print(f"  - Tổng số tên trạm (unique) gom từ 3 tệp JSON: {len(json_names)}")
    print(f"  * nodes.json:")
    print(f"    + Tổng số object: {nodes_total}")
    print(f"    + Số object có stationOsmId bị NULL: {nodes_null_osm}")
    print(f"  * edges.json:")
    print(f"    + Tổng số object: {edges_total}")
    print(f"    + Số object có sourceOsmId hoặc targetOsmId bị NULL: {edges_null_osm}")
    print(f"  * tickets.json:")
    print(f"    + Tổng số object: {tickets_total}")
    print(f"    + Số object có osmId bị NULL (hoặc chứa mảng có NULL): {tickets_null_osm}")
    print("-" * 80)
    
    print(f"[3] CHÊNH LỆCH TÊN TRẠM GIỮA JSON VÀ CSV")
    print(f"[!] CÓ TRONG JSON NHƯNG THIẾU BÊN CSV ({len(in_json_not_in_csv)} trạm):")
    if in_json_not_in_csv:
        for name in sorted(in_json_not_in_csv):
            print(f"  - {name}")
    else:
        print("  (Không có)")
        
    print()
    print(f"[!] CÓ TRONG CSV NHƯNG KHÔNG ĐƯỢC DÙNG TRONG JSON ({len(in_csv_not_in_json)} trạm):")
    if in_csv_not_in_json:
        for name in sorted(in_csv_not_in_json):
            print(f"  - {name}")
    else:
        print("  (Không có)")
    print("=" * 80)

if __name__ == '__main__':
    main()
