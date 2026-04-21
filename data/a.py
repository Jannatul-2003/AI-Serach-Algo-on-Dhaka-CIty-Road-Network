import networkx as nx
import ast
import unicodedata

def add_junction_names(graph):
    for node, data in graph.nodes(data=True):
        streets = set()
        all_edges = list(graph.out_edges(node, data=True)) + list(graph.in_edges(node, data=True))
        
        for u, v, edge_data in all_edges:
            if 'name' in edge_data:
                name_val = edge_data['name']
                
                # 1. Handle strings that look like lists e.g. "['Road A']"
                if isinstance(name_val, str) and name_val.startswith('['):
                    try:
                        name_val = ast.literal_eval(name_val)
                    except:
                        pass
                
                # 2. Convert to a list if it's a single string for uniform processing
                names_to_process = name_val if isinstance(name_val, list) else [name_val]
                
                for n in names_to_process:
                    # 3. Clean string and normalize Unicode (fixes the Bengali duplicate issue)
                    clean_name = unicodedata.normalize('NFC', str(n)).strip("[]'\" ")
                    if clean_name:
                        streets.add(clean_name)
        
        if streets:
            # 4. Join unique names
            data['junction_name'] = " & ".join(sorted(list(streets)))
        else:
            data['junction_name'] = f"Node_{node}"

# Load, Run, and Save
G = nx.read_graphml('dhaka_road_graph.graphml')
add_junction_names(G)
nx.write_graphml(G, 'dhaka_city_graph_with_names.graphml')
print("Done! Brackets and duplicate Bengali names fixed.")
