import pandas as pd
import glob
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import os
import json
import unicodedata

def normalize_string(s):
    if pd.isna(s) or s is None:
        return ""
    # Chuyển về dạng NFC, bỏ khoảng trắng thừa 2 đầu, chuyển chữ thường
    s = str(s)
    return unicodedata.normalize('NFC', s).strip().lower()

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Đọc unique_stations.csv
    unique_stations_path = os.path.join(root_dir, 'origin_csv', 'unique_stations.csv')
    try:
        df_unique = pd.read_csv(unique_stations_path)
        if 'stationName' not in df_unique.columns:
            print(f"Lỗi: Không tìm thấy cột 'stationName' trong {unique_stations_path}")
            return
        unique_stations = df_unique['stationName'].dropna().unique().tolist()
    except Exception as e:
        print(f"Lỗi khi đọc unique_stations.csv: {e}")
        return

    # 2. Đọc các file routes/*/merged_*.csv
    routes_dir = os.path.join(root_dir, 'routes')
    # Lấy các file merged_*.csv trong tất cả các thư mục con của routes/
    merged_files = glob.glob(os.path.join(routes_dir, '*', 'merged_*.csv'))
    
    epass_names = set()
    for file_path in merged_files:
        try:
            df = pd.read_csv(file_path)
            if 'epass_name' in df.columns:
                # Lọc distinct
                names = df['epass_name'].dropna().unique().tolist()
                epass_names.update(names)
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {e}")

    # 3. Tạo mapping dictionaries
    # Dictionary chứa name đã chuẩn hóa
    norm_to_orig_unique = {normalize_string(name): name for name in unique_stations}
    norm_to_orig_epass = {normalize_string(name): name for name in epass_names}

    mapping = {}
    matched_epass = set()

    # So khớp các stationName có trong unique_stations
    for orig_unique_name in unique_stations:
        norm_unique = normalize_string(orig_unique_name)
        stripped_unique = str(orig_unique_name).strip()
        if norm_unique in norm_to_orig_epass:
            orig_epass = norm_to_orig_epass[norm_unique]
            mapping[stripped_unique] = str(orig_epass).strip()
            matched_epass.add(norm_unique)
        else:
            mapping[stripped_unique] = None
    
    # Gán các giá trị epass_name chưa được so khớp với keys là các chuỗi số
    unmatched_epass = [str(orig).strip() for norm, orig in norm_to_orig_epass.items() if norm not in matched_epass]
    
    unmatched_count = 0
    for epass in unmatched_epass:
        mapping[str(unmatched_count)] = epass
        unmatched_count += 1

    # 4. Lưu ra mapping.json ở root
    mapping_path = os.path.join(root_dir, 'mapping.json')
    try:
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)
        print(f"Đã lưu thành công file mapping tại: {mapping_path}")
    except Exception as e:
        print(f"Lỗi khi lưu file {mapping_path}: {e}")

if __name__ == "__main__":
    main()
