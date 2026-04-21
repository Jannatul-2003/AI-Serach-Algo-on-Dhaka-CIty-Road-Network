#!/usr/bin/env python
"""Quick test to verify edge data is not all zeros"""

import sys
sys.path.insert(0, '.')

try:
    from core.route_optimizer import RouteOptimizer

    # Load optimizer
    print('Loading graph and risk database...')
    opt = RouteOptimizer('data/dhaka_road_graph.graphml')

    # Check first 5 edges
    print('\nSample edge attributes:')
    for edge_id, attrs in list(opt.risk_db.risk_data.items())[:5]:
        print(f'  {edge_id}:')
        print(f'    risk_factor={attrs.get("risk_factor", 0):.3f}')
        print(f'    traffic={attrs.get("traffic_factor")}')
        print(f'    construction={attrs.get("construction_work")}')
        print(f'    tolled={attrs.get("tolled_street")}')
        print(f'    street_width={attrs.get("street_width")}')

    # Get some sample costs with different criteria
    print('\n\nTesting cost calculations with different optimization criteria:')

    # Find a valid path
    source_nodes = list(opt.graph.nodes())[:10]
    dest_nodes = list(opt.graph.nodes())[50:60]

    path = None
    for src in source_nodes:
        for dst in dest_nodes:
            try:
                p, _ = opt.search_algorithms.breadth_first_search(opt.graph, src, dst)
                if p and len(p) > 1:
                    path = p
                    break
            except:
                pass
        if path:
            break

    if path:
        print(f'Found path: {path[:5]}... ({len(path)} nodes)')
        
        # Test costs with different criteria
        for criteria in ['fastest', 'safest', 'cheapest']:
            opt.cost_func.set_optimization_criteria(criteria)
            opt.cost_func.custom_weights_applied = False
            
            total_cost = 0
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                keys = list(opt.graph[u][v].keys())
                if keys:
                    edge_id = f'{u}_{v}_{keys[0]}'
                    edge_attrs = opt.risk_db.risk_data.get(edge_id, {})
                    cost = opt.cost_func.calculate_edge_cost(opt.graph, u, v, keys[0], edge_attrs)
                    total_cost += cost
            
            print(f'\n  {criteria.upper()}: total_cost = {total_cost:.4f}')
            print(f'    Weights: {opt.cost_func.weights}')
    else:
        print('Could not find a path')

    print('\n\nRisk data summary:')
    print(f'Total edges with attributes: {len(opt.risk_db.risk_data)}')

    if opt.risk_db.risk_data:
        risk_factors = [attrs.get('risk_factor', 0) for attrs in opt.risk_db.risk_data.values()]
        print(f'Risk factor range: {min(risk_factors):.3f} to {max(risk_factors):.3f}')
        print(f'Average risk factor: {sum(risk_factors) / len(risk_factors):.3f}')
        
        # Check for variation in attributes
        traffic_levels = [attrs.get('traffic_factor') for attrs in opt.risk_db.risk_data.values()]
        construction_count = sum(1 for attrs in opt.risk_db.risk_data.values() if attrs.get('construction_work'))
        toll_count = sum(1 for attrs in opt.risk_db.risk_data.values() if attrs.get('tolled_street'))
        
        print(f'\nAttribute variation:')
        print(f'  Traffic levels: {set(traffic_levels)}')
        print(f'  Edges with construction: {construction_count} / {len(opt.risk_db.risk_data)}')
        print(f'  Tolled edges: {toll_count} / {len(opt.risk_db.risk_data)}')

except Exception as e:
    print(f'ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
