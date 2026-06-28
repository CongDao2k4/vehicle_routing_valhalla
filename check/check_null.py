import pandas as pd
import json
import os
from pathlib import Path

def check_csv(tickets, base_dir, log_file):
    csv_path = base_dir / 'origin_csv/tram_thu_phi_complete_epass.csv'
    df = pd.read_csv(csv_path)
    valid_epass_names = set()
    for name in df['epass_name'].dropna():
        clean_name = str(name).strip()
        if clean_name:
            valid_epass_names.add(clean_name)
            
    unmapped_names = set()
    for ticket in tickets:
        ref_type = ticket.get("refType")
        ref_ids = ticket.get("refId")
        osm_ids = ticket.get("osmId")
        
        if ref_type == "NODE":
            if osm_ids is None:
                name = str(ref_ids).strip() if ref_ids else ""
                if name and name not in valid_epass_names:
                    unmapped_names.add(name)
                    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("=== 1. CHECK TICKET NULL OSM_ID VS CSV ===\n")
        if unmapped_names:
            for name in sorted(unmapped_names):
                f.write(f"- Missing in CSV: {name}\n")
        else:
            f.write("- All null osmId tickets have matching epass_name in CSV.\n")
        f.write("\n")
    print("Checked CSV.")

def check_nodes(tickets, base_dir, log_file):
    nodes_path = base_dir / 'nodes.json'
    with open(nodes_path, 'r', encoding='utf-8') as f:
        nodes = json.load(f)
        
    valid_node_osm_ids = set()
    for node in nodes:
        node_id = node.get("stationOsmId")
        if node_id:
            valid_node_osm_ids.add(str(node_id).strip())
            
    unmapped_nodes = set()
    for ticket in tickets:
        if ticket.get("refType") == "NODE":
            osm_ids = ticket.get("osmId")
            ref_id = ticket.get("refId")
            if osm_ids:
                if isinstance(osm_ids, list) and len(osm_ids) > 0:
                    osm_id = str(osm_ids[0]).strip()
                else:
                    osm_id = str(osm_ids).strip()
                    
                if osm_id not in valid_node_osm_ids:
                    name = str(ref_id).strip() if ref_id else "Unknown"
                    unmapped_nodes.add(f"'{name}' (osmId: {osm_id})")
                    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("=== 2. CHECK TICKET NODE VS NODES.JSON ===\n")
        if unmapped_nodes:
            for n in sorted(unmapped_nodes):
                f.write(f"- Ticket NODE missing in nodes.json: {n}\n")
        else:
            f.write("- All ticket NODE osmId exist in nodes.json.\n")
        f.write("\n")
    print("Checked Nodes.")

def check_edges(tickets, base_dir, log_file):
    edges_path = base_dir / 'edges.json'
    with open(edges_path, 'r', encoding='utf-8') as f:
        edges = json.load(f)
        
    valid_edge_pairs = set()
    for edge in edges:
        s_id = edge.get("sourceOsmId")
        t_id = edge.get("targetOsmId")
        if s_id and t_id:
            valid_edge_pairs.add(f"{str(s_id).strip()}_{str(t_id).strip()}")
            
    unmapped_edges = set()
    for ticket in tickets:
        if ticket.get("refType") == "EDGE":
            osm_ids = ticket.get("osmId")
            ref_ids = ticket.get("refId")
            if osm_ids and len(osm_ids) >= 2:
                s_id = str(osm_ids[0]).strip()
                t_id = str(osm_ids[1]).strip()
                if f"{s_id}_{t_id}" not in valid_edge_pairs:
                    source_name = str(ref_ids[0]).strip() if (ref_ids and len(ref_ids) >= 2) else "Unknown"
                    target_name = str(ref_ids[1]).strip() if (ref_ids and len(ref_ids) >= 2) else "Unknown"
                    unmapped_edges.add(f"'{source_name} -> {target_name}' (osmIds: {s_id} -> {t_id})")
                    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("=== 3. CHECK TICKET EDGE VS EDGES.JSON ===\n")
        if unmapped_edges:
            for e in sorted(unmapped_edges):
                f.write(f"- Ticket EDGE missing in edges.json: {e}\n")
        else:
            f.write("- All ticket EDGE pairs exist in edges.json.\n")
        f.write("\n")
    print("Checked Edges.")

def main():
    base_dir = Path(__file__).parent.parent
    tickets_path = base_dir / 'tickets.json'
    
    # Tạo thư mục log nếu chưa có
    log_dir = base_dir / 'log'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'check_tickets.log'
    
    # Xóa log cũ
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("")
        
    print(f"Reading tickets from: {tickets_path}")
    with open(tickets_path, 'r', encoding='utf-8') as f:
        tickets = json.load(f)
        
    check_csv(tickets, base_dir, log_file)
    check_nodes(tickets, base_dir, log_file)
    check_edges(tickets, base_dir, log_file)
    
    print(f"All checks completed. See logs at: {log_file}")

if __name__ == "__main__":
    main()
