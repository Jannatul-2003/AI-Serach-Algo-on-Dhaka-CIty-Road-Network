#!/usr/bin/env python
"""Test if weights actually change costs for the same path"""

import sys
import warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, '.')

try:
    print('Importing...')
    from core.route_optimizer import RouteOptimizer
    from core.search_algorithms import SearchAlgorithms
    
    print('Loading optimizer...')
    opt = RouteOptimizer('data/dhaka_road_graph.graphml')
    
    # Find a valid path using BFS
    print('Finding a test path...')
    source = list(opt.graph.nodes())[0]
    destination = list(opt.graph.nodes())[100]
    
    try:
        path, _ = SearchAlgorithms.breadth_first_search(opt.graph, source, destination)
    except Exception as e:
        print(f'BFS Error: {e}')
        path = None
    
    if not path or len(path) < 2:
        print(f'ERROR: Could not find a path from {source} to {destination}')
        # Try a shorter distance
        for dest_idx in range(10, 50):
            try:
                destination = list(opt.graph.nodes())[dest_idx]
                path, _ = SearchAlgorithms.breadth_first_search(opt.graph, source, destination)
                if path and len(path) > 2:
                    break
            except:
                pass
    
    if not path or len(path) < 2:
        print('ERROR: Could not find ANY path!')
        exit(1)
    
    print(f'Found path: length={len(path)}, nodes: {path[:5]}...')
    print('\n' + '='*60)
    print('Testing SAME PATH with DIFFERENT optimization criteria:')
    print('='*60)
    
    # Test with each optimization criteria
    criteria_list = ['fastest', 'safest', 'cheapest']
    
    results = {}
    for criteria in criteria_list:
        print(f'\n>>> Optimization Criteria: {criteria.upper()}')
        
        try:
            # Reset and set criteria
            opt.cost_func.custom_weights_applied = False
            opt.cost_func.set_optimization_criteria(criteria)
            
            weights_str = ', '.join([f'{k}:{v:.2f}' for k, v in list(opt.cost_func.weights.items())[:4]])
            print(f'    Weights: {weights_str}...')
            
            # Calculate cost for the entire path
            total_cost = 0
            edge_count = 0
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                try:
                    keys = list(opt.graph[u][v].keys())
                    if keys:
                        edge_id = f'{u}_{v}_{keys[0]}'
                        edge_attrs = opt.risk_db.risk_data.get(edge_id, {})
                        if edge_attrs:
                            cost = opt.cost_func.calculate_edge_cost(opt.graph, u, v, keys[0], edge_attrs)
                            total_cost += cost
                            edge_count += 1
                except Exception as e:
                    print(f'    Edge error {u}->{v}: {e}')
            
            results[criteria] = {
                'total': total_cost,
                'avg': total_cost / edge_count if edge_count > 0 else 0,
                'num_edges': edge_count
            }
            
            print(f'    Total Cost: {total_cost:.6f}')
            print(f'    Avg Cost/Edge: {total_cost / edge_count:.6f}' if edge_count > 0 else '    Avg Cost/Edge: N/A')
            print(f'    Edges calculated: {edge_count}')
        except Exception as e:
            print(f'    ERROR: {type(e).__name__}: {e}')
            import traceback
            traceback.print_exc()
    
    # Compare results
    print('\n' + '='*60)
    print('COMPARISON:')
    print('='*60)
    
    if 'fastest' in results and 'safest' in results and 'cheapest' in results:
        fastest = results['fastest']['total']
        safest = results['safest']['total']
        cheapest = results['cheapest']['total']
        
        print(f'\nFastest:  {fastest:.6f}')
        print(f'Safest:   {safest:.6f}')
        print(f'Cheapest: {cheapest:.6f}')
        
        # Check if they're different
        max_cost = max(fastest, safest, cheapest)
        if max_cost > 0:
            diffs = [
                ('Fastest vs Safest', abs(fastest - safest) / max_cost),
                ('Fastest vs Cheapest', abs(fastest - cheapest) / max_cost),
                ('Safest vs Cheapest', abs(safest - cheapest) / max_cost),
            ]
            
            print('\nPercentage Differences (relative to max):')
            for name, pct in diffs:
                print(f'  {name}: {pct*100:.2f}%')
            
            if all(pct < 0.01 for _, pct in diffs):
                print('\n⚠️ PROBLEM FOUND: Costs are nearly identical!')
                print('   Weights are not affecting cost calculations.')
            else:
                print('\n✅ Good: Costs differ based on optimization criteria')
        else:
            print('\n⚠️ All costs are zero!')

except Exception as e:
    print(f'FATAL ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()

