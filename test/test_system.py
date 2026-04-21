#!/usr/bin/env python3
"""
Test script to verify core functionality
Run this before using the UI to ensure everything works
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_graph_loading():
    """Test loading the road network graph"""
    print("\n" + "="*60)
    print("TEST 1: Loading Road Network Graph")
    print("="*60)
    
    try:
        from core.graph_loader import GraphLoader
        
        graphml_path = 'data/dhaka_road_graph.graphml'
        graph = GraphLoader.load_graph(graphml_path)
        
        print(f"✅ Graph loaded successfully")
        print(f"   - Nodes: {graph.number_of_nodes()}")
        print(f"   - Edges: {graph.number_of_edges()}")
        
        return graph
    except Exception as e:
        print(f"❌ Error loading graph: {e}")
        return None


def test_risk_database(graph):
    """Test risk database generation"""
    print("\n" + "="*60)
    print("TEST 2: Risk Database Generation")
    print("="*60)
    
    try:
        from core.risk_generator import RiskDatabase
        
        risk_db = RiskDatabase()
        
        if len(risk_db.risk_data) == 0:
            print("⏳ Generating risk data for all edges...")
            risk_db.generate_risk_data_for_graph(graph)
        
        stats = risk_db.get_statistics()
        print(f"✅ Risk database ready")
        print(f"   - Total edges: {stats['total_edges']}")
        print(f"   - Avg risk: {stats['avg_risk_factor']:.4f}")
        print(f"   - Min risk: {stats['min_risk_factor']:.4f}")
        print(f"   - Max risk: {stats['max_risk_factor']:.4f}")
        
        return risk_db
    except Exception as e:
        print(f"❌ Error with risk database: {e}")
        return None


def test_cost_function(graph, risk_db):
    """Test cost function calculation"""
    print("\n" + "="*60)
    print("TEST 3: Cost Function")
    print("="*60)
    
    try:
        from core.cost_function import CostFunction
        
        cost_func = CostFunction()
        print(f"✅ Cost function initialized")
        print(f"   - Weights: {list(cost_func.weights.keys())}")
        
        # Get first edge
        edges = list(graph.edges(keys=True, data=True))
        if edges:
            u, v, key, data = edges[0]
            edge_id = f"{u}_{v}_{key}"
            edge_attrs = risk_db.risk_data.get(edge_id, {})
            
            cost = cost_func.calculate_edge_cost(graph, u, v, key, edge_attrs)
            print(f"   - Sample edge cost: {cost:.4f}")
        
        return cost_func
    except Exception as e:
        print(f"❌ Error with cost function: {e}")
        return None


def test_heuristics(graph, risk_db):
    """Test heuristic functions"""
    print("\n" + "="*60)
    print("TEST 4: Heuristic Functions")
    print("="*60)
    
    try:
        from core.heuristics import HeuristicFunctions
        
        nodes = list(graph.nodes())[:2]
        if len(nodes) < 2:
            print("❌ Not enough nodes to test heuristics")
            return False
        
        current, goal = nodes[0], nodes[1]
        
        h_distance = HeuristicFunctions.euclidean_distance_heuristic(graph, current, goal)
        h_manhattan = HeuristicFunctions.manhattan_distance_heuristic(graph, current, goal)
        h_conservative = HeuristicFunctions.conservative_distance_heuristic(graph, current, goal)
        
        print(f"✅ Heuristic functions working")
        print(f"   - Euclidean heuristic: {h_distance:.2f} m")
        print(f"   - Manhattan heuristic: {h_manhattan:.2f} m")
        print(f"   - Conservative heuristic: {h_conservative:.2f} m")
        
        return True
    except Exception as e:
        print(f"❌ Error with heuristics: {e}")
        return False


def test_search_algorithms(graph, risk_db, cost_func):
    """Test search algorithms"""
    print("\n" + "="*60)
    print("TEST 5: Search Algorithms")
    print("="*60)
    
    try:
        from core.search_algorithms import SearchAlgorithms, get_algorithm
        
        # Get two connected nodes
        nodes = list(graph.nodes())
        start_node = nodes[0]
        
        # Find a node that can be reached
        goal_node = None
        for neighbor in graph.successors(start_node):
            goal_node = neighbor
            break
        
        if not goal_node:
            print("⚠️  Could not find connected nodes to test pathfinding")
            return False
        
        print(f"   Testing with start={start_node}, goal={goal_node}")
        
        # Test BFS
        path, expanded = SearchAlgorithms.breadth_first_search(graph, start_node, goal_node)
        if path:
            print(f"   ✅ BFS: Found path with {len(path)} nodes, expanded {expanded} nodes")
        else:
            print(f"   ⚠️  BFS: No path found")
        
        # Test UCS (Uniform Cost Search)
        path, expanded = SearchAlgorithms.uniform_cost_search(graph, start_node, goal_node, 
                                                              cost_func, risk_db.risk_data)
        if path:
            print(f"   ✅ UCS: Found path with {len(path)} nodes, expanded {expanded} nodes")
        else:
            print(f"   ⚠️  UCS: No path found")
        
        return True
    except Exception as e:
        print(f"❌ Error with search algorithms: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_route_optimizer():
    """Test route optimizer integration"""
    print("\n" + "="*60)
    print("TEST 6: Route Optimizer Integration")
    print("="*60)
    
    try:
        from core.route_optimizer import RouteOptimizer
        
        graphml_path = 'data/dhaka_road_graph.graphml'
        optimizer = RouteOptimizer(graphml_path)
        
        print(f"✅ Route optimizer initialized")
        
        info = optimizer.get_graph_info()
        print(f"   - Network nodes: {info['total_nodes']}")
        print(f"   - Network edges: {info['total_edges']}")
        print(f"   - Risk database edges: {info['risk_database_edges']}")
        
        return optimizer
    except Exception as e:
        print(f"❌ Error with route optimizer: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests"""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  🧪 DHAKA ROUTE OPTIMIZER - FUNCTIONAL TESTS".ljust(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run tests
    graph = test_graph_loading()
    if not graph:
        return 1
    
    risk_db = test_risk_database(graph)
    if not risk_db:
        return 1
    
    cost_func = test_cost_function(graph, risk_db)
    if not cost_func:
        return 1
    
    if not test_heuristics(graph, risk_db):
        return 1
    
    if not test_search_algorithms(graph, risk_db, cost_func):
        return 1
    
    optimizer = test_route_optimizer()
    if not optimizer:
        return 1
    
    # Success
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n✨ System is ready to use!")
    print("\n🚀 To start the web application, run:")
    print("   python main.py")
    print("   OR")
    print("   streamlit run ui/streamlit_app.py")
    print("\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
