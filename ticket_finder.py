import json
import os
import sys

# Force console to output UTF-8
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

EDGES_PATH = r"edges.json"
TICKETS_PATH = r"tickets.json"

NODES_PATH = r"nodes.json"

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_routes_by_station(station_name, edges_data=None):
    """
    Hàm 1: Nhập tên trạm, tìm các routeName chứa trạm này (làm source hoặc target)
    """
    if edges_data is None:
        edges_data = load_json(EDGES_PATH)
    
    routes = set()
    for edge in edges_data:
        if edge.get('source') == station_name or edge.get('target') == station_name:
            if 'routeName' in edge:
                routes.add(edge['routeName'].strip())
    
    return list(routes)

def get_tickets_by_station(station_name):
    """
    Hàm 2: Nhập tên trạm, tìm các routeName từ hàm 1,
    sau đó với mỗi routeName, liệt kê các json ticket thuộc về route đó.
    """
    edges_data = load_json(EDGES_PATH)
    tickets_data = load_json(TICKETS_PATH)
    
    route_names = get_routes_by_station(station_name, edges_data)
    
    # Tạo map từ routeName -> danh sách các cặp (source, target) thuộc route đó
    route_to_edges = {}
    for edge in edges_data:
        r_name = edge.get('routeName', '').strip()
        if r_name in route_names:
            if r_name not in route_to_edges:
                route_to_edges[r_name] = []
            route_to_edges[r_name].append((edge.get('source'), edge.get('target')))
            
    # Tạo map từ (source, target) -> ticket json để tra cứu nhanh
    edge_to_ticket = {}
    for ticket in tickets_data:
        if ticket.get('refType') == 'EDGE' and 'refId' in ticket:
            ref_id = ticket['refId']
            if len(ref_id) == 2:
                edge_to_ticket[(ref_id[0], ref_id[1])] = ticket
                
    result = {}
    for r_name in route_names:
        result[r_name] = []
        edges_in_route = route_to_edges.get(r_name, [])
        for src, tgt in edges_in_route:
            ticket = edge_to_ticket.get((src, tgt))
            if ticket:
                result[r_name].append(ticket)
                
    return result

def get_nodes_for_route(route_name, edges_data=None, nodes_data=None):
    """
    Hàm 3: Nhập tên tuyến đường, trả về danh sách các nodes thuộc tuyến đường đó,
    sắp xếp từ Bắc xuống Nam (Latitude giảm dần), từ Tây sang Đông (Longitude tăng dần).
    """
    if edges_data is None:
        edges_data = load_json(EDGES_PATH)
    if nodes_data is None:
        nodes_data = load_json(NODES_PATH)
        
    node_names_in_route = set()
    for edge in edges_data:
        if edge.get('routeName') == route_name:
            node_names_in_route.add(edge.get('source'))
            node_names_in_route.add(edge.get('target'))
            
    # filter nodes
    route_nodes = []
    for n in nodes_data:
        if n.get('stationName') in node_names_in_route:
            route_nodes.append(n)
            
    # Sắp xếp Bắc->Nam (lat giảm dần), Tây->Đông (lon tăng dần)
    # Dấu '-' trước vĩ độ để xếp giảm dần (số to lên trước).
    route_nodes.sort(key=lambda n: (
        -(n.get('latitude') if n.get('latitude') is not None else 0),
        (n.get('longitude') if n.get('longitude') is not None else 0)
    ))
    
    return route_nodes

if __name__ == "__main__":
    # Ví dụ cách gọi
    station_to_search = "Nút giao Nghi Phương"

    print(f"--- Các routeName chứa trạm '{station_to_search}' ---")
    routes = get_routes_by_station(station_to_search)
    for r in routes:
        print("-", r)
        
    print(f"\n--- Các tickets và nodes theo từng routeName của trạm '{station_to_search}' ---")
    tickets_by_route = get_tickets_by_station(station_to_search)
    edges_db = load_json(EDGES_PATH)
    nodes_db = load_json(NODES_PATH)
    
    for route, tickets in tickets_by_route.items():
        print(f"\n======================================")
        print(f"ROUTE: {route}")
        print(f"======================================")
        
        # 1. Liệt kê nodes
        nodes = get_nodes_for_route(route, edges_db, nodes_db)
        print(f"\n>> DANH SÁCH {len(nodes)} TRẠM (Sắp xếp Bắc -> Nam, Tây -> Đông):")
        for idx, node in enumerate(nodes, 1):
            name = node.get('stationName')
            lat = node.get('latitude')
            lon = node.get('longitude')
            print(f"  {idx:02d}. {name:<40} (Lat: {lat}, Lon: {lon})")
            
        # 2. Liệt kê tickets
        print(f"\n>> DANH SÁCH {len(tickets)} TICKETS TRÊN TUYẾN:")
        for ticket in tickets:
            ref_id = ticket.get('refId', [])
            if len(ref_id) == 2:
                print(f"  - Từ {ref_id[0]} -> {ref_id[1]}")

