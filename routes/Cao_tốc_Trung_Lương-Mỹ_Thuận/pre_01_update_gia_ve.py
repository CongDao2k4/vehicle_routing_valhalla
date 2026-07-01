import sys
import os
import json
import unicodedata

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def normalize_string(s):
    if s is None:
        return ""
    s = str(s)
    return unicodedata.normalize('NFC', s).strip().lower()

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(os.path.dirname(script_dir))
    
    mapping_path = os.path.join(root_dir, 'mapping.json')
    gia_ve_path = os.path.join(script_dir, 'new_epass', 'gia_ve.json')
    
    if not os.path.exists(mapping_path):
        print(f"Lỗi: Không tìm thấy {mapping_path}")
        return
        
    if not os.path.exists(gia_ve_path):
        print(f"Lỗi: Không tìm thấy {gia_ve_path}")
        return
        
    with open(mapping_path, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
        
    with open(gia_ve_path, 'r', encoding='utf-8') as f:
        gia_ve_data = json.load(f)
        
    # Tạo bản đồ tìm kiếm với key chuẩn hóa
    norm_to_key = {}
    for k, v in mapping.items():
        norm_k = normalize_string(k)
        norm_to_key[norm_k] = k

    tickets_to_keep = []
    mapping_updated = False
    
    for ticket in gia_ve_data:
        in_name = ticket.get("stationInName", "")
        out_name = ticket.get("stationOutName", "")
        
        norm_in = normalize_string(in_name)
        norm_out = normalize_string(out_name)
        
        delete_ticket = False
        
        # Xử lý stationInName
        if norm_in in norm_to_key:
            orig_key = norm_to_key[norm_in]
            val = mapping[orig_key]
            if val is None:
                delete_ticket = True
            else:
                ticket["stationInName"] = str(val).strip()
        else:
            # Không tìm thấy -> dữ liệu mới
            mapping[in_name.strip()] = in_name.strip()
            norm_to_key[norm_in] = in_name.strip()
            mapping_updated = True
            
        # Xử lý stationOutName
        if norm_out in norm_to_key:
            orig_key = norm_to_key[norm_out]
            val = mapping[orig_key]
            if val is None:
                delete_ticket = True
            else:
                ticket["stationOutName"] = str(val).strip()
        else:
            # Không tìm thấy -> dữ liệu mới
            mapping[out_name.strip()] = out_name.strip()
            norm_to_key[norm_out] = out_name.strip()
            mapping_updated = True
            
        if not delete_ticket:
            tickets_to_keep.append(ticket)
            
    # Cập nhật gia_ve.json
    with open(gia_ve_path, 'w', encoding='utf-8') as f:
        json.dump(tickets_to_keep, f, ensure_ascii=False, indent=4)
        
    print(f"Đã cập nhật xong {gia_ve_path}. Giữ lại {len(tickets_to_keep)}/{len(gia_ve_data)} vé.")
    
    # Cập nhật mapping.json nếu có dữ liệu mới
    if mapping_updated:
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=4)
        print(f"Đã cập nhật {mapping_path} với các trạm mới.")

if __name__ == "__main__":
    main()
