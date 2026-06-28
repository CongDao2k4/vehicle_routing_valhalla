import json
from pathlib import Path

def count_items(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return len(data)
    except FileNotFoundError:
        return "File not found"
    except json.JSONDecodeError:
        return "Invalid JSON"
    except Exception as e:
        return f"Error: {e}"

def main():
    base_dir = Path(__file__).parent
    
    files_to_check = {
        "Nodes": base_dir / "nodes.json",
        "Edges": base_dir / "edges.json",
        "Tickets": base_dir / "tickets.json"
    }
    
    print("=" * 40)
    print("STATISTICS OF JSON FILES")
    print("=" * 40)
    
    for name, path in files_to_check.items():
        count = count_items(path)
        print(f"- {name:<10}: {count}")
        
    print("=" * 40)

if __name__ == "__main__":
    main()
