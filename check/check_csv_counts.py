import json
import csv
import sys
from pathlib import Path

# Cấu hình UTF-8 cho console Windows
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(r"/data_complete_valhalla")
NODES_PATH = BASE_DIR / "nodes.json"
ROUTES_DIR = BASE_DIR / "routes"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    print("========================================")
    print("KIỂM KÊ SỐ LƯỢNG TRẠM TRONG CÁC FILE CSV")
    print("========================================")
    
    # 1. Đếm trong nodes.json
    try:
        nodes_data = load_json(NODES_PATH)
        # Bỏ qua các node rỗng nếu có
        total_in_json = len([n for n in nodes_data if n.get('stationName')])
        print(f"Tổng số trạm trong nodes.json: {total_in_json}")
    except Exception as e:
        print(f"Lỗi khi đọc nodes.json: {e}")
        return

    # 2. Đếm trong thư mục routes/
    total_in_csv = 0
    route_files_count = 0
    indep_count = 0
    unique_stations_in_csv = set()
    stations_in_routes_map = {}
    
    print("\n--- Chi tiết từng file CSV ---")
    
    if not ROUTES_DIR.exists():
        print(f"Không tìm thấy thư mục {ROUTES_DIR}")
        return
        
    for csv_file in ROUTES_DIR.glob("*.csv"):
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    count += 1
                    epass_name = row.get('epass_name', '').strip()
                    if epass_name:
                        unique_stations_in_csv.add(epass_name)
                        if csv_file.name != "Independent_Nodes.csv":
                            if epass_name not in stations_in_routes_map:
                                stations_in_routes_map[epass_name] = []
                            stations_in_routes_map[epass_name].append(csv_file.name)
                            
                total_in_csv += count
                
                # In chi tiết
                if csv_file.name == "Independent_Nodes.csv":
                    indep_count = count
                    print(f"- [Độc lập] {csv_file.name:<30}: {count} dòng")
                else:
                    route_files_count += 1
                    print(f"- [Tuyến]    {csv_file.name:<30}: {count} dòng")
        except Exception as e:
            print(f"Lỗi khi đọc file {csv_file.name}: {e}")

    # Tìm các trạm thuộc nhiều tuyến
    multi_route_stations = {k: v for k, v in stations_in_routes_map.items() if len(v) > 1}

    print("\n========================================")
    print("TỔNG KẾT:")
    print(f"- Số file tuyến đường : {route_files_count}")
    print(f"- Tổng số dòng trong các CSV tuyến : {total_in_csv - indep_count}")
    print(f"- Tổng số dòng trong CSV độc lập   : {indep_count}")
    print(f"- TỔNG CỘNG SỐ DÒNG (CSV)          : {total_in_csv}")
    print(f"- SỐ TRẠM UNIQUE TRONG CÁC CSV     : {len(unique_stations_in_csv)}")
    print("========================================")
    
    if len(multi_route_stations) > 0:
        print("\n[!] Chú ý: Phát hiện các trạm NẰM Ở NHIỀU TUYẾN ĐƯỜNG (Giao cắt):")
        for st, routes in multi_route_stations.items():
            print(f"  + Trạm '{st}' thuộc {len(routes)} tuyến: {', '.join(routes)}")
            
    if len(unique_stations_in_csv) == total_in_json:
        print("\n>>> KẾT LUẬN: KHỚP 100% HOÀN HẢO! Tổng số trạm Unique trong CSV bằng đúng số lượng trong nodes.json.")
    else:
        print(f"\n>>> KẾT LUẬN: BỊ LỆCH MẤT {abs(len(unique_stations_in_csv) - total_in_json)} TRẠM! Cần kiểm tra lại.")
        
        json_station_names = set(n.get('stationName') for n in nodes_data if n.get('stationName'))
        extra_in_csv = unique_stations_in_csv - json_station_names
        missing_in_csv = json_station_names - unique_stations_in_csv
        
        if extra_in_csv:
            print("\n[!] CÁC TRẠM CÓ TRONG CSV (từ edges) NHƯNG KHÔNG CÓ TRONG nodes.json:")
            for s in extra_in_csv:
                print(f"  - {s}")
        if missing_in_csv:
            print("\n[!] CÁC TRẠM CÓ TRONG nodes.json NHƯNG KHÔNG ĐƯỢC XUẤT RA CSV:")
            for s in missing_in_csv:
                print(f"  - {s}")

if __name__ == "__main__":
    main()
