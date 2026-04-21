from typing import Dict, List, Tuple, Any, Optional
import networkx as nx
from .graph_loader import GraphLoader
from .risk_generator import RiskDatabase
from .cost_function import CostFunction
from .heuristics import get_scaled_heuristic_function, AVAILABLE_HEURISTICS
from .search_algorithms import SearchAlgorithms, get_algorithm


class RouteOptimizer:
    """Main orchestrator for route optimization"""

    def __init__(self, graphml_path: str):
        self.graph = GraphLoader.load_graph(graphml_path)
        self.risk_db = RiskDatabase()
        self.cost_func = CostFunction()

        if len(self.risk_db.risk_data) == 0:
            self.risk_db.generate_risk_data_for_graph(self.graph)

        # ── Cache: time-adjusted risk data ───────────────────────────────────
        # Rebuilt only when (day_of_week, hour_of_day) changes.
        self._risk_cache_key: Optional[Tuple[str, int]] = None
        self._risk_cache: Dict[str, Any] = {}

        # ── Cache: global minimum risk across all edges ───────────────────────
        # Used by the admissible heuristic. Recomputed only when risk cache
        # is rebuilt (i.e. when time changes).
        self._min_risk_cache: float = 0.0

        print("Route optimizer initialized")
        print(f"Risk database stats: {self.risk_db.get_statistics()}")

    # ─────────────────────────────────────────────────────────────────────────
    # Public helpers
    # ─────────────────────────────────────────────────────────────────────────

    def get_available_nodes(self) -> List[int]:
        return GraphLoader.get_all_nodes(self.graph)

    def validate_nodes(self, source: int, destination: int) -> Tuple[bool, str]:
        if not GraphLoader.validate_node(self.graph, source):
            return False, f"Source node {source} not found"
        if not GraphLoader.validate_node(self.graph, destination):
            return False, f"Destination node {destination} not found"
        if source == destination:
            return False, "Source and destination must be different"
        return True, "Valid nodes"

    # ─────────────────────────────────────────────────────────────────────────
    # Main entry point
    # ─────────────────────────────────────────────────────────────────────────

    def find_routes(self, source: int, destination: int,
                    algorithms: List[str],
                    vehicle_type: str = 'car',
                    gender: str = 'mixed',
                    age_group: str = 'adult',
                    day_of_week: str = 'Monday',
                    hour_of_day: int = 14,
                    optimization_criteria: str = 'fastest',
                    heuristic_type: str = 'admissible') -> Dict[str, Any]:

        valid, msg = self.validate_nodes(source, destination)
        if not valid:
            return {"error": msg}

        # Update cost weights for the chosen criteria
        self.cost_func.set_optimization_criteria(optimization_criteria)

        self._current_filters = {
            'vehicle_type': vehicle_type,
            'gender': gender,
            'age_group': age_group,
        }

        # Rebuild time-adjusted risk only when time slot changes
        adjusted_risk_data = self._get_adjusted_risk(day_of_week, hour_of_day)

        # Build heuristic bound to current weights and pre-computed min_risk
        heuristic_func = get_scaled_heuristic_function(
            heuristic_type,
            optimization_criteria,
            self.cost_func.weights,
            self._min_risk_cache,   # pass pre-computed min risk
        )

        results = {
            'source': source,
            'destination': destination,
            'algorithms': {},
            'metadata': {
                'vehicle_type': vehicle_type,
                'gender': gender,
                'age_group': age_group,
                'day_of_week': day_of_week,
                'hour_of_day': hour_of_day,
                'optimization_criteria': optimization_criteria,
                'heuristic': AVAILABLE_HEURISTICS['admissible']['name'],
            }
        }

        for algo_name in algorithms:
            path, nodes_expanded = self._run_algorithm(
                algo_name, source, destination, adjusted_risk_data, heuristic_func
            )

            if path:
                total_cost, stats = self.cost_func.calculate_path_cost(
                    self.graph, path, adjusted_risk_data
                )
                results['algorithms'][algo_name] = {
                    'path': path,
                    'cost': total_cost,
                    'nodes_expanded': nodes_expanded,
                    'statistics': stats,
                }
            else:
                results['algorithms'][algo_name] = {
                    'path': None,
                    'error': 'No path found',
                    'nodes_expanded': nodes_expanded,
                }

        return results

    # ─────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _get_adjusted_risk(self, day_of_week: str, hour_of_day: int) -> Dict[str, Any]:
        """
        Return time-adjusted risk data.
        Result is cached by (day_of_week, hour_of_day) so repeated calls with
        the same time slot cost nothing.
        """
        cache_key = (day_of_week, hour_of_day)
        if cache_key == self._risk_cache_key:
            return self._risk_cache   # cache hit — free

        # Cache miss: rebuild and store
        adjusted: Dict[str, Any] = {}
        for edge_id, attrs in self.risk_db.risk_data.items():
            adjusted[edge_id] = self.risk_db.get_time_adjusted_attributes(
                attrs, day_of_week, hour_of_day
            )

        # Pre-compute global minimum risk for the heuristic (O(edges), done once)
        if adjusted:
            self._min_risk_cache = min(
                v.get('risk_factor', 1.0) for v in adjusted.values()
            )
        else:
            self._min_risk_cache = 0.0

        self._risk_cache_key = cache_key
        self._risk_cache = adjusted
        return self._risk_cache

    def _run_algorithm(self, algo_name: str, source: int, destination: int,
                       risk_data: Dict[str, Any],
                       heuristic_func) -> Tuple[Optional[List], int]:

        algo_func = get_algorithm(algo_name)
        if algo_func is None:
            return None, 0

        if algo_name == 'BFS':
            return algo_func(self.graph, source, destination)
        elif algo_name == 'DFS':
            return algo_func(self.graph, source, destination)
        elif algo_name == 'UCS':
            return algo_func(self.graph, source, destination, self.cost_func, risk_data)
        elif algo_name == 'DLS':
            return algo_func(self.graph, source, destination, None, None, depth_limit=20)
        elif algo_name == 'IDLS':
            return algo_func(self.graph, source, destination, None, None, max_depth=50)
        elif algo_name == 'IDS':
            return algo_func(self.graph, source, destination)
        elif algo_name == 'Greedy':
            return algo_func(self.graph, source, destination, heuristic_func, risk_data)
        elif algo_name == 'A*':
            return algo_func(self.graph, source, destination, self.cost_func,
                             heuristic_func, risk_data)
        elif algo_name == 'Weighted A*':
            return algo_func(self.graph, source, destination, self.cost_func,
                             heuristic_func, risk_data, 'afternoon', weight=1.5)
        return None, 0

    # ─────────────────────────────────────────────────────────────────────────
    # Coordinate / ranking helpers
    # ─────────────────────────────────────────────────────────────────────────

    def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
        return GraphLoader.get_node_coordinates(self.graph, node_id)

    def get_path_coordinates(self, path: List[int]) -> List[Tuple[float, float]]:
        return [self.get_node_coordinates(node) for node in path]

    def rank_routes(self, routes: Dict[str, Any]) -> List[Tuple[str, float]]:
        rankings = [
            (name, info['cost'], info['nodes_expanded'])
            for name, info in routes.get('algorithms', {}).items()
            if info.get('path')
        ]
        rankings.sort(key=lambda x: (x[1], x[2]))
        return [(name, cost) for name, cost, _ in rankings]

    # ─────────────────────────────────────────────────────────────────────────
    # Weight management
    # ─────────────────────────────────────────────────────────────────────────

    def update_cost_weights(self, weights: Dict[str, float]):
        self.cost_func.update_weights(weights)

    def reset_custom_weights(self):
        self.cost_func.reset_custom_weights()

    def get_cost_weights(self) -> Dict[str, float]:
        return self.cost_func.weights.copy()

    def get_default_cost_weights(self) -> Dict[str, float]:
        return self.cost_func.default_weights.copy()

    # ─────────────────────────────────────────────────────────────────────────
    # Info
    # ─────────────────────────────────────────────────────────────────────────

    def get_graph_info(self) -> Dict[str, Any]:
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'risk_database_edges': len(self.risk_db.risk_data),
            'risk_stats': self.risk_db.get_statistics(),
        }

    def get_available_heuristics(self) -> Dict[str, Dict[str, str]]:
        return AVAILABLE_HEURISTICS.copy()

    def get_heuristic_info(self) -> Dict[str, str]:
        return AVAILABLE_HEURISTICS['admissible']
