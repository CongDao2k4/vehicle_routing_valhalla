import json
import pandas as pd
import unicodedata
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def normalize_json_data(data):
    """Đệ quy để chuẩn hóa toàn bộ chuỗi trong cấu trúc JSON."""
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

    # 1. Chuẩn hóa file CSV
    csv_file = SCRIPT_DIR / "merged_Mai Sơn - Quốc Lộ 45.csv"
    if csv_file.exists():
        df = pd.read_csv(csv_file)
        # Áp dụng chuẩn hóa cho các cột có kiểu dữ liệu là string (object)
        for col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].apply(lambda x: unicodedata.normalize("NFC", str(x).strip()) if isinstance(x, str) else x)
        df.to_csv(csv_file, index=False, encoding="utf-8")
        print(f" Đã chuẩn hóa: {csv_file.name}")

    # 2. Chuẩn hóa các file JSON
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
