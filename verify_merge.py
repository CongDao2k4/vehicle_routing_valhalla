import json
from pathlib import Path

def main():
    routes_dir = Path(r"routes")
    merged_file = Path(r"ticket_submission.json")
    
    subdirs = [d for d in routes_dir.iterdir() if d.is_dir()]
    
    total_from_subs = 0
    
    print(f"{'THƯ MỤC':<40} | {'SỐ LƯỢNG OBJECT':<15}")
    print("-" * 60)
    
    for d in subdirs:
        ticket_file = d / "ticket_submission.json"
        if ticket_file.exists():
            try:
                with open(ticket_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    count = len(data)
                    total_from_subs += count
                    print(f"{d.name:<40} | {count:<15}")
            except Exception as e:
                print(f"{d.name:<40} | LỖI: {e}")
                
    print("-" * 60)
    print(f"{'TỔNG CỘNG TỪ CÁC THƯ MỤC CON':<40} | {total_from_subs:<15}")
    
    if merged_file.exists():
        with open(merged_file, "r", encoding="utf-8") as f:
            merged_data = json.load(f)
            merged_count = len(merged_data)
        
        print(f"{'TỔNG SỐ OBJECT TRONG FILE MERGED':<40} | {merged_count:<15}")
        print("=" * 60)
        
        if total_from_subs == merged_count:
            print("✅ KHỚP NHAU 100%! Việc merge đã thực hiện đúng, không sót dữ liệu.")
        else:
            print(f"❌ CÓ SỰ SAI LỆCH! Thiếu/Thừa {abs(total_from_subs - merged_count)} objects.")
    else:
        print("Không tìm thấy file ticket_submission.json để đối chiếu.")

if __name__ == '__main__':
    # Fix console encoding on Windows to prevent Unicode error when printing emojis or Vietnamese chars
    import sys
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    main()
