import os
import json

base_dir = os.path.dirname(os.path.abspath(__file__))
jsonl_files = ["ve_luot.jsonl", "ve_thang.jsonl", "ve_quy.jsonl"]

nodes_dict = {}
edges_dict = {}
tickets_dict = {} # key -> { ticketType: { ... prices: { priceType: {...} } } }

def get_node(name):
    if name not in nodes_dict:
        nodes_dict[name] = {
            "stationName": name,
            "stationType": 0,
            "stationTypeName": "CLOSED",
            "latitude": None,
            "longitude": None,
            "stationOsmId": None,
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
    
    # If ticketType is not present (should be rare), skip or set a default
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

for file_name in jsonl_files:
    file_path = os.path.join(base_dir, file_name)
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line: continue
            record = json.loads(line)
            
            s_type = record.get("stationType")
            
            if s_type == 1:
                # OPEN
                name = record.get("stationName").strip()
                if not name: continue
                node = get_node(name)
                # Upgrade to OPEN
                node["stationType"] = 1
                node["stationTypeName"] = "OPEN"
                
                # Ticket
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
                
                # Edge key -> [stationInName, stationOutName]
                edge_key = f"{in_name}||{out_name}"
                if edge_key not in edges_dict:
                    # We might want to keep multiple routes if they exist, but normally [In, Out] is unique enough
                    edges_dict[edge_key] = {
                        "source": in_name,
                        "target": out_name,
                        "routeName": route,
                        "stageName": stage,
                        "stationType": 0,
                        "stationTypeName": "CLOSED"
                    }
                
                # Ticket
                ref_id_val = [in_name, out_name]
                process_ticket("EDGE", edge_key, ref_id_val, record)

# Convert sets to lists and flatten tickets
nodes_list = []
for node in nodes_dict.values():
    node["incoming_edges"] = list(node["incoming_edges"])
    node["outgoing_edges"] = list(node["outgoing_edges"])
    nodes_list.append(node)

edges_list = list(edges_dict.values())

tickets_list = []
for v in tickets_dict.values():
    # Flatten tickets_map
    t_arr = []
    for t_val in v["tickets_map"].values():
        t_val["prices"] = list(t_val["prices_map"].values())
        del t_val["prices_map"]
        t_arr.append(t_val)
    
    tickets_list.append({
        "refType": v["refType"],
        "refId": v["refId"],
        "tickets": t_arr
    })

# Write to files
with open(os.path.join(base_dir, "nodes.json"), "w", encoding="utf-8") as f:
    json.dump(nodes_list, f, ensure_ascii=False, indent=4)

with open(os.path.join(base_dir, "edges.json"), "w", encoding="utf-8") as f:
    json.dump(edges_list, f, ensure_ascii=False, indent=4)

with open(os.path.join(base_dir, "tickets.json"), "w", encoding="utf-8") as f:
    json.dump(tickets_list, f, ensure_ascii=False, indent=4)

print(f"Generated {len(nodes_list)} nodes -> nodes.json")
print(f"Generated {len(edges_list)} edges -> edges.json")
print(f"Generated {len(tickets_list)} tickets -> tickets.json")
