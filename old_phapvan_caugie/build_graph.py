import os
import json
import sys
import io

# Force stdout to output UTF-8 to prevent encoding issues in Windows terminal
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

base_dir = os.path.dirname(os.path.abspath(__file__))

# Recursive string strip utility
def strip_strings(obj):
    if isinstance(obj, dict):
        return {k.strip() if isinstance(k, str) else k: strip_strings(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [strip_strings(x) for x in obj]
    elif isinstance(obj, str):
        return obj.strip()
    return obj

# Path references
old_nodes_path = os.path.join(base_dir, "nodes.json")
old_edges_path = os.path.join(base_dir, "edges.json")
old_tickets_path = os.path.join(base_dir, "tickets.json")

# 1. Load Old Data for Preservation & Comparison
old_nodes = {}
if os.path.exists(old_nodes_path):
    with open(old_nodes_path, "r", encoding="utf-8") as f:
        try:
            items = strip_strings(json.load(f))
            for item in items:
                old_nodes[item["stationName"]] = item
        except Exception as e:
            print(f"Warning: could not load old nodes: {e}")

old_edges = {}
if os.path.exists(old_edges_path):
    with open(old_edges_path, "r", encoding="utf-8") as f:
        try:
            items = strip_strings(json.load(f))
            for item in items:
                key = (item["source"], item["target"])
                old_edges[key] = item
        except Exception as e:
            print(f"Warning: could not load old edges: {e}")

old_tickets = {}
if os.path.exists(old_tickets_path):
    with open(old_tickets_path, "r", encoding="utf-8") as f:
        try:
            items = strip_strings(json.load(f))
            for item in items:
                ref_type = item.get("refType")
                ref_id = item.get("refId")
                if ref_type == "EDGE":
                    key = ("EDGE", tuple(ref_id))
                else:
                    key = ("NODE", ref_id)
                old_tickets[key] = item
        except Exception as e:
            print(f"Warning: could not load old tickets: {e}")

# Build structures
nodes_dict = {}
edges_dict = {}
tickets_dict = {} # key -> { ticketType: { ... prices: { priceType: {...} } } }
new_stations_set = set()

def get_node(name):
    if name not in nodes_dict:
        # Default properties
        lat = None
        lon = None
        osm_id = None
        
        # Preserve from old if matches
        if name in old_nodes:
            lat = old_nodes[name].get("latitude")
            lon = old_nodes[name].get("longitude")
            osm_id = old_nodes[name].get("stationOsmId")
        else:
            new_stations_set.add(name)
            
        nodes_dict[name] = {
            "stationName": name,
            "stationType": 0,
            "stationTypeName": "CLOSED",
            "latitude": lat,
            "longitude": lon,
            "stationOsmId": osm_id,
            "incoming_edges": set(),
            "outgoing_edges": set()
        }
    return nodes_dict[name]

def process_ticket(ref_type, ref_id_key, ref_id_val, record):
    if ref_id_key not in tickets_dict:
        tickets_dict[ref_id_key] = {
            "refType": ref_type,
            "refId": ref_id_val,
            "tickets_map": {}
        }
    
    t_map = tickets_dict[ref_id_key]["tickets_map"]
    t_type = record.get("ticketType")
    
    if t_type is None:
        return
        
    if t_type not in t_map:
        t_map[t_type] = {
            "ticketType": t_type,
            "ticketTypeName": record.get("ticketTypeName"),
            "prices_map": {}
        }
        
    p_map = t_map[t_type]["prices_map"]
    p_type = record.get("priceType")
    
    if p_type is not None and p_type not in p_map:
        price_obj = {
            "priceType": p_type,
            "priceTypeName": record.get("priceTypeName")
        }
        for k, v in record.items():
            if k.startswith("feeType"):
                price_obj[k] = v
                
        p_map[p_type] = price_obj

# 2. Parse new gia_ve.json input
gia_ve_path = os.path.join(base_dir, "new_epass", "gia_ve.json")
if not os.path.exists(gia_ve_path):
    raise FileNotFoundError(f"Source file not found at: {gia_ve_path}")

with open(gia_ve_path, "r", encoding="utf-8") as f:
    content = f.read().strip()

# Check wrapper and parse robustly
if content.startswith("["):
    records = strip_strings(json.loads(content))
else:
    # Wrap it if missing brackets
    if content.endswith(","):
        content = content[:-1]
    content = "[" + content + "]"
    records = strip_strings(json.loads(content))

# Process records
for record in records:
    s_type = record.get("stationType")
    
    if s_type == 1:
        # OPEN
        name = record.get("stationName").strip()
        if not name: continue
        node = get_node(name)
        node["stationType"] = 1
        node["stationTypeName"] = "OPEN"
        
        process_ticket("NODE", name, name, record)
        
    elif s_type == 0:
        # CLOSED
        in_name = record.get("stationInName").strip()
        out_name = record.get("stationOutName").strip()
        if not in_name or not out_name: continue
        
        # Ensure nodes exist
        node_in = get_node(in_name)
        node_out = get_node(out_name)
        
        # Update edges list
        node_in["outgoing_edges"].add(out_name)
        node_out["incoming_edges"].add(in_name)
        
        route = record.get("routeName")
        stage = record.get("stageName")
        
        # Edge key
        edge_key = f"{in_name}||{out_name}"
        if edge_key not in edges_dict:
            src_osm = node_in["stationOsmId"] if node_in["stationOsmId"] is not None else ""
            tgt_osm = node_out["stationOsmId"] if node_out["stationOsmId"] is not None else ""
            
            edges_dict[edge_key] = {
                "source": in_name,
                "target": out_name,
                "routeName": route,
                "stageName": stage,
                "stationType": 0,
                "stationTypeName": "CLOSED",
                "sourceOsmId": src_osm,
                "targetOsmId": tgt_osm
            }
        
        ref_id_val = [in_name, out_name]
        process_ticket("EDGE", edge_key, ref_id_val, record)

# Convert sets to lists and sort for predictability
nodes_list = []
for node in nodes_dict.values():
    node["incoming_edges"] = sorted(list(node["incoming_edges"]))
    node["outgoing_edges"] = sorted(list(node["outgoing_edges"]))
    nodes_list.append(node)
nodes_list = sorted(nodes_list, key=lambda x: x["stationName"])

edges_list = list(edges_dict.values())
edges_list = sorted(edges_list, key=lambda x: (x["source"], x["target"]))

tickets_list = []
for k, v in tickets_dict.items():
    t_arr = []
    for t_val in v["tickets_map"].values():
        t_val["prices"] = list(t_val["prices_map"].values())
        t_val["prices"] = sorted(t_val["prices"], key=lambda x: x.get("priceType", 0))
        del t_val["prices_map"]
        t_arr.append(t_val)
    
    t_arr = sorted(t_arr, key=lambda x: x.get("ticketType", 0))
    
    # Resolve osmId array (for EDGE: [sourceOsmId, targetOsmId], for NODE: stationOsmId)
    osm_ids = []
    if v["refType"] == "EDGE":
        src_name = v["refId"][0]
        tgt_name = v["refId"][1]
        src_node = nodes_dict.get(src_name, {})
        tgt_node = nodes_dict.get(tgt_name, {})
        src_osm = src_node.get("stationOsmId")
        tgt_osm = tgt_node.get("stationOsmId")
        if src_osm and tgt_osm:
            osm_ids = [src_osm, tgt_osm]
    else:
        node_name = v["refId"]
        node_obj = nodes_dict.get(node_name, {})
        node_osm = node_obj.get("stationOsmId")
        if node_osm:
            osm_ids = [node_osm]
            
    tickets_list.append({
        "refType": v["refType"],
        "refId": v["refId"],
        "tickets": t_arr,
        "osmId": osm_ids
    })

def sort_ticket_key(x):
    r_type = x["refType"]
    r_id = x["refId"]
    if r_type == "EDGE":
        return ("EDGE", r_id[0], r_id[1])
    else:
        return ("NODE", r_id, "")

tickets_list = sorted(tickets_list, key=sort_ticket_key)

# Compute node, edge and ticket diffs first
# 1. Nodes Compare
new_nodes_map = {n["stationName"]: n for n in nodes_list}
added_nodes = set(new_nodes_map.keys()) - set(old_nodes.keys())
removed_nodes = set(old_nodes.keys()) - set(new_nodes_map.keys())
modified_nodes = []

for name in sorted(set(new_nodes_map.keys()) & set(old_nodes.keys())):
    old_n = old_nodes[name]
    new_n = new_nodes_map[name]
    changes = []
    for k in ["stationType", "stationTypeName"]:
        if old_n.get(k) != new_n.get(k):
            changes.append(f"{k}: {old_n.get(k)} -> {new_n.get(k)}")
    if changes:
        modified_nodes.append((name, changes))

# 2. Edges Compare
new_edges_map = {(e["source"], e["target"]): e for e in edges_list}
added_edges = set(new_edges_map.keys()) - set(old_edges.keys())
removed_edges = set(old_edges.keys()) - set(new_edges_map.keys())
modified_edges = []

for key in sorted(set(new_edges_map.keys()) & set(old_edges.keys())):
    old_e = old_edges[key]
    new_e = new_edges_map[key]
    changes = []
    for k in ["routeName", "stageName", "stationType", "stationTypeName"]:
        if old_e.get(k) != new_e.get(k):
            changes.append(f"{k}: '{old_e.get(k)}' -> '{new_e.get(k)}'")
    if changes:
        modified_edges.append((key, changes))

# 3. Tickets Compare
def get_ticket_key(item):
    ref_type = item.get("refType")
    ref_id = item.get("refId")
    if ref_type == "EDGE":
        return ("EDGE", tuple(ref_id))
    else:
        return ("NODE", ref_id)

new_tickets_map = {get_ticket_key(t): t for t in tickets_list}
added_tickets = set(new_tickets_map.keys()) - set(old_tickets.keys())
removed_tickets = set(old_tickets.keys()) - set(new_tickets_map.keys())
modified_tickets = []

for key in sorted(set(new_tickets_map.keys()) & set(old_tickets.keys())):
    old_t_entry = old_tickets[key]
    new_t_entry = new_tickets_map[key]
    
    old_t_types = {t["ticketType"]: t for t in old_t_entry.get("tickets", [])}
    new_t_types = {t["ticketType"]: t for t in new_t_entry.get("tickets", [])}
    
    t_changes = []
    
    added_tt = set(new_t_types.keys()) - set(old_t_types.keys())
    removed_tt = set(old_t_types.keys()) - set(new_t_types.keys())
    
    if added_tt:
        t_changes.append(f"Thêm loại vé: {[new_t_types[tt]['ticketTypeName'] for tt in added_tt]}")
    if removed_tt:
        t_changes.append(f"Xóa loại vé: {[old_t_types[tt]['ticketTypeName'] for tt in removed_tt]}")
        
    for tt in sorted(set(new_t_types.keys()) & set(old_t_types.keys())):
        old_tt_obj = old_t_types[tt]
        new_tt_obj = new_t_types[tt]
        
        old_p_map = {p["priceType"]: p for p in old_tt_obj.get("prices", [])}
        new_p_map = {p["priceType"]: p for p in new_tt_obj.get("prices", [])}
        
        added_pt = set(new_p_map.keys()) - set(old_p_map.keys())
        removed_pt = set(old_p_map.keys()) - set(new_p_map.keys())
        
        if added_pt:
            t_changes.append(f"[{new_tt_obj['ticketTypeName']}] Thêm phân loại giá: {[new_p_map[pt]['priceTypeName'] for pt in added_pt]}")
        if removed_pt:
            t_changes.append(f"[{old_tt_obj['ticketTypeName']}] Xóa phân loại giá: {[old_p_map[pt]['priceTypeName'] for pt in removed_pt]}")
            
        for pt in sorted(set(new_p_map.keys()) & set(old_p_map.keys())):
            old_p = old_p_map[pt]
            new_p = new_p_map[pt]
            
            p_name = old_p.get("priceTypeName", f"PriceType {pt}")
            tt_name = old_tt_obj["ticketTypeName"]
            
            fee_changes = []
            all_fees = sorted(list(set(old_p.keys()) | set(new_p.keys())))
            for f_key in all_fees:
                if f_key.startswith("feeType"):
                    old_val = old_p.get(f_key)
                    new_val = new_p.get(f_key)
                    if old_val != new_val:
                        if old_val is None:
                            fee_changes.append(f"{f_key} added: {new_val}")
                        elif new_val is None:
                            fee_changes.append(f"{f_key} removed (was {old_val})")
                        else:
                            diff = new_val - old_val
                            sign = "+" if diff > 0 else ""
                            fee_changes.append(f"{f_key}: {old_val} -> {new_val} ({sign}{diff:,} VND)")
            if fee_changes:
                t_changes.append(f"[{tt_name} - {p_name}] Thay đổi cước: {', '.join(fee_changes)}")
                
    if t_changes:
        modified_tickets.append((key, t_changes))

# Write differences to note directory
note_dir = os.path.join(base_dir, "note")
os.makedirs(note_dir, exist_ok=True)

# Clean up redundant legacy log files if they exist
for old_file in ["new_epass.txt", "new_ticket.txt", "removed_epass.txt", "removed_node.txt"]:
    old_file_path = os.path.join(note_dir, old_file)
    if os.path.exists(old_file_path):
        try:
            os.remove(old_file_path)
        except Exception:
            pass

# 1. new_nodes.txt
added_nodes_sorted = sorted(list(added_nodes))
with open(os.path.join(note_dir, "new_nodes.txt"), "w", encoding="utf-8") as f:
    for node in added_nodes_sorted:
        f.write(node + "\n")

# 2. removed_nodes.txt
removed_nodes_sorted = sorted(list(removed_nodes))
with open(os.path.join(note_dir, "removed_nodes.txt"), "w", encoding="utf-8") as f:
    for node in removed_nodes_sorted:
        f.write(node + "\n")

# 3. new_edges.txt
added_edges_sorted = sorted(list(added_edges))
with open(os.path.join(note_dir, "new_edges.txt"), "w", encoding="utf-8") as f:
    for src, tgt in added_edges_sorted:
        f.write(f"{src} -> {tgt}\n")

# 4. removed_edges.txt
removed_edges_sorted = sorted(list(removed_edges))
with open(os.path.join(note_dir, "removed_edges.txt"), "w", encoding="utf-8") as f:
    for src, tgt in removed_edges_sorted:
        f.write(f"{src} -> {tgt}\n")

# 5. new_tickets.txt
added_tickets_sorted = sorted(list(added_tickets), key=lambda x: (x[0], str(x[1])))
with open(os.path.join(note_dir, "new_tickets.txt"), "w", encoding="utf-8") as f:
    for rtype, rid in added_tickets_sorted:
        label = f"{rtype} {list(rid) if rtype == 'EDGE' else rid}"
        f.write(label + "\n")

# 6. removed_tickets.txt
removed_tickets_sorted = sorted(list(removed_tickets), key=lambda x: (x[0], str(x[1])))
with open(os.path.join(note_dir, "removed_tickets.txt"), "w", encoding="utf-8") as f:
    for rtype, rid in removed_tickets_sorted:
        label = f"{rtype} {list(rid) if rtype == 'EDGE' else rid}"
        f.write(label + "\n")

# 7. modified_nodes.txt
with open(os.path.join(note_dir, "modified_nodes.txt"), "w", encoding="utf-8") as f:
    for name, changes in sorted(modified_nodes):
        f.write(f"{name}: {', '.join(changes)}\n")

# 8. modified_edges.txt
with open(os.path.join(note_dir, "modified_edges.txt"), "w", encoding="utf-8") as f:
    for (src, tgt), changes in sorted(modified_edges):
        f.write(f"{src} -> {tgt}: {', '.join(changes)}\n")

# 9. modified_tickets.txt
with open(os.path.join(note_dir, "modified_tickets.txt"), "w", encoding="utf-8") as f:
    for (rtype, rid), changes in sorted(modified_tickets, key=lambda x: (x[0][0], str(x[0][1]))):
        label = f"{rtype} {list(rid) if rtype == 'EDGE' else rid}"
        f.write(f"{label}:\n")
        for change in changes:
            f.write(f"  - {change}\n")

print(f"Recorded differences into note directory: new_nodes, new_edges, new_tickets, removed_nodes, removed_edges, removed_tickets, modified_nodes, modified_edges, modified_tickets")

# 3. Write to both _new.json files and original files (apply changes)
for suffix in ["_new.json", ".json"]:
    with open(os.path.join(base_dir, f"nodes{suffix}"), "w", encoding="utf-8") as f:
        json.dump(nodes_list, f, ensure_ascii=False, indent=4)

    with open(os.path.join(base_dir, f"edges{suffix}"), "w", encoding="utf-8") as f:
        json.dump(edges_list, f, ensure_ascii=False, indent=4)

    with open(os.path.join(base_dir, f"tickets{suffix}"), "w", encoding="utf-8") as f:
        json.dump(tickets_list, f, ensure_ascii=False, indent=4)

print(f"Applied and generated {len(nodes_list)} nodes -> nodes.json & nodes_new.json")
print(f"Applied and generated {len(edges_list)} edges -> edges.json & edges_new.json")
print(f"Applied and generated {len(tickets_list)} tickets -> tickets.json & tickets_new.json")

# 4. Deep Comparison & Diff Report
print("\n" + "="*70)
print("             BÁO CÁO SO SÁNH PHÁT HIỆN THAY ĐỔI")
print("="*70)

print(f"\n1. SO SÁNH NODES (Tổng số mới: {len(nodes_list)} | Cũ: {len(old_nodes)})")
if added_nodes:
    print("  [ADDED] Các trạm mới:")
    for n in sorted(added_nodes):
        print(f"    + {n}")
if removed_nodes:
    print("  [REMOVED] Các trạm bị xóa:")
    for n in sorted(removed_nodes):
        print(f"    - {n}")
if modified_nodes:
    print("  [MODIFIED] Các trạm thay đổi cấu hình:")
    for name, changes in sorted(modified_nodes):
        print(f"    * {name}: {', '.join(changes)}")
if not added_nodes and not removed_nodes and not modified_nodes:
    print("  => Không có thay đổi nào về Nodes.")

print(f"\n2. SO SÁNH EDGES (Tổng số mới: {len(edges_list)} | Cũ: {len(old_edges)})")
if added_edges:
    print("  [ADDED] Các chặng mới:")
    for src, tgt in sorted(added_edges):
        print(f"    + {src} -> {tgt}")
if removed_edges:
    print("  [REMOVED] Các chặng bị xóa:")
    for src, tgt in sorted(removed_edges):
        print(f"    - {src} -> {tgt}")
if modified_edges:
    print("  [MODIFIED] Các chặng thay đổi thuộc tính:")
    for (src, tgt), changes in sorted(modified_edges):
        print(f"    * {src} -> {tgt}: {', '.join(changes)}")
if not added_edges and not removed_edges and not modified_edges:
    print("  => Không có thay đổi nào về Edges.")

print(f"\n3. SO SÁNH VÉ (TICKETS) (Tổng số mới: {len(tickets_list)} | Cũ: {len(old_tickets)})")
if added_tickets:
    print("  [ADDED] Vé mới cho chặng/trạm:")
    for rtype, rid in sorted(added_tickets):
        print(f"    + {rtype} {rid}")
if removed_tickets:
    print("  [REMOVED] Vé bị xóa cho chặng/trạm:")
    for rtype, rid in sorted(removed_tickets):
        print(f"    - {rtype} {rid}")
if modified_tickets:
    print("  [MODIFIED] Thay đổi chi tiết vé:")
    for (rtype, rid), changes in sorted(modified_tickets, key=lambda x: (x[0][0], str(x[0][1]))):
        label = f"{rtype} {list(rid) if rtype == 'EDGE' else rid}"
        print(f"    * {label}:")
        for change in changes:
            print(f"      - {change}")
if not added_tickets and not removed_tickets and not modified_tickets:
    print("  => Không có thay đổi nào về Giá vé/Tickets.")

print("\n" + "="*70)
