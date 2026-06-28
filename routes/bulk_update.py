import os
from pathlib import Path
import re

ROUTES_DIR = Path(r"d:\A-VinVSF\vehicle_routing_valhalla\routes")

TEMPLATE_00 = """import json
import pandas as pd
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def normalize_json_data(data):
    if isinstance(data, dict):
        return {k: normalize_json_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_json_data(item) for item in data]
    elif isinstance(data, str):
        return unicodedata.normalize("NFC", data.strip())
    else:
        return data

def main():
    print("===== BẮT ĐẦU CHUẨN HÓA DỮ LIỆU (NFC) =====")

    csv_file = SCRIPT_DIR / f"merged_{SCRIPT_DIR.name}.csv"
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: unicodedata.normalize("NFC", str(x).strip()) if isinstance(x, str) else x)
        df.to_csv(csv_file, index=False, encoding="utf-8")
        print(f" Đã chuẩn hóa: {csv_file.name}")

    json_files = ["edges.json", "tickets.json", "nodes.json"]
    for jf in json_files:
        path = SCRIPT_DIR / jf
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            norm_data = normalize_json_data(data)
            
            with open(path, "w", encoding="utf-8") as f:
                json.dump(norm_data, f, ensure_ascii=False, indent=4)
            print(f" Đã chuẩn hóa: {jf}")

    print("===== HOÀN THÀNH CHUẨN HÓA =====")

if __name__ == "__main__":
    main()
"""

for route_dir in ROUTES_DIR.iterdir():
    if not route_dir.is_dir():
        continue
    
    # 1. Write 00_normalize_data.py
    py_path = route_dir / "00_normalize_data.py"
    with open(py_path, "w", encoding="utf-8") as f:
        f.write(TEMPLATE_00)
        
    # 2. Update run_pipeline.bat
    bat_path = route_dir / "run_pipeline.bat"
    if bat_path.exists():
        with open(bat_path, "r", encoding="utf-8") as f:
            bat_content = f.read()
        
        if "00_normalize_data.py" not in bat_content:
            # Insert before File 1
            replacement = """:: File 0 (Chuẩn hóa)
echo Chạy 00_normalize_data.py...
python "00_normalize_data.py"
echo Đang chờ 3 giây...
ping 127.0.0.1 -n 4 > nul
echo ------------------------------------------

:: File 1"""
            bat_content = bat_content.replace(":: File 1", replacement)
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
                
    # 3. Update run_pipeline.sh
    sh_path = route_dir / "run_pipeline.sh"
    if sh_path.exists():
        with open(sh_path, "r", encoding="utf-8") as f:
            sh_content = f.read()
            
        if "00_normalize_data.py" not in sh_content:
            sh_content = sh_content.replace(
                'run_script "01_build_station_tree.py"',
                'run_script "00_normalize_data.py"\nrun_script "01_build_station_tree.py"'
            )
            with open(sh_path, "w", encoding="utf-8", newline='\n') as f:
                f.write(sh_content)
                
print("DONE updating all directories.")
